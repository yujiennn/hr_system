# 智慧员工运营系统 (HR Smart Operation System)

## 📋 项目概述

**智慧员工运营系统**是一个现代化的企业人力资源管理解决方案，基于 **B/S 三层架构** 的 Web 应用。系统采用浏览器-服务器-数据库架构模式，统一了客户端操作界面，将核心功能实现集中在服务器端，简化了系统的开发、维护和使用。

### ✨ 核心特性

- 🔐 **多角色权限管理**：管理员、部门经理、普通员工三级权限体系
- 👤 **人脸识别打卡**：通过人脸识别和 GPS 定位确保考勤真实性
- 📍 **智能定位验证**：基于 GPS 和 Haversine 算法的位置范围检查
- 📊 **完整薪资管理**：薪资计算、Excel 导出、多维度统计
- 📅 **灵活请假流程**：申请-审批-记录完整流程，自动余额管理
- 📈 **绩效评估体系**：目标管理、绩效评估、数据统计分析
- 📱 **响应式界面**：现代化的 Vue3 UI，完整的数据可视化

---

## 🛠 技术栈

### 后端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Django | 5.1.5 | 轻量级 Web 框架，企业级应用开发 |
| Django REST Framework | 3.15.2 | RESTful API 开发框架 |
| djangorestframework-simplejwt | 5.3.0 | JWT 用户认证与授权 |
| MySQL | - | 关系型数据库，数据持久化存储 |
| Pillow | 10.2.0 | 图像处理库（头像、人脸图片） |
| face-recognition | 1.3.0 | 人脸识别和特征提取 |
| openpyxl | 3.1.2 | Excel 文件生成和操作 |

### 前端技术
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.13 | 渐进式 JavaScript 框架 |
| TypeScript | 5.8.0 | 类型化 JavaScript 超集 |
| Vite | 6.3.5 | 现代化前端构建工具 |
| Element Plus | 2.9.11 | Vue 3 UI 组件库 |
| Pinia | 3.0.1 | 轻量化状态管理方案 |
| ECharts | 5.6.0 | 数据可视化图表库 |
| Axios | 1.9.0 | HTTP 请求客户端 |

### 架构模式
- **后端**：MVC 设计模式，Django App 模块化结构
- **前端**：MVVM 架构，Vue 组件化开发
- **认证**：JWT Token 认证，支持 Token 自动刷新
- **API**：RESTful 设计，统一的 JSON 响应格式

---

## 📦 项目结构

```
hr_system/
├── hr_backend/              # Django 主项目配置
│   ├── settings.py          # 项目设置（数据库、中间件、应用注册）
│   ├── urls.py              # 主 URL 路由分配
│   └── wsgi.py/asgi.py      # WSGI/ASGI 应用入口
│
├── users/                   # 用户管理应用
│   ├── models.py            # 用户模型（继承 AbstractUser）
│   ├── views.py             # 用户 API 视图
│   ├── face_views.py        # 人脸识别视图
│   ├── serializers.py       # 数据序列化器
│   └── urls.py              # 路由配置
│
├── attendance/              # 考勤管理应用
│   ├── models.py            # 打卡记录、工作时间表、异常记录
│   ├── views.py             # 考勤 API 视图
│   ├── serializers.py       # 序列化器
│   └── urls.py              # 路由配置
│
├── leave/                   # 请假管理应用
│   ├── models.py            # 请假申请、审批记录
│   ├── views.py             # 请假 API 视图
│   └── serializers.py       # 序列化器
│
├── salary/                  # 薪资管理应用
│   ├── models.py            # 薪资记录、薪资项目配置
│   ├── views.py             # 薪资计算、查询、导出功能
│   └── serializers.py       # 序列化器
│
├── performance/             # 绩效管理应用
│   ├── models.py            # 绩效评估、目标管理
│   ├── views.py             # 绩效 API 视图
│   └── serializers.py       # 序列化器
│
├── reports/                 # 报告统计应用
│   ├── models.py            # 报告数据模型
│   ├── views.py             # 报告生成和查询
│   └── serializers.py       # 序列化器
│
├── system_config/           # 系统配置应用
│   ├── models.py            # 公司位置、部门、系统参数
│   ├── views.py             # 配置管理 API
│   └── serializers.py       # 序列化器
│
├── frontend/                # Vue 3 前端项目
│   ├── src/
│   │   ├── views/           # 页面组件（登录、考勤、薪资等）
│   │   ├── components/      # 可复用组件
│   │   ├── services/        # API 服务调用（axios）
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # 路由配置和守卫
│   │   └── App.vue          # 根组件
│   ├── public/              # 静态资源
│   └── vite.config.ts       # Vite 构建配置
│
├── media/                   # 媒体文件存储
│   ├── avatars/             # 用户头像
│   ├── face_images/         # 人脸注册图片
│   └── logos/               # 企业 Logo
│
├── requirements.txt         # Python 依赖包列表
└── manage.py               # Django 管理脚本
```

