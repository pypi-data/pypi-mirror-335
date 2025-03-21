import uniserde
import test.models as models
import uniserde.lazy_wrapper as lazy_wrapper
import uniserde.json_deserialize
import uniserde.bson_deserialize

value_fresh = models.TestClass.create_variant_1()
value_serialized = uniserde.as_json(value_fresh)

value_lazy: models.TestClass = lazy_wrapper.create_lazy_instance(
    value_serialized,
    uniserde.json_deserialize.JsonDeserializationCache(
        custom_handlers={},
        lazy=False,
    ),
    models.TestClass,
)

print(value_lazy.val_str)
print(value_lazy.val_datetime)
print(value_lazy.val_doesnt_exist)
