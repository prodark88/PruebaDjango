from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import OuterRef, Subquery
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Max
from django.utils.timesince import timesince
from django.contrib.auth.models import User
import random
from faker import Faker

# Tus imports existentes
from api.model.CustomersModel import Customer
from api.model.InteractionModel import Interaction
from api.serializers.CustomersSerializer import CustomerSerializer
# Asumiendo que tienes estos modelos
from api.model.CompaniesModel import Company  # Ajusta según tu estructura
from api.model.UserModel import User as SalesRep  # Ajusta según tu estructura

fake = Faker('es_ES')  # Para generar datos en español

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'empresa__nombre', 'fecha_nacimiento']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Anotar la última interacción
        latest_interaction = Interaction.objects.filter(
            cliente=OuterRef('pk')
        ).order_by('-fecha')

        queryset = queryset.annotate(
            ultima_interaccion_fecha=Subquery(latest_interaction.values('fecha')[:1]),
            ultima_interaccion_tipo=Subquery(latest_interaction.values('tipo')[:1]),
        )

        # Filtro adicional: cumpleaños esta semana
        birthday_this_week = self.request.query_params.get('birthday_this_week')
        if birthday_this_week == 'true':
            today = now().date()
            end_week = today + timedelta(days=7)
            queryset = queryset.annotate(
                birth_month=ExtractMonth('fecha_nacimiento'),
                birth_day=ExtractDay('fecha_nacimiento')
            ).filter(
                birth_month=today.month,
                birth_day__gte=today.day,
                birth_day__lte=end_week.day
            )

        # Ordenar por última interacción
        ordering = self.request.query_params.get('ordering')
        if ordering == 'ultima_interaccion':
            queryset = queryset.order_by('-ultima_interaccion_fecha')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Serializar manualmente para incluir datos personalizados
        data = []
        for cliente in queryset:
            # Dividir el nombre para obtener firstName y lastName
            nombre_partes = cliente.nombre.split(' ', 1)
            first_name = nombre_partes[0] if nombre_partes else ''
            last_name = nombre_partes[1] if len(nombre_partes) > 1 else ''
            
            data.append({
                'id': cliente.id,
                'firstName': first_name,
                'lastName': last_name,
                'fullName': cliente.nombre,
                'company': cliente.empresa.nombre,
                'birthday': cliente.fecha_nacimiento,
                'lastInteraction': {
                    'date': cliente.ultima_interaccion_fecha,
                    'type': cliente.ultima_interaccion_tipo
                } if cliente.ultima_interaccion_fecha else None
            })
        return Response(data)

    @action(detail=False, methods=['post'])
    def load_fake_data(self, request):
        """
        Endpoint para cargar datos ficticios
        """
        try:
            # 1. Crear representantes de ventas (3 usuarios)
            sales_reps = []
            for i in range(3):
                sales_rep, created = SalesRep.objects.get_or_create(
                    email=f'rep{i+1}@empresa.com',
                    defaults={
                        'nombre': fake.name(),
                        'password': 'password123',  # En producción, usar hash
                        'is_staff': False
                    }
                )
                sales_reps.append(sales_rep)

            # 2. Crear compañías (entre 50-100 compañías)
            companies = []
            company_names = [
                'TechCorp S.A.', 'Innovate Ltd.', 'Global Solutions', 'StartupXYZ', 
                'Enterprise Co.', 'Digital Works', 'Future Systems', 'Smart Business',
                'Advanced Tech', 'Creative Solutions', 'Data Dynamics', 'Cloud Computing',
                'AI Innovations', 'Cyber Security', 'Mobile Apps', 'Web Development',
                'E-commerce Plus', 'Marketing Pro', 'Sales Force', 'Customer Success'
            ]
            
            for i in range(50):
                company_name = f"{random.choice(company_names)} {i+1}"
                company, created = Company.objects.get_or_create(
                    nombre=company_name,
                    defaults={
                        'created_at': fake.date_between(start_date='-5y', end_date='today')
                    }
                )
                companies.append(company)

            # 3. Crear 1000 clientes
            customers = []
            for i in range(1000):
                customer = Customer.objects.create(
                    nombre=fake.name(),
                    fecha_nacimiento=fake.date_between(start_date='-60y', end_date='-18y'),
                    empresa=random.choice(companies),
                    representante=random.choice(sales_reps),  # Ajusta según tu modelo
                    created_at=fake.date_between(start_date='-2y', end_date='today')
                )
                customers.append(customer)

            # 4. Crear interacciones (500 por cliente = 500,000 total)
            interaction_types = ['Call', 'Email', 'SMS', 'Facebook', 'WhatsApp', 'Meeting', 'LinkedIn']
            
            # Procesar en lotes para evitar problemas de memoria
            batch_size = 1000
            total_interactions = 0
            
            for customer in customers:
                interactions_batch = []
                for j in range(500):  # 500 interacciones por cliente
                    interaction = Interaction(
                        cliente=customer,
                        tipo=random.choice(interaction_types),
                        fecha=fake.date_time_between(start_date='-1y', end_date='now'),
                        # Agregar otros campos según tu modelo
                    )
                    interactions_batch.append(interaction)
                    
                    # Crear en lotes
                    if len(interactions_batch) >= batch_size:
                        Interaction.objects.bulk_create(interactions_batch)
                        total_interactions += len(interactions_batch)
                        interactions_batch = []
                
                # Crear el lote restante
                if interactions_batch:
                    Interaction.objects.bulk_create(interactions_batch)
                    total_interactions += len(interactions_batch)

            # Estadísticas finales
            stats = {
                'users': SalesRep.objects.count(),
                'companies': Company.objects.count(),
                'customers': Customer.objects.count(),
                'interactions': Interaction.objects.count()
            }

            return Response({
                'success': True,
                'message': 'Datos ficticios cargados exitosamente',
                'statistics': stats
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error al cargar datos ficticios:", e)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def reset_database(self, request):
        """
        Endpoint para limpiar la base de datos
        """
        try:
            # Eliminar en orden para evitar problemas de claves foráneas
            deleted_stats = {}
            
            deleted_stats['interactions'] = Interaction.objects.count()
            Interaction.objects.all().delete()
            
            deleted_stats['customers'] = Customer.objects.count()
            Customer.objects.all().delete()
            
            deleted_stats['companies'] = Company.objects.count()
            Company.objects.all().delete()
            
            deleted_stats['users'] = SalesRep.objects.count()
            SalesRep.objects.all().delete()

            return Response({
                'success': True,
                'message': 'Base de datos limpiada exitosamente',
                'deleted': deleted_stats
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Endpoint para obtener estadísticas de la base de datos
        """
        try:
            stats = {
                'users': SalesRep.objects.count(),
                'companies': Company.objects.count(),
                'customers': Customer.objects.count(),
                'interactions': Interaction.objects.count()
            }
            
            return Response({
                'success': True,
                'statistics': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)