# Generated by Django 2.2.4 on 2019-08-24 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_auto_20190824_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]