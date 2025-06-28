from rest_framework import serializers

from api.model.CustomersModel import Customer
from api.model.CompaniesModel import Company
from api.model.UserModel import User

from api.serializers.UserSerializer import UserSerializer
from api.serializers.CompaniesSerializer import CompanySerializer


# 3. Customer Serializer
class CustomerSerializer(serializers.ModelSerializer):
    empresa = CompanySerializer(read_only=True)
    empresa_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), source='empresa', write_only=True
    )
    representante = UserSerializer(read_only=True)
    representante_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='representante', write_only=True
    )

    class Meta:
        model = Customer
        fields = [
            'id', 'nombre', 'fecha_nacimiento',
            'empresa', 'empresa_id',
            'representante', 'representante_id',
            'created_at', 'updated_at'
        ]
