from django.db import models


from api.model.CompaniesModel import Company
from api.model.UserModel import User

class Customer(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre completo
    fecha_nacimiento = models.DateField()
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clientes')
    representante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clientes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
