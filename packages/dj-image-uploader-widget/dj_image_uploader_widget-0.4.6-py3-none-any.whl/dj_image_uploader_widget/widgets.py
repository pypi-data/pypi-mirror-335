from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe


class ImageUploaderWidget(widgets.URLInput):
    template_name = "dj_image_uploader_widget/uploader.html"

    def __init__(self, upload_url, attrs=None):
        self.upload_url = upload_url
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["upload_url"] = self.upload_url
        context["widget"]["value"] = value
        return context

    class Media:
        css = {"all": ("uploader/css/uploader.css",)}
        js = ("uploader/js/uploader.js",)