---

## 🔄 系统架构

### 三层架构设计

```
┌─────────────────────────────────────────────────┐
│            表现层 (Presentation Layer)            │
│  Vue 3 + TypeScript + Element Plus              │
│  浏览器端响应式用户界面                           │
├─────────────────────────────────────────────────┤
│            业务层 (Business Logic Layer)          │
│  Django REST Framework RESTful API              │
│  JWT 认证、权限控制、业务逻辑处理                │
├─────────────────────────────────────────────────┤
│            数据层 (Data Access Layer)            │
│  MySQL 数据库 + Django ORM                      │
│  数据持久化、事务管理                            │
└─────────────────────────────────────────────────┘
```

### 数据流向

1. **前端请求** → 用户通过 Vue 组件操作，调用 API 服务（axios）
2. **API 路由** → 请求通过 Django URL 路由到对应 ViewSet
3. **业务处理** → ViewSet 验证权限，调用 Serializer 和 Model
4. **数据库操作** → Django ORM 执行 SQL 查询/修改
5. **响应返回** → JSON 数据返回前端，Pinia Store 更新状态，Vue 组件重新渲染

---

## 🚀 核心功能模块

### 1️⃣ 用户管理 (`users`)
- 用户注册、登录、认证
- 三角色权限管理（员工、经理、管理员）
- **人脸识别**：人脸特征提取和注册、实时人脸识别验证
- 用户信息编辑、头像上传

### 2️⃣ 考勤管理 (`attendance`)
- **打卡流程**：人脸识别验证 + GPS 定位检查 → 生成打卡记录
- **位置验证**：Haversine 距离公式计算，支持多公司位置范围
- 工作时间表配置
- 考勤异常记录和处理
- **权限隔离**：员工看自己、经理看部门、管理员看全部

### 3️⃣ 请假管理 (`leave`)
- 请假申请（多种类型：年假、事假、病假等）
- 部门经理审批工作流
- 假期余额自动扣除
- 请假记录统计和查询

### 4️⃣ 薪资管理 (`salary`)
- 薪资项目配置（基本工资、津贴、扣税等）
- 薪资自动计算
- 薪资单查询和 **Excel 导出**（含格式化）
- **权限细粒度控制**：
  - 普通员工：查看自己薪资
  - 部门经理：查看部门薪资
  - 管理员：全局薪资管理

### 5️⃣ 绩效管理 (`performance`)
- 绩效目标制定和跟踪
- 员工绩效评估
- 绩效数据统计和分析

### 6️⃣ 报告统计 (`reports`)
- 考勤报表：出勤率、迟到早退统计
- 请假报表：按部门、按员工统计
- 薪资报表：部门工资总额、平均工资
- 自定义报告生成

### 7️⃣ 系统配置 (`system_config`)
- 公司位置管理（GPS 范围设置）
- 部门管理
- 员工工作时间表配置
- 系统参数设置

---

## 🔑 关键业务流程

