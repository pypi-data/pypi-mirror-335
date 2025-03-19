# dj_vditor

Django integration for Vditor Markdown Editor

## Installation

```bash
pip install dj_vditor

# 如果需要OSS支持
pip install dj_vditor[oss]
```

## Quick Start

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'dj_vditor',
]
```

2. Add URL route in `urls.py`:

```python
# 当然你也可以自定义url和view, 只要跟配置中的upload.url一致即可
urlpatterns = [
    ...
    path('vditor/', include('dj_vditor.urls')),
]
```

3. Use in Model:

```python
from dj_vditor.models import VditorTextField

class Article(models.Model):
    content = VditorTextField(config_name="my_config")
```

4. Configure settings:

```python
# 这是默认配置, 如果不需要修改的话, 可以不设置, 直接使用默认配置
VDITOR_CONFIGS = {
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
        "url": "/vditor-upload/",  # 上传接口地址
        "max": 5 * 1024 * 1024,  # 5MB
        "accept": "image/png,image/jpeg,image/gif,image/webp",  # 允许类型
        "fieldName": "file[]",
        "multiple": True,
    },
}
```
