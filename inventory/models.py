from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

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
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.catergory.name if self.category else 'Uncategorized'})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the image first to get a valid path
        if self.image:
            self.compress_image(self.image.path)

    def compress_image(self, image_path):
        img = Image.open(image_path)
        img = img.convert('RGB')  # Ensure image is in RGB format

        max_size = 2 * 1024 * 1024  # 2MB
        target_ppi = 100

        # Resize the image to 100 PPI
        img_width, img_height = img.size
        img = img.resize((int(img_width * target_ppi / 300), int(img_height * target_ppi / 300)), Image.LANCZOS)

        # Save the image with reduced quality directly to the original path
        quality = 85
        while True:
            img.save(image_path, 'JPEG', quality=quality)
            if os.path.getsize(image_path) <= max_size or quality <= 10:
                break
            quality -= 5

        img.close()

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']  # Ensure categories are listed in alphabetical order

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

class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
