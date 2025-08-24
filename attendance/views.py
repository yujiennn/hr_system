from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import AttendanceRecord, WorkSchedule, AttendanceException
from .serializers import AttendanceRecordSerializer, WorkScheduleSerializer, AttendanceExceptionSerializer
from users.models import User
from system_config.models import CompanyLocation
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


def validate_attendance_location(latitude, longitude, location_id=None):
    """
    验证打卡位置是否在允许范围内
    返回: (is_valid, location_info, distance)
    """
    if not latitude or not longitude:
        return False, None, None
    
    try:
        # 如果指定了位置ID，验证该位置
        if location_id:
            location = CompanyLocation.objects.get(id=location_id, is_active=True)
            distance = calculate_distance(latitude, longitude, location.latitude, location.longitude)
            is_valid = distance <= location.radius
            return is_valid, location, distance
        
        # 否则检查是否在任何一个公司位置范围内
        locations = CompanyLocation.objects.filter(is_active=True)
        for location in locations:
            distance = calculate_distance(latitude, longitude, location.latitude, location.longitude)
            if distance <= location.radius:
                return True, location, distance
        
        # 如果没有在任何位置范围内，返回最近的位置信息
        if locations.exists():
            nearest_location = None
            min_distance = float('inf')
            for location in locations:
                distance = calculate_distance(latitude, longitude, location.latitude, location.longitude)
                if distance < min_distance:
                    min_distance = distance
                    nearest_location = location
            return False, nearest_location, min_distance
        
        return False, None, None
        
    except CompanyLocation.DoesNotExist:
        return False, None, None


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AttendanceRecord.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AttendanceRecord.objects.all()
        elif user.is_manager:
            return AttendanceRecord.objects.filter(user__department=user.department)
        else:
            return AttendanceRecord.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_records(self, request):
        """获取当前用户的考勤记录"""
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', None)
        
        queryset = AttendanceRecord.objects.filter(user=user, clock_time__year=year)
        
        if month:
            queryset = queryset.filter(clock_time__month=month)
            
        queryset = queryset.order_by('-clock_time')
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })
    
    @action(detail=False, methods=['get'])
    def today_status(self, request):
        """获取今日考勤状态"""
        user = request.user
        today = timezone.now().date()
        
        # 获取今日的打卡记录
        today_records = AttendanceRecord.objects.filter(
            user=user,
            clock_time__date=today
        ).order_by('clock_time')
        
        clock_in_time = None
        clock_out_time = None
        work_hours = None
        is_late = False
        is_early_leave = False
        status_text = ''
        
        for record in today_records:
            if record.clock_type == 'in':
                clock_in_time = record.clock_time.isoformat()
                is_late = record.status == 'late'
                status_text = record.status
            elif record.clock_type == 'out':
                clock_out_time = record.clock_time.isoformat()
                is_early_leave = record.status == 'early'
                
                # 计算工作时长
                if clock_in_time:
                    clock_in_dt = datetime.fromisoformat(clock_in_time.replace('Z', '+00:00'))
                    clock_out_dt = record.clock_time
                    if clock_out_dt.tzinfo is None:                    clock_out_dt = timezone.make_aware(clock_out_dt)
                    work_hours = round((clock_out_dt - clock_in_dt).total_seconds() / 3600, 1)
        
        return Response({
            'clock_in_time': clock_in_time,
            'clock_out_time': clock_out_time,
            'work_hours': work_hours,
            'status': status_text or 'normal',
            'is_late': is_late,
            'is_early_leave': is_early_leave
        })
    
    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        """获取月度考勤统计"""
        user = request.user
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        # 构建时区感知的日期范围
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        
        # 使用时区感知的开始和结束时间
        start_datetime = timezone.make_aware(
            timezone.datetime(year, month, 1, 0, 0, 0)
        )
        end_datetime = timezone.make_aware(
            timezone.datetime(year, month, days_in_month, 23, 59, 59)
        )
        
        # 获取该月所有考勤记录 - 使用时间范围查询
        records = AttendanceRecord.objects.filter(
            user=user,
            clock_time__gte=start_datetime,
            clock_time__lte=end_datetime
        )
        
        # 统计数据
        work_days = 0
        late_days = 0
        early_leave_days = 0
        absent_days = 0
        total_hours = 0
        
        # 按日期分组统计
        daily_records = {}
        for record in records:
            # 使用本地时间的日期
            local_time = timezone.localtime(record.clock_time)
            date_str = str(local_time.date())
            if date_str not in daily_records:
                daily_records[date_str] = {'clock_in': None, 'clock_out': None, 'is_late': False, 'is_early': False}
            
            if record.clock_type == 'in':
                daily_records[date_str]['clock_in'] = record.clock_time
                if record.status == 'late':
                    daily_records[date_str]['is_late'] = True
            elif record.clock_type == 'out':
                daily_records[date_str]['clock_out'] = record.clock_time
                if record.status == 'early':
                    daily_records[date_str]['is_early'] = True
        
        # 计算统计数据
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, days_in_month).date()
        current_date = start_date
        while current_date <= end_date:
            # 跳过周末（假设周六日不上班）
            if current_date.weekday() < 5:  # 0-4 为周一到周五
                date_str = str(current_date)
                if date_str in daily_records:
                    day_record = daily_records[date_str]
                    work_days += 1
                    
                    if day_record['is_late']:
                        late_days += 1
                    if day_record['is_early']:
                        early_leave_days += 1
                    
                    # 计算工作时长
                    if day_record['clock_in'] and day_record['clock_out']:
                        work_time = (day_record['clock_out'] - day_record['clock_in']).total_seconds() / 3600
                        total_hours += work_time
                else:
                    # 工作日但没有打卡记录，算作缺勤
                    absent_days += 1
            
            current_date += timezone.timedelta(days=1)
        
        # 计算出勤率
        total_workdays = work_days + absent_days
        attendance_rate = round((work_days / total_workdays * 100), 1) if total_workdays > 0 else 0
        
        return Response({
            'work_days': work_days,
            'late_days': late_days,
            'early_leave_days': early_leave_days,
            'absent_days': absent_days,
            'total_hours': round(total_hours, 1),
            'attendance_rate': attendance_rate
        })


class WorkScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WorkSchedule.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return WorkSchedule.objects.all()
        elif user.is_manager:
            return WorkSchedule.objects.filter(user__department=user.department)
        else:
            return WorkSchedule.objects.filter(user=user)


class AttendanceExceptionViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceExceptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AttendanceException.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return AttendanceException.objects.all()
        elif user.is_manager:
            return AttendanceException.objects.filter(
                Q(user=user) | Q(user__department=user.department)
            )
        else:
            return AttendanceException.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批考勤异常"""
        exception = self.get_object()
        user = request.user
        
        if not (user.is_admin or user.is_manager):
            return Response({'error': '无权限审批'}, status=status.HTTP_403_FORBIDDEN)
        
        if exception.status != 'pending':
            return Response({'error': '该申请已处理'}, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = request.data.get('action')  # 'approve' or 'reject'
        approval_note = request.data.get('approval_note', '')
        
        if action_type == 'approve':
            exception.status = 'approved'
        elif action_type == 'reject':
            exception.status = 'rejected'
        else:
            return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        exception.approver = user
        exception.approval_note = approval_note
        exception.approved_at = timezone.now()
        exception.save()
        
        return Response({
            'message': f'申请已{exception.get_status_display()}',
            'exception': AttendanceExceptionSerializer(exception).data
        })


class ClockInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        now = timezone.now()
        # 使用本地时间的日期进行查询
        local_now = timezone.localtime(now)
        today = local_now.date()
        
        # 获取位置信息
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location_id = request.data.get('location_id')
        force_clock = request.data.get('force_clock', False)  # 是否强制打卡（忽略位置限制）
        
        # 位置验证（如果提供了位置信息）
        location_info = None
        distance = None
        if latitude and longitude:
            is_valid, location_info, distance = validate_attendance_location(
                float(latitude), float(longitude), location_id
            )
            
            # 如果位置验证失败且不是强制打卡，返回错误
            if not is_valid and not force_clock:
                return Response({
                    'error': '不在打卡范围内',
                    'location_required': True,
                    'current_distance': round(distance, 1) if distance else None,
                    'nearest_location': {
                        'name': location_info.name,
                        'address': location_info.address,
                        'radius': location_info.radius
                    } if location_info else None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用时间范围查询而不是 __date 查询
        from datetime import time
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
            location=location_info.name if location_info else request.data.get('location', ''),
            latitude=latitude,
            longitude=longitude,
            note=request.data.get('note', '')
        )
        
        serializer = AttendanceRecordSerializer(attendance_record)
        
        response_data = {
            'message': '上班打卡成功',
            'record': serializer.data
        }
        
        # 添加位置信息到响应
        if location_info:
            response_data['location_info'] = {
                'name': location_info.name,
                'address': location_info.address,
                'distance': round(distance, 1) if distance else None
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class ClockOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        now = timezone.now()
        # 使用本地时间的日期进行查询
        local_now = timezone.localtime(now)
        today = local_now.date()
        
        # 获取位置信息
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location_id = request.data.get('location_id')
        force_clock = request.data.get('force_clock', False)  # 是否强制打卡（忽略位置限制）
        
        # 位置验证（如果提供了位置信息）
        location_info = None
        distance = None
        if latitude and longitude:
            is_valid, location_info, distance = validate_attendance_location(
                float(latitude), float(longitude), location_id
            )
            
            # 如果位置验证失败且不是强制打卡，返回错误
            if not is_valid and not force_clock:
                return Response({
                    'error': '不在打卡范围内',
                    'location_required': True,
                    'current_distance': round(distance, 1) if distance else None,
                    'nearest_location': {
                        'name': location_info.name,
                        'address': location_info.address,
                        'radius': location_info.radius
                    } if location_info else None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用时间范围查询而不是 __date 查询
        from datetime import time
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
            location=location_info.name if location_info else request.data.get('location', ''),
            latitude=latitude,
            longitude=longitude,
            note=request.data.get('note', '')
        )
        
        serializer = AttendanceRecordSerializer(attendance_record)
        
        response_data = {
            'message': '下班打卡成功',
            'record': serializer.data
        }
        
        # 添加位置信息到响应
        if location_info:
            response_data['location_info'] = {
                'name': location_info.name,
                'address': location_info.address,
                'distance': round(distance, 1) if distance else None
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class AttendanceStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        year = int(request.query_params.get('year', timezone.now().year))
        month = request.query_params.get('month', None)
        employee_id = request.query_params.get('employee_id', None)
        
        # 权限检查
        if employee_id and not (user.is_admin or user.is_manager):
            return Response({'error': '无权限查看其他员工数据'}, status=status.HTTP_403_FORBIDDEN)
        
        # 确定查询的用户
        target_users = []
        if employee_id:
            try:
                target_user = User.objects.get(employee_id=employee_id)
                if user.is_manager and target_user.department != user.department:
                    return Response({'error': '无权限查看其他部门员工数据'}, status=status.HTTP_403_FORBIDDEN)
                target_users = [target_user]
            except User.DoesNotExist:
                return Response({'error': '员工不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if user.is_admin:
                target_users = User.objects.all()
            elif user.is_manager:
                target_users = User.objects.filter(department=user.department)
            else:
                target_users = [user]
        
        # 构建日期范围
        if month:
            from calendar import monthrange
            _, days_in_month = monthrange(year, int(month))
            start_date = timezone.datetime(year, int(month), 1).date()
            end_date = timezone.datetime(year, int(month), days_in_month).date()
        else:
            start_date = timezone.datetime(year, 1, 1).date()
            end_date = timezone.datetime(year, 12, 31).date()
        
        statistics = {}
        
        for target_user in target_users:
            # 构建日期范围内的所有日期
            daily_records = {}
            current_date = start_date
            while current_date <= end_date:
                daily_records[str(current_date)] = {
                    'date': str(current_date),
                    'weekday': current_date.strftime('%A'),
                    'clock_in': None,
                    'clock_out': None,
                    'status': 'absent',  # 默认为缺勤
                    'note': ''
                }
                current_date += timezone.timedelta(days=1)
            
            # 获取该用户在指定日期范围内的所有考勤记录
            records = AttendanceRecord.objects.filter(
                user=target_user,
                clock_time__date__range=(start_date, end_date)
            ).order_by('clock_time')
            
            # 处理考勤记录
            for record in records:
                date_str = str(record.clock_time.date())
                if date_str in daily_records:
                    if record.clock_type == 'in':
                        daily_records[date_str]['clock_in'] = record.clock_time.strftime('%H:%M:%S')
                        if record.status == 'late':
                            daily_records[date_str]['status'] = 'late'
                        elif daily_records[date_str]['status'] == 'absent':
                            daily_records[date_str]['status'] = 'normal'
                    else:  # clock_out
                        daily_records[date_str]['clock_out'] = record.clock_time.strftime('%H:%M:%S')
                        if record.status == 'early':
                            daily_records[date_str]['status'] = 'early'
                        elif daily_records[date_str]['status'] == 'absent':
                            daily_records[date_str]['status'] = 'normal'
                    
                    daily_records[date_str]['note'] = record.note
            
            # 统计汇总
            total_days = (end_date - start_date).days + 1
            attended_days = sum(1 for day in daily_records.values() if day['status'] != 'absent')
            late_days = sum(1 for day in daily_records.values() if day['status'] == 'late')
            early_days = sum(1 for day in daily_records.values() if day['status'] == 'early')
            absent_days = total_days - attended_days
            
            statistics[target_user.employee_id] = {
                'employee_id': target_user.employee_id,
                'name': f"{target_user.first_name} {target_user.last_name}" if target_user.first_name else target_user.username,
                'department': target_user.department.name if target_user.department else '',
                'position': target_user.position,
                'summary': {
                    'total_days': total_days,
                    'attended_days': attended_days,
                    'late_days': late_days,
                    'early_days': early_days,
                    'absent_days': absent_days
                },
                'daily_records': list(daily_records.values())
            }
        
        return Response({
            'statistics': statistics,
            'period': {
                'start_date': str(start_date),
                'end_date': str(end_date),
                'year': year,
                'month': month
            }
        })


class ClockView(APIView):
    """通用打卡视图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """打卡操作"""
        clock_type = request.data.get('clock_type', 'in')
        if clock_type == 'in':
            view = ClockInView()
            return view.post(request)
        elif clock_type == 'out':
            view = ClockOutView()
            return view.post(request)
        else:
            return Response({'error': '无效的打卡类型'}, status=status.HTTP_400_BAD_REQUEST)


