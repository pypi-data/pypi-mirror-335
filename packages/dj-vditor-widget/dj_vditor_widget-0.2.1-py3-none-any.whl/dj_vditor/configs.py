from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULT_CONFIG = {
    "width": "100%",
    "height": 720,
    "cache": {"enable": False},
    "mode": "sv",
    "debugger": "false",
    "icon": "ant",
    "outline": "",
    "counter": {
        "enable": True,
    },
    "lang": "zh_CN",
    "toolbar": [
        "emoji",
        "headings",
        "bold",
        "italic",
        "strike",
        "link",
        "|",
        "list",
        "ordered-list",
        "check",
        "outdent",
        "indent",
        "|",
        "quote",
        "line",
        "code",
        "inline-code",
        "insert-after",
        "table",
        "|",
        "upload",
        "fullscreen",
        "export",
        "|",
        "outline",
    ],
    "upload": {
        "url": "/upload-to-oss/",  # 上传接口地址
        "max": 5 * 1024 * 1024,  # 5MB
        "accept": "image/png,image/jpeg,image/gif,image/webp",  # 允许类型
        "fieldName": "file[]",
        "multiple": True,
    },
    # "upload_max": 10,
    # "upload_accept": "image/*",
    # "toolbarConfig": {
    # "hide": True,
    # "pin": True
    # },
    # "fullscreen": {
    # "enable": True,
    # "isolate": True # 启用视觉隔离
    # }
}


class VditorConfig(dict):
    def __init__(self, config_name="default"):
        self.update(DEFAULT_CONFIG)
        self.set_configs(config_name)

    def set_configs(self, config_name="default"):
        configs = getattr(settings, "VDITOR_CONFIGS", None)
        if configs:
            if isinstance(configs, dict):
                if config_name in configs:
                    config = configs[config_name]
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured(
                            'VDITOR_CONFIGS["%s"] \
                                        setting must be a dictionary type.'
                            % config_name
                        )
                    self.update(config)
                else:
                    raise ImproperlyConfigured(
                        "No configuration named '%s' \
                                    found in your VDITOR_CONFIGS setting."
                        % config_name
                    )
            else:
                raise ImproperlyConfigured(
                    "VDITOR_CONFIGS setting must be a\
                                dictionary type."
                )
