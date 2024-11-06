# Generated by Django 5.1.2 on 2024-10-22 17:51

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_project_inventoryitem_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='inventory.project'),
            preserve_default=False,
        ),
    ]