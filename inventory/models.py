from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="inventory_items", blank=False, null=False)
    image = models.ImageField(upload_to='inventory_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
	name = models.CharField(max_length=200)

	class Meta:
		verbose_name_plural = 'categories'

	def __str__(self):
		return self.name

class MaterialHistory(models.Model):
    OPERATION_CHOICES = (
        ('add', 'Add'),
        ('remove', 'Remove'),
    )

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='history')
    quantity_change = models.IntegerField()
    operation = models.CharField(max_length=6, choices=OPERATION_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.quantity_change} units {self.operation}d on {self.date}'
