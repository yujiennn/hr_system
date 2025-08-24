from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .models import CompanyLocation
from .serializers import CompanyLocationSerializer
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    计算两个地理坐标之间的距离（单位：米）
    使用Haversine公式
    """
    # 转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # 地球半径（米）
    r = 6371000
    
    return c * r


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_locations(request):
    """获取所有可用的公司位置"""
    try:
        locations = CompanyLocation.objects.filter(is_active=True)
        serializer = CompanyLocationSerializer(locations, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取位置信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_location(request):
    """验证用户当前位置是否在公司打卡范围内"""
    try:
        user_lat = float(request.data.get('latitude'))
        user_lon = float(request.data.get('longitude'))
        location_id = request.data.get('location_id')
        
        if not all([user_lat, user_lon, location_id]):
            return Response({
                'success': False,
                'message': '缺少必要的位置信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取公司位置
        try:
            company_location = CompanyLocation.objects.get(id=location_id, is_active=True)
        except CompanyLocation.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定的公司位置不存在或已禁用'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 计算距离
        distance = calculate_distance(
            user_lat, user_lon,
            company_location.latitude, company_location.longitude
        )
        
        # 判断是否在范围内
        in_range = distance <= company_location.radius
        
        return Response({
            'success': True,
            'data': {
                'in_range': in_range,
                'distance': round(distance, 1),
                'allowed_radius': company_location.radius,
                'location_name': company_location.name,
                'location_address': company_location.address
            }
        })
        
    except ValueError:
        return Response({
            'success': False,
            'message': '位置坐标格式错误'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'位置验证失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nearest_location(request):
    """获取距离用户最近的公司位置"""
    try:
        user_lat = float(request.GET.get('latitude'))
        user_lon = float(request.GET.get('longitude'))
        
        if not all([user_lat, user_lon]):
            return Response({
                'success': False,
                'message': '缺少位置坐标'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        locations = CompanyLocation.objects.filter(is_active=True)
        if not locations.exists():
            return Response({
                'success': False,
                'message': '暂无可用的公司位置'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 计算到每个位置的距离
        location_distances = []
        for location in locations:
            distance = calculate_distance(
                user_lat, user_lon,
                location.latitude, location.longitude
            )
            location_distances.append({
                'location': location,
                'distance': distance
            })
        
        # 找到最近的位置
        nearest = min(location_distances, key=lambda x: x['distance'])
        location_data = CompanyLocationSerializer(nearest['location']).data
        location_data['distance'] = round(nearest['distance'], 1)
        location_data['in_range'] = nearest['distance'] <= nearest['location'].radius
        
        return Response({
            'success': True,
            'data': location_data
        })
        
    except ValueError:
        return Response({
            'success': False,
            'message': '位置坐标格式错误'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取最近位置失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
