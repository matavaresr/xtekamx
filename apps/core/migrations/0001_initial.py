# Generated by Django 5.1.7 on 2025-05-03 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('url_portada', models.TextField()),
                ('descripcion', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Amenidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefono', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConfiguracionSitio',
            fields=[
                ('clave', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('valor', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('ubicacion', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoPaquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ubicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('url_portada', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contrasena', models.CharField(max_length=255)),
                ('tipo', models.SmallIntegerField(choices=[(1, 'Administrador'), (2, 'Supervisor'), (3, 'Empleado')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Paquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('duracion_dias', models.SmallIntegerField()),
                ('precio_adulto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_nino', models.DecimalField(decimal_places=2, max_digits=10)),
                ('minimo_personas', models.SmallIntegerField()),
                ('maximo_personas', models.SmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('tipo_paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tipopaquete')),
            ],
        ),
        migrations.CreateModel(
            name='Itinerario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.SmallIntegerField()),
                ('descripcion', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
        ),
        migrations.CreateModel(
            name='ImagenPaquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_imagen', models.TextField()),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('es_portada', models.BooleanField(default=False)),
                ('public_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.TextField()),
                ('respuesta', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
        ),
        migrations.CreateModel(
            name='Reservacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('cantidad_adultos', models.SmallIntegerField()),
                ('cantidad_ninos', models.SmallIntegerField()),
                ('total_pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.SmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
        ),
        migrations.CreateModel(
            name='PaqueteActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.actividad')),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
            options={
                'unique_together': {('paquete', 'actividad')},
            },
        ),
        migrations.CreateModel(
            name='PaqueteAmenidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.SmallIntegerField()),
                ('amenidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.amenidad')),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
            ],
            options={
                'unique_together': {('paquete', 'amenidad')},
            },
        ),
        migrations.CreateModel(
            name='ClienteReservacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cliente')),
                ('reservacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reservacion')),
            ],
            options={
                'unique_together': {('cliente', 'reservacion')},
            },
        ),
        migrations.CreateModel(
            name='PaqueteUbicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paquete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paquete')),
                ('ubicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ubicacion')),
            ],
            options={
                'unique_together': {('paquete', 'ubicacion')},
            },
        ),
    ]
