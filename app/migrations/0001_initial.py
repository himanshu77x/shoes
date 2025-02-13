# Generated by Django 5.1.2 on 2025-02-02 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('selling_price', models.FloatField()),
                ('dicounted_price', models.FloatField()),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('ms', 'menshoes'), ('ws', 'womenshoes'), ('ks', 'kids shoes')], max_length=2)),
                ('product_image', models.ImageField(upload_to='products')),
            ],
        ),
    ]
