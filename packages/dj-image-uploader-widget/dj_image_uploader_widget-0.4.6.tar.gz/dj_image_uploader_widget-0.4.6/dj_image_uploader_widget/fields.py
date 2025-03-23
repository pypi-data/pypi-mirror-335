from django.db import models
from .widgets import ImageUploaderWidget
from django import forms


class ImageUploadField(models.Field):
    def __init__(self, upload_url=None, *args, **kwargs):
        self.upload_url = upload_url
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "form_class": ImageUploaderFormField,
            "widget": ImageUploaderWidget(upload_url=self.upload_url),
            "upload_url": self.upload_url,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class ImageUploaderFormField(forms.fields.Field):
    def __init__(self, upload_url=None, *args, **kwargs):
        kwargs.update["widget"]: ImageUploaderWidget(upload_url=upload_url)
        super().__init__(*args, **kwargs)
