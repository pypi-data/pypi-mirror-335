from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import oss2


def get_oss_config():
    return getattr(
        settings,
        "DJ_IMAGE_UPLOADER_OSS_CONFIG",
    )


def upload_to_oss(file_obj, pathname=None):
    config = get_oss_config()
    if pathname:
        filename = f"{pathname}/{file_obj.name}"
    else:
        filename = f"{config['BASE_PATH']}/{file_obj.name}"
    try:
        auth = oss2.Auth(config["ACCESS_KEY_ID"], config["ACCESS_KEY_SECRET"])
        bucket = oss2.Bucket(auth, config["ENDPOINT"], config["BUCKET_NAME"])

        filename = f"{pathname}/{file_obj.name}"
        bucket.put_object(filename, file_obj)
        return f"https://{config['BUCKET_NAME']}.{config['ENDPOINT']}/{filename}"
    except KeyError as e:
        raise ImproperlyConfigured(f"Missing OSS config: {e}")
