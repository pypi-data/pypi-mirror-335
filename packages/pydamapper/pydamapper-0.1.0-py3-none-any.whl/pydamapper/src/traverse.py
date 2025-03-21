from typing import Type, List, Optional, Iterable, Any, TypeVar, Generic, Protocol
from pydantic import BaseModel

from .path_manager import path_manager
from .error_manager import error_manager
from .field_cache import matched_fields_cache
from .meta_field import FieldMetaData

T = TypeVar("T")


class ModelVisitor(Protocol, Generic[T]):
    """Protocol defining the visitor interface for model traversal."""

    def visit_field(self, model: BaseModel, field_name: str, value: Any, path: str) -> Optional[T]:
        """Visit a field within a model."""
        pass

    def visit_model(self, model: BaseModel, path: str) -> Optional[T]:
        """Visit a single model instance."""
        pass

    def visit_collection_item(self, item: Any, index: int, path: str) -> Optional[T]:
        """Visit an item within a collection."""
        pass

    def should_continue(self, result: Optional[T]) -> bool:
        """Determine if traversal should continue after finding a result."""
        pass


class ModelTraverser:
    """Centralized traversal logic for Pydantic models."""

    def __init__(self):
        self._path_manager = path_manager

    def traverse(self, model: BaseModel, visitor: ModelVisitor[T]) -> Optional[T]:
        """Traverse a model structure with the given visitor."""
        return self._traverse_model(model, "", visitor)

    def _traverse_model(
        self, model: BaseModel, path_segment: str, visitor: ModelVisitor[T]
    ) -> Optional[T]:
        """Traverse a single model instance."""
        if not isinstance(model, BaseModel):
            return None

        with self._path_manager.track_segment("source", path_segment):
            # Visit the model itself
            result = visitor.visit_model(model, self._path_manager.get_path("source"))
            if result is not None and not visitor.should_continue(result):
                return result

            # Visit each field in the model
            for field_name, field_info in model.model_fields.items():
                field_value = getattr(model, field_name)

                with self._path_manager.track_segment("source", field_name):
                    # Visit the field
                    result = visitor.visit_field(
                        model, field_name, field_value, self._path_manager.get_path("source")
                    )
                    if result is not None and not visitor.should_continue(result):
                        return result

                    # Recurse into nested models
                    if isinstance(field_value, BaseModel):
                        result = self._traverse_model(field_value, "", visitor)
                        if result is not None and not visitor.should_continue(result):
                            return result

                    # Recurse into collections
                    elif isinstance(field_value, (list, tuple)) and field_value:
                        result = self._traverse_collection(field_value, visitor)
                        if result is not None and not visitor.should_continue(result):
                            return result

            return None

    def _traverse_collection(
        self, collection: Iterable[Any], visitor: ModelVisitor[T]
    ) -> Optional[T]:
        """Traverse a collection of items."""
        for index, item in enumerate(collection):
            with self._path_manager.track_segment("source", f"[{index}]"):
                # Visit the collection item
                result = visitor.visit_collection_item(
                    item, index, self._path_manager.get_path("source")
                )
                if result is not None and not visitor.should_continue(result):
                    return result

                # Recurse into model items
                if isinstance(item, BaseModel):
                    result = self._traverse_model(item, "", visitor)
                    if result is not None and not visitor.should_continue(result):
                        return result

                # Recurse into nested collections
                elif isinstance(item, (list, tuple)) and item:
                    result = self._traverse_collection(item, visitor)
                    if result is not None and not visitor.should_continue(result):
                        return result

        return None


class FieldValueVisitor(ModelVisitor[Any]):
    """Visitor that finds a specific field value."""

    def __init__(
        self,
        target_field: str,
        field_meta_data: FieldMetaData,
    ):
        self.target_field = target_field
        self.field_meta_data = field_meta_data
        self._error_manager = error_manager
        self._cache = matched_fields_cache

    def visit_model(self, model: BaseModel, path: str) -> Optional[Any]:
        """Try to find the target field directly in this model."""
        if not hasattr(model, self.target_field):
            return None

        value = getattr(model, self.target_field)
        if value is None:
            return None

        if self._cache.is_cached(path):
            return None

        # Validate and cache the found value
        target_path = path.replace("source", "target")
        self._error_manager.validate_type(
            target_path, self.field_meta_data.field_type_safe, value, type(value)
        )
        self._cache.add(path)
        return value

    def visit_field(
        self, model: BaseModel, field_name: str, value: Any, path: str
    ) -> Optional[Any]:
        """No additional field checking needed, handled by model traversal."""
        return None

    def visit_collection_item(self, item: Any, index: int, path: str) -> Optional[Any]:
        """No special handling for collection items."""
        return None

    def should_continue(self, result: Any) -> bool:
        """Stop traversal after finding the first match."""
        return False


class ModelInstanceCollector(ModelVisitor[List[BaseModel]]):
    """Visitor that collects all instances of a specific model type."""

    def __init__(self, model_type: Type[BaseModel]):
        self.model_type = model_type
        self.instances: List[BaseModel] = []

    def visit_model(self, model: BaseModel, path: str) -> Optional[List[BaseModel]]:
        """Collect if model matches the target type."""
        if isinstance(model, self.model_type):
            self.instances.append(model)
        return self.instances

    def visit_field(
        self, model: BaseModel, field_name: str, value: Any, path: str
    ) -> Optional[List[BaseModel]]:
        """No additional field checking needed."""
        return None

    def visit_collection_item(self, item: Any, index: int, path: str) -> Optional[List[BaseModel]]:
        """No special handling for collection items."""
        return None

    def should_continue(self, result: List[BaseModel]) -> bool:
        """Always continue traversal to find all matches."""
        return True
