from django.db import models
from .widgets import ImageUploaderWidget
from django import forms


class ImageUploaderField(models.URLField):
    def __init__(self, upload_url=None, *args, **kwargs):
        self.upload_url = upload_url
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_form_class():
        return ImageUploaderFormField

    def formfield(self, **kwargs):
        defaults = {
            "form_class": ImageUploaderFormField,
            "widget": ImageUploaderWidget(upload_url=self.upload_url),
            "upload_url": self.upload_url,
        }
        defaults.update(kwargs)
        return super(ImageUploaderField, self).formfield(**defaults)


class ImageUploaderFormField(forms.fields.URLField):
    def __init__(self, upload_url=None, **kwargs):
        kwargs.update({"widget": ImageUploaderWidget(upload_url=upload_url)})
        super(ImageUploaderFormField, self).__init__(**kwargs)
