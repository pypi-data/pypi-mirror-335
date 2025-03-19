from django.conf import settings
from django.http import JsonResponse
from .configs import VditorConfig
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import logging
from .oss import upload_to_oss
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ImproperlyConfigured
from oss2.exceptions import OssError


def generate_user_path(user_id):
    """生成用户专属存储路径"""
    try:
        # 尝试解析为 UUID
        uuid.UUID(str(user_id))
        return f"user-{user_id}"
    except ValueError:
        try:
            # 格式化为 8 位数字
            return f"user-{int(user_id):08d}"
        except ValueError:
            # 哈希处理非常规 ID
            return f"user-{abs(hash(user_id)):016x}"


VDITOR_CONFIGS = VditorConfig("default")

logger = logging.getLogger("vditor.upload")


@login_required
@require_POST
@csrf_exempt
def vditor_images_upload_view(request):
    """处理图片上传请求"""
    file_list = request.FILES.getlist("file[]")

    # 验证文件存在
    if not file_list:
        return JsonResponse(
            {
                "code": 400,
                "msg": "未收到上传文件",
                "data": {"errFiles": [], "succMap": {}},
            },
            status=400,
        )

    succ_map = {}
    err_files = []

    allowed_types = VDITOR_CONFIGS["upload"]["accept"].split(",")
    max_size = VDITOR_CONFIGS["upload"]["max"]
    user_path = generate_user_path(request.user.id)

    for file_obj in file_list:

        # 文件类型验证
        if file_obj.content_type not in allowed_types:
            err_files.append(file_obj.name)
            continue

        # 文件大小验证
        if file_obj.size > max_size:
            err_files.append(file_obj.name)
            continue
            return JsonResponse(
                {
                    "code": 413,
                    "msg": f"文件大小超过{max_size//1024//1024}MB限制",
                    "data": {"errFiles": [file_obj.name], "succMap": {}},
                },
                status=413,
            )

        try:
            # 上传文件
            file_url = upload_to_oss(file_obj, user_path)
            succ_map[file_obj.name] = file_url
        except Exception as e:
            err_files.append(file_obj.name)
            logger.error(f"文件上传失败: {str(e)}")

    return JsonResponse(
        {
            "code": 0 if len(err_files) == 0 else 500,
            "msg": f"成功上传 {len(succ_map)} 个文件",
            "data": {
                "errFiles": [],
                "succMap": succ_map,
            },
        }
    )
