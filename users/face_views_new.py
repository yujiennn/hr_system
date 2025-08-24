import base64
import io
import json
import random
import math
from PIL import Image
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
    """提取人脸特征（简化版本，返回模拟特征）"""
    try:
        # 这里应该使用真实的人脸识别库如face_recognition
        # 现在返回模拟的特征向量
        random.seed(42)  # 固定种子确保一致性
        features = [random.random() for _ in range(128)]  # 128维特征向量
        return features
    except Exception as e:
        print(f"特征提取失败: {e}")
        return None


def compare_faces(features1, features2, threshold=0.6):
    """比较两个人脸特征的相似度"""
    try:
        if not features1 or not features2:
            return False, 0.0
        
        # 计算欧几里得距离
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(features1, features2)))
        
        # 转换为相似度
        max_distance = math.sqrt(len(features1))  # 最大可能距离
        similarity = 1 - (distance / max_distance)
        
        # 判断是否匹配
        is_match = similarity > threshold
        return is_match, similarity
    except Exception as e:
        print(f"人脸比较失败: {e}")
        return False, 0.0


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

        # 查找匹配的用户
        users_with_faces = User.objects.filter(face_registered=True)
        
        best_match = None
        highest_similarity = 0
        
        for user in users_with_faces:
            if user.face_encoding:
                stored_features = json.loads(user.face_encoding)
                is_match, similarity = compare_faces(features, stored_features)
                
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = user

        if best_match and highest_similarity > 0.6:
            return Response({
                'success': True,
                'user_id': best_match.id,
                'user_name': best_match.username,
                'similarity': f"{highest_similarity:.2%}"
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
