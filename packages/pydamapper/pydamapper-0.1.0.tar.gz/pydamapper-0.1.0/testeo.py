from typing import Dict, Type, Union, List, Tuple, Optional, get_origin, get_args
from pydantic import BaseModel, Field


class AliasMappingError(Exception):
    """Base exception for alias mapping errors"""

    pass


class ModelStructureError(AliasMappingError):
    """Raised when invalid model structure is detected"""

    pass


def _get_all_model_aliases(model: Type[BaseModel]) -> Dict[str, str]:
    """
    Generates mapping of original field names to their aliases for a Pydantic model class.
    Handles nested models and lists of models. Works with model structure only (not instances).

    Args:
        model: Pydantic model class to analyze

    Returns:
        Dictionary with original field names as keys and their aliases as values

    Raises:
        ModelStructureError: If invalid model structure is detected
    """
    aliases = {}
    visited = set()  # Prevent infinite recursion on circular references

    def process_model(current_model: Type[BaseModel], parent_path: str = "") -> None:
        nonlocal aliases, visited

        if current_model in visited:
            return

        if not issubclass(current_model, BaseModel):
            raise ModelStructureError(f"Invalid model type: {type(current_model)}")

        try:
            visited.add(current_model)

            for field_name, field_info in current_model.model_fields.items():
                full_path = f"{parent_path}.{field_name}" if parent_path else field_name

                # Store alias if present
                if field_info.alias:
                    aliases[field_name] = field_info.alias

                # Recursively process nested structures
                field_type = field_info.annotation
                origin = get_origin(field_type) or field_type
                args = get_args(field_type)

                # Handle Union/Optional, check this in depth
                if origin is Union:
                    for arg in args:
                        if isinstance(arg, type) and issubclass(arg, BaseModel):
                            process_model(arg, full_path)

                # Handle List/Tuples
                elif origin in (list, tuple):
                    inner_type = args[0] if args else None
                    if isinstance(inner_type, type) and issubclass(
                        inner_type, BaseModel
                    ):
                        process_model(inner_type, full_path)

                # Handle direct nested models
                elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    process_model(field_type, full_path)

        except Exception as e:
            raise ModelStructureError(
                f"Error processing model {current_model.__name__}: {str(e)}"
            ) from e

    try:
        process_model(model)
        return aliases
    except RecursionError as e:
        raise ModelStructureError(
            "Circular reference detected in model structure"
        ) from e


# For model structure
class NestedModel(BaseModel):
    value: str = Field(alias="val")


class MainModel(BaseModel):
    items: List[NestedModel] = Field(alias="elements")
    name: str = Field(alias="title")


print(_get_all_model_aliases(MainModel))
# Output: {'items': 'elements', 'name': 'title'}

# For model instance
# instance = MainModel(elements=[NestedModel(val="test")], title="example")
# print(_get_source_aliases(instance))
# Output: {'elements': 'items', 'title': 'name', 'val': 'items[0].value'}

print("#############################")


# Model 1: Simple nested model with alias
class Child(BaseModel):
    child_field: str = Field(alias="cf")
    deep_nested: Optional["Child"] = None


# Model 2: Parent with list of nested models and aliases
class Parent(BaseModel):
    children: List[Child] = Field(alias="ch")
    name: str  # No alias
    optional_list: Optional[List[Child]] = None


# Model 3: Grandparent with Union and Tuple
class AnotherModel(BaseModel):
    data: str = Field(alias="dt")


class Grandparent(BaseModel):
    parent: Union[Parent, AnotherModel] = Field(alias="gp")
    tuple_field: Tuple[Child, AnotherModel] = Field(alias="tf")


# Circular reference model
Child.model_rebuild()  # Fix forward reference

# Instance 1: Parent with nested children
parent_instance = Parent(
    ch=[Child(cf="child1", deep_nested=Child(cf="deep_child"))],
    name="test",
    opt=None,  # Optional list set to None
)

# Instance 2: Grandparent with Union and Tuple
grandparent_instance = Grandparent(
    gp=Parent(ch=[Child(cf="child2")], name="nested"),
    tf=(Child(cf="tuple_child"), AnotherModel(dt="tuple_data")),
)

# Instance 3: Circular reference
circular_child = Child(cf="circular")
circular_child.deep_nested = circular_child  # Points to itself


print(f"Child :{_get_all_model_aliases(Child)}")
print(f"Parent :{_get_all_model_aliases(Parent)}")
print(f"Grandparent :{_get_all_model_aliases(Grandparent)}")

print("#############################")

# print(f"Instancia Parent :{_get_source_aliases(parent_instance)}")
# print(f"Instancia Grandparent :{_get_source_aliases(grandparent_instance)}")
# print(f"Instancia circular :{_get_source_aliases(circular_child)}")
