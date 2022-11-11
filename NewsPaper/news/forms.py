from django import forms
from .models import Post
from django.db import models

class PostForm(forms.ModelForm):
    description = models.TextField()
    title = models.CharField(max_length=255)
    class Meta:
        model = Post
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        title = cleaned_data.get("title")
        if description is not None and len(description) < 20:
            raise ValidationError({
                "description": "Описание не может быть менее 20 символов."
            })

        if len(title) > 255:
            raise ValidationError(
                "Наименование не может быть больше 255 символов."
            )
        return cleaned_data

    def get_absolute_url(self):
        return reverse('st_detail', args=[str(self.id)])


