# Generated by Django 5.2 on 2025-04-12 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autor',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='editorial',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='genero',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='subcategoria',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
