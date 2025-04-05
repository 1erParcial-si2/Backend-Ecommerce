from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from usuarios.views import UsuarioViewSet, LoginView  # Asegúrate de que esto sea correcto

# Swagger imports
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de rutas automáticas
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Backend SI2",
        default_version='v1',
        description="Documentación interactiva de la API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="tucorreo@ejemplo.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[TokenAuthentication],  # 👈 esto es clave
)

# Rutas del proyecto
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),

    # Swagger y ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
