from drf_spectacular.extensions import OpenApiSerializerFieldExtension


class ChoiceFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'saas_base.drf.serializers.ChoiceField'

    def map_serializer_field(self, auto_schema, direction):
        choices = list(self.target.choices.values())
        return {'type': 'string', 'enum': choices}
