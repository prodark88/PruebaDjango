from rest_framework import serializers
from api.model.InteractionModel import Interaction
from api.model.CustomersModel import Customer
from api.serializers.CustomersSerializer import CustomerSerializer
from django.contrib.auth.hashers import make_password


# 4. Interaction Serializer
class InteractionSerializer(serializers.ModelSerializer):
    cliente = CustomerSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source='cliente', write_only=True
    )

    class Meta:
        model = Interaction
        fields = ['id', 'cliente', 'cliente_id', 'tipo', 'fecha']