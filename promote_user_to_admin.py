#!/usr/bin/env python
"""
提升用户为管理员的脚本
用法: python promote_user_to_admin.py <username>
或: python promote_user_to_admin.py <username> --superuser
"""

import os
import sys
import django

# 设置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_backend.settings')
django.setup()

from users.models import User


def promote_user(username, make_superuser=False):
    """提升用户为管理员"""
    try:
        user = User.objects.get(username=username)
        
        # 设置为管理员类型
        user.user_type = 'admin'
        if make_superuser:
            user.is_superuser = True
            user.is_staff = True
        
        user.save()
        
        print(f"✓ 用户 '{username}' 已提升为管理员")
        print(f"  - user_type: {user.user_type}")
        print(f"  - is_superuser: {user.is_superuser}")
        print(f"  - is_staff: {user.is_staff}")
        return True
        
    except User.DoesNotExist:
        print(f"✗ 用户 '{username}' 不存在")
        return False
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False


def list_users():
    """列出所有用户"""
    users = User.objects.all().values('id', 'username', 'user_type', 'is_superuser', 'is_staff')
    
    if not users:
        print("暂无用户")
        return
    
    print("已有用户:")
    print("-" * 80)
    print(f"{'ID':<5} {'用户名':<20} {'用户类型':<15} {'超级用户':<10} {'员工':<10}")
    print("-" * 80)
    
    for user in users:
        print(f"{user['id']:<5} {user['username']:<20} {user['user_type']:<15} {str(user['is_superuser']):<10} {str(user['is_staff']):<10}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python promote_user_to_admin.py <username>        # 设置为管理员用户类型")
        print("  python promote_user_to_admin.py <username> --superuser  # 同时设置为超级用户")
        print("  python promote_user_to_admin.py --list            # 列出所有用户")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_users()
    else:
        username = sys.argv[1]
        make_superuser = '--superuser' in sys.argv
        promote_user(username, make_superuser)
