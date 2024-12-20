from django import forms
from .models import Project, Category, InventoryItem, InventoryItem, Location
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class InventoryItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), initial=0)
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label="Select a Location",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'category', 'price', 'image', 'location']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)  # Accept project as an argument
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if self.project and self.project.name != "Main Project":
            # Check for duplicates within the same project, excluding the main inventory
            if InventoryItem.objects.filter(name=name, project=self.project).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(f"An item with the name '{name}' already exists in this project.")
        
        # For main inventory, skip duplicate check across projects
        return cleaned_data

        def clean_image(self):
            image = self.cleaned_data.get('image')
            if image:
                # Validate file size
                max_size = 2 * 1024 * 1024  # 2MB
                if image.size > max_size:
                    raise forms.ValidationError("Image file size must be under 2MB.")
                
                # Validate image format (optional)
                valid_formats = ['JPEG', 'PNG']
                if image.image.format not in valid_formats:
                    raise forms.ValidationError("Invalid image format. Only JPEG and PNG are allowed.")
            return image

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']


class UpdateQuantityForm(forms.Form):
    quantity_change = forms.IntegerField(label="Quantity", min_value=1)
    operation = forms.ChoiceField(
        choices=[('add', 'Add'), ('remove', 'Remove')],
        widget=forms.RadioSelect
    )
