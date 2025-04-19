# Generated by Django 5.2 on 2025-04-18 23:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('descuento', models.DecimalField(decimal_places=2, help_text='Porcentaje de descuento, ej: 25.00 para 25%', max_digits=5)),
                ('estado', models.BooleanField(default=True)),
                ('fecha_exp', models.DateField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cupones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.IntegerField(blank=True, help_text='Calificación del pedido (opcional, del 1 al 5 por ejemplo)', null=True)),
                ('fecha_pedido', models.DateTimeField(auto_now_add=True, help_text='Fecha en que se realizó el pedido')),
                ('descuento', models.DecimalField(decimal_places=2, default=0.0, help_text='Descuento aplicado en porcentaje, ej: 15.00 = 15%', max_digits=5)),
                ('total', models.DecimalField(decimal_places=2, help_text='Total del pedido después del descuento', max_digits=10)),
                ('activo', models.BooleanField(default=True)),
                ('cupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pedidos', to='pedidos.cupon')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.producto')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='pedidos.pedido')),
            ],
        ),
    ]
