#!/usr/bin/env python
"""
完整的前后端对接测试
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_backend.settings')
django.setup()

from rest_framework.test import APIClient
from users.models import User
from performance.models import PerformanceEvaluation
import json

print("=" * 70)
print("HR系统 - 绩效评估完整诊断报告")
print("=" * 70)

# 1. 数据库检查
print("\n📊 1. 数据库数据检查")
print("-" * 70)
caiwu3 = User.objects.filter(username='财务3').first()
if not caiwu3:
    print("❌ 找不到财务3用户")
    exit(1)

print(f"✅ 用户: {caiwu3.username} (ID: {caiwu3.id}, 部门: {caiwu3.department})")

evaluations = PerformanceEvaluation.objects.filter(goal__user=caiwu3).order_by('-updated_at')
print(f"✅ 绩效评估数: {evaluations.count()}")

for eval in evaluations:
    print(f"   └─ ID={eval.id}, 状态={eval.status}, 期次={eval.goal.period.name}, 最终分={eval.final_score}")

# 2. 后端API检查
print("\n🔌 2. 后端API检查")
print("-" * 70)

client = APIClient()
client.force_authenticate(user=caiwu3)

# 调用API
response = client.get('/api/performance/evaluations/my_evaluations/')
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.data
    print(f"✅ 返回记录数: {len(data)}")
    
    # 逐条检查
    for i, eval_data in enumerate(data, 1):
        print(f"\n   记录{i}:")
        print(f"   ├─ ID: {eval_data.get('id')}")
        print(f"   ├─ 期次: {eval_data.get('period_name')}")
        print(f"   ├─ 状态: {eval_data.get('status')}")
        print(f"   ├─ 自评分: {eval_data.get('self_evaluation_score')}")
        print(f"   ├─ 最终分: {eval_data.get('final_score')}")
        print(f"   └─ 更新时间: {eval_data.get('updated_at')}")
        
        # 检查关键字段是否存在
        required_fields = ['id', 'goal', 'status', 'final_score', 'final_rating', 'period_name', 'template_name']
        missing = [f for f in required_fields if f not in eval_data or eval_data[f] is None]
        if missing:
            print(f"   ⚠️ 缺失字段: {missing}")
else:
    print(f"❌ API错误: {response.data}")
    exit(1)

# 3. 前端数据绑定检查
print("\n📝 3. 前端数据格式检查")
print("-" * 70)
if response.data:
    sample = response.data[0]
    print("样本数据结构:")
    print(json.dumps(sample, indent=2, ensure_ascii=False, default=str)[:500] + "...")
    
    # 检查表格需要的字段
    table_fields = {
        'period_name': '评估周期',
        'template_name': '评估模板',
        'final_score': '最终得分',
        'final_rating': '等级',
        'status': '状态',
        'evaluator_name': '评估人',
        'updated_at': '更新时间'
    }
    
    print("\n表格字段检查:")
    all_ok = True
    for field, label in table_fields.items():
        if field in sample and sample[field] is not None:
            print(f"✅ {label:12} ({field:20}): {sample[field]}")
        else:
            print(f"❌ {label:12} ({field:20}): 缺失或为空")
            all_ok = False
    
    if all_ok:
        print("\n✅ 所有字段完整，前端表格应该能正常显示数据")
    else:
        print("\n⚠️ 有些字段缺失，可能导致表格显示不完整")

# 4. 诊断总结
print("\n" + "=" * 70)
print("诊断结论")
print("=" * 70)

if evaluations.count() > 0 and len(response.data) > 0:
    print("✅ 数据完整：")
    print("   • 数据库中有绩效评估数据")
    print("   • 后端API成功返回数据")
    print("   • 前端应该能显示数据")
    print("\n可能的问题：")
    print("   1. 前端缓存问题 - 清除浏览器缓存")
    print("   2. 前端代码问题 - 检查loadEvaluations()方法")
    print("   3. 前端样式问题 - 检查table是否被隐藏")
    print("   4. 路由权限问题 - 检查用户是否真的登录成功")
else:
    print("❌ 数据不完整：")
    print(f"   • 数据库评估数: {evaluations.count()}")
    print(f"   • API返回数: {len(response.data) if response.status_code == 200 else '错误'}")

print("\n" + "=" * 70)
print("建议操作：")
print("=" * 70)
print("1. 打开浏览器 F12 控制台")
print("2. 登录为财务3")
print("3. 导航到绩效查询页面")
print("4. 查看Console标签页的日志输出")
print("5. 查看Network标签页的 /api/performance/evaluations/my_evaluations/ 请求")
print("=" * 70)
