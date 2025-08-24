"""
URL configuration for hr_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
@require_http_methods(["POST"])
def upload_logo(request):
    """上传公司logo"""
    if 'file' not in request.FILES:
        return JsonResponse({'error': '没有找到上传的文件'}, status=400)
    
    file = request.FILES['file']
    
    # 检查文件类型
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        return JsonResponse({'error': '只支持 JPG, PNG, GIF 格式的图片'}, status=400)
    
    # 检查文件大小 (5MB)
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': '文件大小不能超过5MB'}, status=400)
    
    try:
        # 创建logos目录
        logo_dir = 'logos'
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, logo_dir)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, logo_dir))
        
        # 生成文件名
        file_extension = os.path.splitext(file.name)[1]
        filename = f'company_logo{file_extension}'
        file_path = os.path.join(logo_dir, filename)
        
        # 保存文件
        saved_path = default_storage.save(file_path, ContentFile(file.read()))
        
        # 返回文件URL
        file_url = settings.MEDIA_URL + saved_path
        
        return JsonResponse({
            'message': 'Logo上传成功',
            'url': file_url,
            'filename': filename
        })
        
    except Exception as e:
        return JsonResponse({'error': f'上传失败: {str(e)}'}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/salary/', include('salary.urls')),
    path('api/performance/', include('performance.urls')),
    path('api/leave/', include('leave.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/system/', include('system_config.urls')),
    path('api/upload/logo', upload_logo, name='upload_logo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
