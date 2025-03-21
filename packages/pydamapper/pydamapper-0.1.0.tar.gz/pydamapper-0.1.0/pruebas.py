from pydamapper.pydamapper import PyDaMapper
from tests.models import *
from tests.sources import *
from tests.expected import *
from pydantic import BaseModel


mapper = PyDaMapper()
date_returned = mapper.map_models(source_data, TargetModelOrder)
# print(json.dumps(expected_target.model_dump(), indent=4, default=custom_serializer))
print("#####################")
# print(json.dumps(date_returned, indent=4, default=custom_serializer))
print(date_returned == expected_target)

print("#####################")

test_data = mapper.map_models(address, MissingFieldAddress)
# print(test_data)

print("#####################")

test_data = mapper.map_models(address, TypeErrorAddress)
# print(test_data)
