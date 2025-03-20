# Django Image Uploader Widget

## 安装

```bash
pip install dj-image-uploader-widget
```

## 配置

```python
# settings.py
DJ_IMAGE_UPLOADER_OSS_CONFIG = {
    'ACCESS_KEY_ID': 'your_aliyun_key',
    'ACCESS_KEY_SECRET': 'your_aliyun_secret',
    'ENDPOINT': 'oss-cn-beijing.aliyuncs.com',
    'BUCKET_NAME': 'your-bucket-name',
    'BASE_PATH': 'user-uploads/'  # 定义你的上传路径, 可选
}

INSTALLED_APPS = [
    ...
    'dj_image_uploader_widget',
]

# urls.py
from dj_image_uploader_widget import views as upload_views

urlpatterns = [
    ...
    path('upload/', upload_views.upload_view, name='image_upload'),
]
```

## 使用示例

```python
# models.py
from django.db import models
from dj_image_uploader_widget.fields import ImageUploadField

class Article(models.Model):
    cover = ImageUploadField(
        upload_url='/upload/',  # 对应你的上传路径
        verbose_name="文章封面"
    )
```