### 考勤打卡流程
```
用户上传人脸图片 + GPS 坐标
    ↓
人脸特征提取 & 与注册特征对比（欧几里得距离）
    ↓
Haversine 算法计算 GPS 距离 & 检查范围
    ↓
生成 AttendanceRecord & 返回打卡结果
```

### 请假审批流程
```
员工提交请假申请
    ↓
部门经理审批
    ↓
系统自动扣除相应假期余额
    ↓
记录假期使用情况
```

### 薪资计算流程
```
配置基本工资 + 津贴 + 扣税项
    ↓
读取考勤记录（计算加班、迟到扣款）
    ↓
自动计算应发工资和实发工资
    ↓
生成薪资单、支持 Excel 导出
```

---

## 🔐 安全与权限

### JWT 认证流程
- 登录成功返回 `access_token` 和 `refresh_token`
- 每个 API 请求自动在 Header 中带 `Authorization: Bearer {token}`
- Token 过期时自动调用刷新接口更新
- 无效 Token / 过期无法刷新 → 重定向到登录页

### 权限控制策略
- **ViewSet 级别**：`permission_classes = [permissions.IsAuthenticated]`
- **QuerySet 级别**：`get_queryset()` 中根据 `user.user_type` 和 `department` 过滤数据
- **业务逻辑级别**：`perform_create()`, `perform_update()` 中复杂权限检查
- **路由守卫**：前端路由 `meta.requiresAuth` 和 `meta.role` 验证

---

## 📝 快速开始

### 前置要求
- Python 3.9+
- Node.js 16+
- MySQL 5.7+ 或 8.0+
- Git

### 后端启动

```bash
# 克隆项目
git clone https://github.com/yujiennn/hr_system.git
cd hr_system

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
.\venv\Scripts\Activate.ps1
# 或 macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库（修改 hr_backend/settings.py 中的 DATABASES）
# 使用默认 SQLite 或配置 MySQL

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
# 访问 http://127.0.0.1:8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://127.0.0.1:5173
# Vite 自动代理 /api → http://127.0.0.1:8000
```

### 测试账户
- **管理员**：admin / admin123
- **部门经理**：manager / manager123
- **普通员工**：employee / employee123

---

## 🎯 主要 API 端点

### 认证 & 用户
- `POST /api/users/token/` - 用户登录
- `POST /api/users/token/refresh/` - 刷新 Token
- `GET /api/users/profile/` - 获取当前用户信息
- `POST /api/users/face/register/` - 人脸注册
- `POST /api/users/face/recognize/` - 人脸验证

### 考勤
- `POST /api/attendance/records/` - 打卡
- `GET /api/attendance/records/` - 查询打卡记录
- `GET /api/attendance/work-schedules/` - 工作时间表

### 请假
- `POST /api/leave/requests/` - 申请请假
- `GET /api/leave/requests/` - 查询请假记录
- `POST /api/leave/requests/{id}/approve/` - 审批请假

### 薪资
- `GET /api/salary/records/` - 查询薪资
- `GET /api/salary/records/{id}/export-salary-slip/` - 导出工资单

### 绩效
- `GET /api/performance/evaluations/` - 查询绩效评估
- `POST /api/performance/evaluations/` - 创建评估

---

## 📊 数据库设计亮点

- **用户管理**：继承 Django AbstractUser，支持灵活的用户扩展
- **多部门支持**：递归外键支持跨部门业务逻辑
- **时间戳自动化**：created_at、updated_at 自动记录
- **考勤关联**：WorkSchedule 与 User 多对一，支持灵活的工作时间配置
- **人脸特征存储**：通过 JSON 字段存储 128 维特征向量

---

## 🐛 已知问题与改进项

1. **User 模型**：`emergency_phone` 字段有重复定义，待清理
2. **多版本共存**：某些 app 有 `views.py` 和 `views_new.py` 两个版本，表示重构进行中
3. **未来优化**：支持扫码打卡、移动端适配、深度学习人脸识别优化

---

## 📄 许可证

本项目为毕业设计项目，供学习参考使用。

---

## 👤 作者

俞杰

**最后更新**：2026 年 4 月 3 日
