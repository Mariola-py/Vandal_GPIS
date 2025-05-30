# Generated by Django 5.2.1 on 2025-05-11 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vandalproy', '0011_blogpost_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticia',
            name='contenido_en',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='noticia',
            name='resumen_en',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='noticia',
            name='titulo_en',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='noticia',
            name='contenido',
            field=models.TextField(default='Contenido Vacio'),
            preserve_default=False,
        ),
    ]
