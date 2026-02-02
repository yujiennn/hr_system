#!/usr/bin/env python
"""查看所有用户"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_backend.settings')
sys.path.insert(0, r'd:\pro_study_pycharm\毕设')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("数据库中的所有用户:")
print("=" * 80)

for user in User.objects.all().order_by('id'):
    print(f"ID: {user.id:2d} | 用户名: {user.username:20s} | 姓名: {user.get_full_name():20s} | 部门: {user.department}")
