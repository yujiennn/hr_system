import base64
import io
import json
import numpy as np
from PIL import Image
import face_recognition
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User


def base64_to_image(base64_string):
    """将base64字符串转换为PIL Image对象"""
    try:
        # 移除data:image/jpeg;base64,前缀
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        print(f"Base64转换图片失败: {e}")
        return None


def extract_face_features(image):
    """提取人脸特征（使用真实的face_recognition库）"""
    try:
        # 转换PIL Image为numpy数组
        image_array = np.array(image.convert('RGB'))
        
        # 检测人脸
        face_locations = face_recognition.face_locations(image_array, model='hog')
        if not face_locations:
            print("未检测到人脸")
            return None
        
        # 提取特征向量（128维）
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if not face_encodings:
            print("无法提取人脸特征")
            return None
        
        # 返回第一个人脸的特征（转为列表便于JSON序列化）
        return face_encodings[0].tolist()
    except Exception as e:
        print(f"特征提取失败: {e}")
        return None


def compare_faces(features1, features2, threshold=0.6):
    """比较两个人脸特征的相似度
    
    Args:
        features1: 第一个人脸的特征向量（128维）
        features2: 第二个人脸的特征向量（128维）
        threshold: 距离阈值（越小越严格）。建议值：
            - 0.5: 非常严格（同一人识别率>99%）
            - 0.6: 标准值（推荐用于员工打卡）
            - 0.7: 较宽松（误识率增加）
    
    Returns:
        (is_match: bool, distance: float) - 是否匹配和距离值
    """
    try:
        if not features1 or not features2:
            return False, 1.0
        
        # 转换为numpy数组便于计算
        features1 = np.array(features1) if not isinstance(features1, np.ndarray) else features1
        features2 = np.array(features2) if not isinstance(features2, np.ndarray) else features2
        
        # 计算欧几里得距离
        # 在face_recognition库中，同一个人的距离通常<0.6，不同人的距离>0.6
        distance = np.linalg.norm(features1 - features2)
        
        # 判断是否匹配
        is_match = distance < threshold
        return is_match, distance
    except Exception as e:
        print(f"人脸比较失败: {e}")
        return False, 1.0


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_registration_view(request):
    """人脸录入"""
    try:
        face_image_data = request.data.get('face_image')
        if not face_image_data:
            return Response({'error': '缺少人脸图片'}, status=status.HTTP_400_BAD_REQUEST)

        # 转换图片
        image = base64_to_image(face_image_data)
        if not image:
            return Response({'error': '无效的图片格式'}, status=status.HTTP_400_BAD_REQUEST)

        # 提取特征
        features = extract_face_features(image)
        if not features:
            return Response({'error': '人脸特征提取失败'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存到用户模型
        user = request.user
        user.face_encoding = json.dumps(features)
        user.face_registered = True
        user.face_registered_at = timezone.now()
        
        # 保存人脸图片
        if hasattr(user, 'face_image') and user.face_image:
            user.face_image.delete(save=False)
        
        # 将base64图片保存为文件
        from django.core.files.base import ContentFile
        import uuid
        
        image_data = base64.b64decode(face_image_data.split(',')[1])
        image_file = ContentFile(image_data, name=f'face_{user.id}_{uuid.uuid4().hex[:8]}.jpg')
        user.face_image.save(image_file.name, image_file, save=False)
        
        user.save()

        return Response({
            'message': '人脸录入成功',
            'face_registered': True,
            'registered_at': user.face_registered_at.isoformat()
        })

    except Exception as e:
        print(f"人脸录入失败: {e}")
        return Response({'error': '录入失败，请重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_recognition_view(request):
    """人脸识别"""
    try:
        face_image_data = request.data.get('face_image')
        if not face_image_data:
            return Response({'error': '缺少人脸图片'}, status=status.HTTP_400_BAD_REQUEST)

        # 转换图片
        image = base64_to_image(face_image_data)
        if not image:
            return Response({'error': '无效的图片格式'}, status=status.HTTP_400_BAD_REQUEST)

        # 提取特征
        features = extract_face_features(image)
        if not features:
            return Response({'error': '人脸特征提取失败'}, status=status.HTTP_400_BAD_REQUEST)

        # 查找匹配的用户（距离越小越接近）
        users_with_faces = User.objects.filter(face_registered=True)
        
        best_match = None
        smallest_distance = float('inf')
        
        for user in users_with_faces:
            if user.face_encoding:
                stored_features = json.loads(user.face_encoding)
                is_match, distance = compare_faces(features, stored_features, threshold=0.6)
                
                # 找出距离最小的匹配
                if distance < smallest_distance:
                    smallest_distance = distance
                    best_match = user

        # 距离 < 0.6 表示同一个人，> 0.6 表示不同的人
        if best_match and smallest_distance < 0.6:
            return Response({
                'success': True,
                'user_id': best_match.id,
                'user_name': best_match.username,
                'distance': f"{smallest_distance:.4f}",
                'message': '人脸识别成功'
            })
        else:
            return Response({
                'success': False,
                'message': '未找到匹配的用户'
            })

    except Exception as e:
        print(f"人脸识别失败: {e}")
        return Response({'error': '识别失败，请重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def face_status_view(request):
    """获取人脸状态"""
    try:
        user = request.user
        return Response({
            'registered': user.face_registered,
            'registeredAt': user.face_registered_at.isoformat() if user.face_registered_at else None,
            'user_name': user.username
        })
    except Exception as e:
        print(f"获取人脸状态失败: {e}")
        return Response({'error': '获取状态失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_face_data_view(request):
    """删除人脸数据"""
    try:
        user = request.user
        
        # 删除人脸图片文件
        if hasattr(user, 'face_image') and user.face_image:
            user.face_image.delete(save=False)
        
        # 清除人脸数据
        user.face_encoding = None
        user.face_registered = False
        user.face_registered_at = None
        user.save()

        return Response({'message': '人脸数据删除成功'})

    except Exception as e:
        print(f"删除人脸数据失败: {e}")
        return Response({'error': '删除失败，请重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 向后兼容的类视图别名
FaceRegistrationView = face_registration_view
FaceRecognitionView = face_recognition_view
FaceStatusView = face_status_view
DeleteFaceDataView = delete_face_data_view
