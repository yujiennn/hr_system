from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
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


class CompanyLocationViewSet(viewsets.ModelViewSet):
    """公司位置管理视图集"""
    serializer_class = CompanyLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 禁用分页
    
    def get_queryset(self):
        # 检查用户是否为管理员
        is_admin = (
            self.request.user.user_type == 'admin' or 
            self.request.user.is_superuser or 
            self.request.user.is_staff
        )
        
        if self.action in ['list', 'retrieve']:
            if is_admin:
                # 管理员可以查看所有位置
                return CompanyLocation.objects.all()
            else:
                # 普通用户和员工只能查看启用的位置
                return CompanyLocation.objects.filter(is_active=True)
        else:
            # 只有管理员可以进行增删改操作
            if is_admin:
                return CompanyLocation.objects.all()
            else:
                return CompanyLocation.objects.none()
    
    def perform_create(self, serializer):
        if not (self.request.user.user_type == 'admin' or self.request.user.is_superuser):
            raise permissions.PermissionDenied("只有管理员可以创建公司位置")
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        if not (self.request.user.user_type == 'admin' or self.request.user.is_superuser):
            raise permissions.PermissionDenied("只有管理员可以修改公司位置")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not (self.request.user.user_type == 'admin' or self.request.user.is_superuser):
            raise permissions.PermissionDenied("只有管理员可以删除公司位置")
        super().perform_destroy(instance)
    
    @action(detail=False, methods=['post'])
    def validate_location(self, request):
        """验证用户位置是否在打卡范围内"""
        try:
            user_lat = float(request.data.get('latitude'))
            user_lon = float(request.data.get('longitude'))
            location_id = request.data.get('location_id')
            
            if not all([user_lat, user_lon]):
                return Response({
                    'success': False,
                    'message': '缺少位置坐标'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 如果指定了位置ID，验证该位置
            if location_id:
                try:
                    location = CompanyLocation.objects.get(id=location_id, is_active=True)
                    distance = calculate_distance(user_lat, user_lon, location.latitude, location.longitude)
                    in_range = distance <= location.radius
                    
                    return Response({
                        'success': True,
                        'data': {
                            'in_range': in_range,
                            'distance': round(distance, 1),
                            'allowed_radius': location.radius,
                            'location_name': location.name,
                            'location_address': location.address
                        }
                    })
                except CompanyLocation.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': '指定的公司位置不存在'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # 否则找到最近的位置
            locations = CompanyLocation.objects.filter(is_active=True)
            if not locations.exists():
                return Response({
                    'success': False,
                    'message': '暂无可用的打卡位置'
                }, status=status.HTTP_404_NOT_FOUND)
            
            nearest_location = None
            min_distance = float('inf')
            
            for location in locations:
                distance = calculate_distance(user_lat, user_lon, location.latitude, location.longitude)
                if distance < min_distance:
                    min_distance = distance
                    nearest_location = location
            
            in_range = min_distance <= nearest_location.radius
            
            return Response({
                'success': True,
                'data': {
                    'in_range': in_range,
                    'distance': round(min_distance, 1),
                    'allowed_radius': nearest_location.radius,
                    'location_name': nearest_location.name,
                    'location_address': nearest_location.address,
                    'location_id': nearest_location.id
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
    
    @action(detail=False, methods=['get'])
    def nearest(self, request):
        """获取距离用户最近的公司位置"""
        try:
            user_lat = float(request.query_params.get('latitude'))
            user_lon = float(request.query_params.get('longitude'))
            
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
