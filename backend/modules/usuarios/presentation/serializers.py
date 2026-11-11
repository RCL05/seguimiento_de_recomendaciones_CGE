from rest_framework import serializers

from backend.modules.usuarios.models import UnidadOrganica, Usuario


class LoginSsoRequestSerializer(serializers.Serializer):
    credential = serializers.CharField(
        trim_whitespace=True,
        help_text="Credencial temporal emitida por el SSO institucional.",
    )


class SesionSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.ChoiceField(choices=["Bearer"])
    expires_in = serializers.IntegerField(help_text="Segundos de validez del JWT.")
    user_id = serializers.UUIDField()
    email = serializers.EmailField()
    display_name = serializers.CharField()
    role = serializers.ChoiceField(choices=Usuario.Rol.choices)
    unit_id = serializers.CharField(allow_null=True)


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadOrganica
        fields = ["id", "codigo", "nombre"]


class UnidadCreateSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=200)


class UsuarioSerializer(serializers.ModelSerializer):
    unidad_codigo = serializers.CharField(source="unidad_org.codigo", allow_null=True, default=None)

    class Meta:
        model = Usuario
        fields = ["id", "correo_institucional", "nombres", "rol", "unidad_codigo", "activo"]


class UsuarioUpdateSerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=Usuario.Rol.choices, required=False)
    unidad_codigo = serializers.CharField(max_length=50, required=False)

    def validate_unidad_codigo(self, value):
        unidad = UnidadOrganica.objects.filter(codigo=value).first()
        if unidad is None:
            raise serializers.ValidationError("La unidad indicada no existe.")
        return unidad

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Indique rol y/o unidad_codigo.")
        return attrs
