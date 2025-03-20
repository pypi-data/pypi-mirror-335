from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ImproperlyConfigured
import oss2
from django.utils.decorators import method_decorator


def upload_to_oss(file_obj, pathname=None):
    oss_config = settings.DJ_IMAGE_UPLOADER_OSS_CONFIG
    if pathname:
        filename = f"{pathname}/{file_obj.name}"
    else:
        filename = f"{oss_config['BASE_PATH']}/{file_obj.name}"
    try:
        auth = oss2.Auth(oss_config["ACCESS_KEY_ID"], oss_config["ACCESS_KEY_SECRET"])
        bucket = oss2.Bucket(auth, oss_config["ENDPOINT"], oss_config["BUCKET_NAME"])

        filename = f"{pathname}/{file_obj.name}"
        bucket.put_object(filename, file_obj)
        return (
            f"https://{oss_config['BUCKET_NAME']}.{oss_config['ENDPOINT']}/{filename}"
        )
    except KeyError as e:
        raise ImproperlyConfigured(f"Missing OSS config: {e}")
