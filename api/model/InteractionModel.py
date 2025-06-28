from django.db import models


from api.model.CustomersModel import Customer

class Interaction(models.Model):
    cliente = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interacciones')
    tipo = models.CharField(max_length=50)  # Call, Email, SMS, etc.
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} con {self.cliente.nombre}"