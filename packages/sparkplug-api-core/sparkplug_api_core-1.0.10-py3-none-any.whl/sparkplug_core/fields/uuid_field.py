from rest_framework import serializers


class UUIDField(serializers.SlugRelatedField):
    def __init__(self, many=False, **kwargs) -> None:
        kwargs.setdefault("slug_field", "uuid")
        self.many = many
        super().__init__(**kwargs)

    def to_representation(self, value):
        # If the field is used with `many=True`, handle the iterable properly
        if self.many and hasattr(value, "all"):
            return list(value.all().values_list("uuid", flat=True))
        elif self.many:
            return [getattr(item, self.slug_field) for item in value]
        # Otherwise, return the single UUID
        return super().to_representation(value)