class TodayStatusView(APIView):
    """今日考勤状态视图"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # 使用本地时间的日期进行查询
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()
        
        # 使用时间范围查询而不是 __date 查询
        from datetime import time
        start_of_day = timezone.make_aware(timezone.datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(timezone.datetime.combine(today, time.max))
        
        # 获取今日考勤记录
        today_records = AttendanceRecord.objects.filter(
            user=user,
            clock_time__gte=start_of_day,
            clock_time__lte=end_of_day
        ).order_by('clock_time')
        
        clock_in_time = None
        clock_out_time = None
        
        for record in today_records:
            if record.clock_type == 'in':
                clock_in_time = record.clock_time
            elif record.clock_type == 'out':
                clock_out_time = record.clock_time
        
        # 计算工作时长
        work_duration = None
        if clock_in_time and clock_out_time:
            work_duration = (clock_out_time - clock_in_time).total_seconds() / 3600  # 小时
        
        return Response({
            'has_clocked_in': clock_in_time is not None,
            'has_clocked_out': clock_out_time is not None,
            'clock_in_time': clock_in_time,
            'clock_out_time': clock_out_time,
            'work_duration': work_duration,
            'records_count': today_records.count()
        })


class MonthlyStatsView(APIView):
    """月度考勤统计视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
        
        # 构建月份的时间范围（使用时区感知的日期时间）
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        
        # 使用时区感知的开始和结束时间
        start_datetime = timezone.make_aware(
            timezone.datetime(year, month, 1, 0, 0, 0)
        )
        end_datetime = timezone.make_aware(
            timezone.datetime(year, month, days_in_month, 23, 59, 59)
        )
        
        # 获取月度考勤记录 - 使用时间范围查询而不是date__range
        monthly_records = AttendanceRecord.objects.filter(
            user=user,
            clock_time__gte=start_datetime,
            clock_time__lte=end_datetime
        )
        
        # 使用与ViewSet一致的统计逻辑
        work_days = 0
        late_days = 0
        early_leave_days = 0
        absent_days = 0
        total_hours = 0
        
        # 按日期分组统计
        daily_records = {}
        for record in monthly_records:
            # 使用本地时间的日期
            local_time = timezone.localtime(record.clock_time)
            date_str = str(local_time.date())
            if date_str not in daily_records:
                daily_records[date_str] = {'clock_in': None, 'clock_out': None, 'is_late': False, 'is_early': False}
            
            if record.clock_type == 'in':
                daily_records[date_str]['clock_in'] = record.clock_time
                if record.status == 'late':
                    daily_records[date_str]['is_late'] = True
            elif record.clock_type == 'out':
                daily_records[date_str]['clock_out'] = record.clock_time
                if record.status == 'early':
                    daily_records[date_str]['is_early'] = True
        
        # 计算统计数据（只统计工作日）
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, days_in_month).date()
        current_date = start_date
        
        while current_date <= end_date:
            # 跳过周末（假设周六日不上班）
            if current_date.weekday() < 5:  # 0-4 为周一到周五
                date_str = str(current_date)
                if date_str in daily_records:
                    day_record = daily_records[date_str]
                    work_days += 1
                    
                    if day_record['is_late']:
                        late_days += 1
                    if day_record['is_early']:
                        early_leave_days += 1
                    
                    # 计算工作时长
                    if day_record['clock_in'] and day_record['clock_out']:
                        work_time = (day_record['clock_out'] - day_record['clock_in']).total_seconds() / 3600
                        total_hours += work_time
                else:
                    # 工作日但没有打卡记录，算作缺勤
                    absent_days += 1
            
            current_date += timedelta(days=1)
          # 计算出勤率
        total_workdays = work_days + absent_days
        attendance_rate = round((work_days / total_workdays * 100), 1) if total_workdays > 0 else 0
        
        return Response({
            'year': year,
            'month': month,
            'work_days': work_days,
            'late_days': late_days,
            'early_leave_days': early_leave_days,
            'absent_days': absent_days,
            'total_hours': round(total_hours, 1),
            'attendance_rate': attendance_rate
        })


