# Generated by Django 5.1.2 on 2024-10-22 20:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_inventoryitem_project'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inventoryitem',
            unique_together={('name', 'project')},
        ),
        migrations.CreateModel(
            name='MaterialHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_change', models.IntegerField()),
                ('operation', models.CharField(choices=[('add', 'Add'), ('remove', 'Remove')], max_length=6)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='inventory.inventoryitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
