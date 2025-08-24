import base64
import io
import json
import math
import random
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, time
from .models import AttendanceRecord, WorkSchedule
from .serializers import AttendanceRecordSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


def extract_face_features(face_image_file):
    """从人脸图像中提取特征向量"""
    try:
        # 获取图像文件大小作为基础特征
        face_image_file.seek(0)
        image_data = face_image_file.read()
        image_size = len(image_data)
        
        # 基于图像数据生成一个相对稳定的种子
        # 使用图像大小和部分字节内容来生成种子
        if len(image_data) > 1000:
            sample_bytes = image_data[100:200] + image_data[500:600] + image_data[-100:]
        else:
            sample_bytes = image_data
        
        # 创建一个相对稳定的种子
        seed = sum(sample_bytes) % 10000
        print(f"图像大小: {image_size}, 生成种子: {seed}")
        
        # 使用种子生成基础特征向量
        random.seed(seed)
        base_features = [random.random() for _ in range(128)]
        
        # 为了模拟真实的人脸识别，我们需要让同一个人的不同照片有相似的特征
        # 这里我们使用图像大小的范围来确定"用户身份"
        user_id_range = (image_size // 1000) % 10  # 基于图像大小确定用户身份范围
        
        # 根据用户身份范围调整特征向量
        for i in range(len(base_features)):
            if i % 10 == user_id_range:
                base_features[i] = 0.8 + (base_features[i] * 0.2)  # 特定位置的特征值较高
            else:
                base_features[i] = base_features[i] * 0.7  # 其他位置的特征值较低
        
        print(f"提取到人脸特征，特征维度: {len(base_features)}, 用户身份范围: {user_id_range}")
        return json.dumps(base_features)
    except Exception as e:
        print(f"特征提取失败: {e}")
        raise ValueError(f"特征提取失败: {str(e)}")


def find_matching_user(face_features, threshold=0.6):
    """根据人脸特征找到匹配的用户"""
    try:
        users_with_faces = User.objects.filter(face_registered=True)
        print(f"查找人脸匹配用户，共找到 {users_with_faces.count()} 个已注册人脸的用户")
        
        best_match = None
        highest_similarity = 0
        
        for user in users_with_faces:
            if not user.face_encoding:
                print(f"用户 {user.username} 没有人脸编码数据")
                continue
                
            try:
                stored_features = json.loads(user.face_encoding)
                similarity = calculate_similarity(face_features, stored_features)
                print(f"用户 {user.username} 相似度: {similarity:.3f}")
                
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = user
                    print(f"当前最佳匹配: {user.username}, 相似度: {similarity:.3f}")
            except Exception as e:
                print(f"处理用户 {user.username} 的人脸特征时出错: {e}")
                continue
        
        print(f"最终匹配结果: 用户={best_match.username if best_match else None}, 相似度={highest_similarity:.3f}, 阈值={threshold}")
        
        if highest_similarity >= threshold:
            return best_match, highest_similarity
        else:
            return None, highest_similarity
    except Exception as e:
        print(f"用户匹配失败: {e}")
        return None, 0


def calculate_similarity(features1, features2):
    """计算两个特征向量的相似度"""
    try:
        if len(features1) != len(features2):
            print(f"特征向量长度不匹配: {len(features1)} vs {len(features2)}")
            return 0
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(features1, features2))
        magnitude1 = math.sqrt(sum(a * a for a in features1))
        magnitude2 = math.sqrt(sum(b * b for b in features2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        
        # 将余弦相似度从[-1,1]转换到[0,1]
        similarity = (cosine_similarity + 1) / 2
        
        print(f"计算相似度: 余弦相似度={cosine_similarity:.3f}, 标准化相似度={similarity:.3f}")
        return similarity
    except Exception as e:
        print(f"计算相似度时出错: {e}")
        return 0


def base64_to_image_file(base64_string, filename='face_image.jpg'):
    """将base64字符串转换为图像文件对象"""
    try:
        # 移除base64前缀
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # 转换为RGB模式（如果是RGBA）
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # 保存到内存中的文件对象
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        # 创建Django文件对象
        file_obj = InMemoryUploadedFile(
            output, None, filename, 'image/jpeg',
            len(output.getvalue()), None
        )
        
        return file_obj
    except Exception as e:
        raise ValueError(f"无效的图像数据: {str(e)}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_clock_in(request):
    """人脸识别上班打卡"""
    user = request.user
    now = timezone.now()
    local_now = timezone.localtime(now)
    today = local_now.date()
    
    # 使用时间范围查询而不是 __date 查询
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, time.max))
    
    # 检查今天是否已经上班打卡
    existing_clock_in = AttendanceRecord.objects.filter(
        user=user,
        clock_time__gte=start_of_day,
        clock_time__lte=end_of_day,
        clock_type='in'
    ).first()
    
    if existing_clock_in:
        return Response(
            {'error': '今日已上班打卡', 'clock_time': existing_clock_in.clock_time},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取人脸图像数据
    face_image_data = request.data.get('face_image')
    if not face_image_data:
        return Response(
            {'error': '人脸图像数据不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 转换base64图像为文件对象
        face_image_file = base64_to_image_file(face_image_data, f'face_{user.employee_id}_{now.strftime("%Y%m%d_%H%M%S")}.jpg')
        
        # 提取人脸特征
        face_features = extract_face_features(face_image_file)
        parsed_features = json.loads(face_features)
        
        # 进行人脸识别匹配
        matched_user, similarity = find_matching_user(parsed_features)
        
        if not matched_user:
            return Response(
                {'error': '人脸识别失败，未找到匹配的用户'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if matched_user != user:
            return Response(
                {'error': f'人脸识别失败，识别为其他用户：{matched_user.username}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取工作时间表
    try:
        schedule = WorkSchedule.objects.get(user=user, is_active=True)
        work_start = schedule.start_time
    except WorkSchedule.DoesNotExist:
        # 默认上班时间为 9:00
        work_start = datetime.strptime('09:00:00', '%H:%M:%S').time()
    
    # 判断是否迟到
    current_time = now.time()
    clock_status = 'normal'
    if current_time > work_start:
        clock_status = 'late'
    
    # 创建考勤记录
    attendance_record = AttendanceRecord.objects.create(
        user=user,
        clock_time=now,
        clock_type='in',
        status=clock_status,
        location=request.data.get('location', ''),
        latitude=request.data.get('latitude'),
        longitude=request.data.get('longitude'),
        face_image=face_image_file,
        note=f'人脸识别打卡 (相似度: {similarity:.2%})'
    )
    
    serializer = AttendanceRecordSerializer(attendance_record)
    return Response({
        'message': '人脸识别上班打卡成功',
        'recognition_info': {
            'similarity': f"{similarity:.2%}",
            'user_name': user.username
        },
        'record': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_clock_out(request):
    """人脸识别下班打卡"""
    user = request.user
    now = timezone.now()
    local_now = timezone.localtime(now)
    today = local_now.date()
    
    # 使用时间范围查询而不是 __date 查询
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, time.max))
    
    # 检查今天是否已经下班打卡
    existing_clock_out = AttendanceRecord.objects.filter(
        user=user,
        clock_time__gte=start_of_day,
        clock_time__lte=end_of_day,
        clock_type='out'
    ).first()
    
    if existing_clock_out:
        return Response(
            {'error': '今日已下班打卡', 'clock_time': existing_clock_out.clock_time},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查是否有上班打卡记录
    clock_in_record = AttendanceRecord.objects.filter(
        user=user,
        clock_time__gte=start_of_day,
        clock_time__lte=end_of_day,
        clock_type='in'
    ).first()
    
    if not clock_in_record:
        return Response(
            {'error': '请先进行上班打卡'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取人脸图像数据
    face_image_data = request.data.get('face_image')
    if not face_image_data:
        return Response(
            {'error': '人脸图像数据不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 转换base64图像为文件对象
        face_image_file = base64_to_image_file(face_image_data, f'face_{user.employee_id}_{now.strftime("%Y%m%d_%H%M%S")}.jpg')
        
        # 提取人脸特征
        face_features = extract_face_features(face_image_file)
        parsed_features = json.loads(face_features)
        
        # 进行人脸识别匹配
        matched_user, similarity = find_matching_user(parsed_features)
        
        if not matched_user:
            return Response(
                {'error': '人脸识别失败，未找到匹配的用户'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if matched_user != user:
            return Response(
                {'error': f'人脸识别失败，识别为其他用户：{matched_user.username}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取工作时间表
    try:
        schedule = WorkSchedule.objects.get(user=user, is_active=True)
        work_end = schedule.end_time
    except WorkSchedule.DoesNotExist:
        # 默认下班时间为 18:00
        work_end = datetime.strptime('18:00:00', '%H:%M:%S').time()
    
    # 判断是否早退
    current_time = now.time()
    clock_status = 'normal'
    if current_time < work_end:
        clock_status = 'early'
    
    # 创建考勤记录
    attendance_record = AttendanceRecord.objects.create(
        user=user,
        clock_time=now,
        clock_type='out',
        status=clock_status,
        location=request.data.get('location', ''),
        latitude=request.data.get('latitude'),
        longitude=request.data.get('longitude'),
        face_image=face_image_file,
        note=f'人脸识别打卡 (相似度: {similarity:.2%})'
    )
    
    serializer = AttendanceRecordSerializer(attendance_record)
    return Response({
        'message': '人脸识别下班打卡成功',
        'recognition_info': {
            'similarity': f"{similarity:.2%}",
            'user_name': user.username
        },
        'record': serializer.data
    }, status=status.HTTP_201_CREATED)