class MyRecordsView(APIView):
    """我的考勤记录视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        year = int(request.query_params.get('year', timezone.now().year))
        month = request.query_params.get('month', None)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        # 构建时间范围查询
        if month:
            month = int(month)
            # 使用日期范围而不是__month查询，以避免时区问题
            from calendar import monthrange
            _, days_in_month = monthrange(year, month)
            start_date = timezone.datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
            end_date = timezone.datetime(year, month, days_in_month, 23, 59, 59, 999999, tzinfo=timezone.get_current_timezone())
            queryset = AttendanceRecord.objects.filter(
                user=user,
                clock_time__gte=start_date,
                clock_time__lte=end_date
            )
        else:
            # 只过滤年份
            start_date = timezone.datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
            end_date = timezone.datetime(year, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.get_current_timezone())
            queryset = AttendanceRecord.objects.filter(
                user=user,
                clock_time__gte=start_date,
                clock_time__lte=end_date
            )
            
        # 按日期分组考勤记录
        from collections import defaultdict
        daily_records = defaultdict(lambda: {'clock_in': None, 'clock_out': None})
        
        for record in queryset:
            local_time = timezone.localtime(record.clock_time)
            date_str = local_time.date().isoformat()
            
            if record.clock_type == 'in':
                daily_records[date_str]['clock_in'] = record
            elif record.clock_type == 'out':
                daily_records[date_str]['clock_out'] = record
        
        # 转换为列表格式
        results = []
        for date_str, records in sorted(daily_records.items(), reverse=True):
            clock_in = records['clock_in']
            clock_out = records['clock_out']
            
            # 计算工作时长
            work_hours = None
            if clock_in and clock_out:
                duration = clock_out.clock_time - clock_in.clock_time
                work_hours = round(duration.total_seconds() / 3600, 2)
            
            # 判断状态
            status = 'normal'
            is_late = False
            is_early_leave = False
            is_absent = False
            
            if not clock_in and not clock_out:
                status = 'absent'
                is_absent = True
            elif clock_in and clock_in.status == 'late':
                is_late = True
                status = 'late'
            elif clock_out and clock_out.status == 'early':
                is_early_leave = True
                status = 'early'
            
            record_data = {
                'date': date_str,
                'clock_in_time': timezone.localtime(clock_in.clock_time).isoformat() if clock_in else None,
                'clock_out_time': timezone.localtime(clock_out.clock_time).isoformat() if clock_out else None,
                'work_hours': work_hours,
                'status': status,
                'is_late': is_late,
                'is_early_leave': is_early_leave,
                'is_absent': is_absent,
                'remarks': clock_in.note if clock_in else (clock_out.note if clock_out else '')
            }
            results.append(record_data)
        
        # 分页处理
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]
        
        return Response({
            'results': paginated_results,
            'count': len(results),
            'page': page,
            'page_size': page_size,
            'total_pages': (len(results) + page_size - 1) // page_size
        })
