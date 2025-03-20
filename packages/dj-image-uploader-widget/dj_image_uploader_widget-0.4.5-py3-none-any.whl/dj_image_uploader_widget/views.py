from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .oss import upload_to_oss
import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
@require_POST
@login_required
def upload_view(request):
    try:
        image_file = request.FILES["image"]
        user_id = request.user.id
        # 判断是否为 UUID 类型
        if isinstance(user_id, uuid.UUID):
            pathname = f"user-{user_id}"
        else:
            # 将数字 ID 格式化为 8 位带前导零
            try:
                formatted_id = f"{int(user_id):08d}"
            except ValueError:
                # 如果既不是 UUID 也不是数字，保留原始值
                formatted_id = str(user_id)

        pathname = f"User-{formatted_id}"
        print(pathname)
        oss_url = upload_to_oss(image_file, pathname)
        return JsonResponse({"url": oss_url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
