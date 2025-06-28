from rest_framework import serializers

from api.model.CompaniesModel import Company


# 2. Company Serializer
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'nombre', 'created_at', 'updated_at']