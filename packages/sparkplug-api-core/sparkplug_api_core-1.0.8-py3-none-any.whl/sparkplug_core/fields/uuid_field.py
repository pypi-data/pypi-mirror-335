from rest_framework import serializers


class UUIDField(serializers.SlugRelatedField):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("slug_field", "uuid")
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the field is used with `many=True`, fetch all related UUIDs
        if self.many:
            return value.values_list("uuid", flat=True)
        # Otherwise, return the single UUID
        return super().to_representation(value)
