from django import forms
from .models import CoverImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = CoverImage
        fields = ['final_image']