# 省队青训营训练档案平台 API 接口文档

> Base URL: `/api`  
> 统一响应格式: `{ "code": 0, "data": ..., "message": "success" }`  
> 错误响应: `{ "code": 1, "data": null, "message": "错误描述" }`

---

## 1. 认证模块 `/api/auth`

### POST `/api/auth/login` 用户登录

**请求体:**
```json
{
  "username": "coach01",
  "password": "123456"
}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  },
  "message": "登录成功"
}
```

### POST `/api/auth/register` 用户注册

**请求体:**
```json
{
  "username": "coach01",
  "password": "123456",
  "role": "coach",
  "name": "张教练",
  "phone": "13800000001",
  "specialty": "短跑",
  "kinship": null
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，唯一 |
| password | string | 是 | 密码 |
| role | string | 是 | `coach` 或 `parent` |
| name | string | 是 | 真实姓名 |
| phone | string | 否 | 手机号 |
| specialty | string | 否 | 教练专长（role=coach时） |
| kinship | string | 否 | 与学员关系（role=parent时） |

**响应:** 返回用户信息

### GET `/api/auth/me` 获取当前用户

**请求头:** `Authorization: Bearer <token>`

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "coach01",
    "role": "coach",
    "name": "张教练",
    "phone": "13800000001"
  },
  "message": "success"
}
```

---

## 2. 学员模块 `/api/students`

### GET `/api/students` 学员列表

**权限:** 教练看到自己负责的学员；家长只看到自己的孩子

**响应:**
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "李明",
      "gender": "男",
      "birth_date": "2012-03-15",
      "group_name": "U12",
      "enrollment_year": 2024,
      "parent_id": 1,
      "status": "active",
      "created_at": "2024-09-01T08:00:00"
    }
  ],
  "message": "success"
}
```

### GET `/api/students/{student_id}` 学员详情

**响应:** 同上 + 附带家长信息和负责教练列表

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "李明",
    "gender": "男",
    "birth_date": "2012-03-15",
    "group_name": "U12",
    "enrollment_year": 2024,
    "status": "active",
    "parent_name": "李父",
    "parent_phone": "13900000001",
    "parent_relationship": "父亲",
    "coaches": [
      {
        "coach_id": 1,
        "name": "张教练",
        "specialty": "短跑",
        "year": 2024,
        "is_primary": true
      }
    ]
  }
}
```

### POST `/api/students` 创建学员

**权限:** 仅教练

**请求体:**
```json
{
  "name": "李明",
  "gender": "男",
  "birth_date": "2012-03-15",
  "group_name": "U12",
  "enrollment_year": 2024,
  "parent_user_id": 5
}
```

### PUT `/api/students/{student_id}` 更新学员

**权限:** 仅教练，且只能更新自己负责的学员

**请求体:** 同创建

---

## 3. 训练记录模块 `/api/training`

### POST `/api/training` 录入/更新训练记录

**权限:** 仅教练，且只能为分配给自己的学员录入

**请求体:**
```json
{
  "student_id": 1,
  "week_number": 12,
  "year": 2024,
  "technique_score": 85.5,
  "fitness_score": 78.0,
  "match_score": 90.0,
  "notes": "本周技术进步明显"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | int | 是 | 学员ID |
| week_number | int | 是 | 训练周数 |
| year | int | 是 | 年份 |
| technique_score | float | 是 | 技术项评分 (0-100) |
| fitness_score | float | 是 | 体能项评分 (0-100) |
| match_score | float | 是 | 对抗赛成绩 (0-100) |
| notes | string | 否 | 备注 |

> 若 (student_id, week_number, year) 已存在则更新，否则新建

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "student_id": 1,
    "coach_id": 1,
    "week_number": 12,
    "year": 2024,
    "technique_score": 85.5,
    "fitness_score": 78.0,
    "match_score": 90.0,
    "notes": "本周技术进步明显",
    "created_at": "2024-09-01T08:00:00",
    "updated_at": "2024-09-01T08:00:00"
  },
  "message": "训练记录创建成功"
}
```

### GET `/api/training/student/{student_id}` 查询学员训练记录

**查询参数:** `year` (可选，按年份筛选)

### GET `/api/training/{record_id}` 查询单条训练记录

---

## 4. 体测评估模块 `/api/assessments`

### POST `/api/assessments` 录入/更新体测数据

**权限:** 仅教练

**请求体:**
```json
{
  "student_id": 1,
  "week_number": 12,
  "year": 2024,
  "speed_score": 88.0,
  "strength_score": 75.5,
  "endurance_score": 82.0,
  "agility_score": 90.0,
  "flexibility_score": 70.0
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| speed_score | float | 速度标准分 |
| strength_score | float | 力量标准分 |
| endurance_score | float | 耐力标准分 |
| agility_score | float | 敏捷标准分 |
| flexibility_score | float | 柔韧标准分 |

> total_score 由后端自动计算（五项均值）

### GET `/api/assessments/student/{student_id}` 查询学员体测记录

**查询参数:** `year` (可选)

### GET `/api/assessments/growth-curve/{student_id}` 获取成长曲线数据

**响应:**
```json
{
  "code": 0,
  "data": {
    "student_id": 1,
    "student_name": "李明",
    "points": [
      {
        "week_number": 1,
        "year": 2024,
        "total_score": 78.2,
        "speed_score": 80.0,
        "strength_score": 72.0,
        "endurance_score": 78.0,
        "agility_score": 85.0,
        "flexibility_score": 76.0
      },
      {
        "week_number": 2,
        "year": 2024,
        "total_score": 80.4,
        "speed_score": 82.0,
        "strength_score": 74.0,
        "endurance_score": 80.0,
        "agility_score": 88.0,
        "flexibility_score": 78.0
      }
    ]
  }
}
```

> 横轴: week_number，纵轴: 各指标标准分，用于前端绘制成长曲线折线图

### POST `/api/assessments/archive/{year}` 按年份归档数据

**权限:** 仅教练

> 将指定年份的学员数据快照存入 archived_students 表（JSONB），学员状态改为 archived

**响应:**
```json
{
  "code": 0,
  "data": {
    "archived_count": 40,
    "year": 2023
  },
  "message": "归档完成"
}
```

---

## 5. 月度评语模块 `/api/comments`

### POST `/api/comments` 创建月度评语

**权限:** 仅教练

**请求体:**
```json
{
  "student_id": 1,
  "month": 10,
  "year": 2024,
  "content": "本月训练态度积极，技术有进步..."
}
```

> 同一教练对同一学员同月只能创建一条评语，重复提交返回 409

### PUT `/api/comments/{comment_id}` 更新评语（含冲突检测）

**权限:** 仅教练，只能修改自己的评语

**请求体:**
```json
{
  "content": "更新后的评语内容...",
  "version": 2,
  "force": false
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| content | string | 评语内容 |
| version | int | 客户端持有的版本号（乐观锁） |
| force | bool | 是否强制覆盖（默认 false） |

**冲突检测逻辑:**
- 若 `force=false` 且 `version != 数据库当前version`，返回 409:

```json
{
  "detail": {
    "code": 1,
    "data": {
      "current_version": 3,
      "current_content": "其他教练已更新的内容...",
      "your_version": 2,
      "your_content": "你提交的内容..."
    },
    "message": "版本冲突，数据已被其他人修改"
  }
}
```

- 客户端收到冲突后可选择:
  - **覆盖:** 重新提交 `force=true`
  - **合并:** 手动合并内容后重新提交

### GET `/api/comments/student/{student_id}` 查询学员评语

**查询参数:** `year` (可选)

### DELETE `/api/comments/{comment_id}` 删除评语

**权限:** 仅教练，只能删除自己的评语

---

## 6. 晋升建议模块 `/api/promotions`

### POST `/api/promotions/generate/{year}/{quarter}` 自动生成晋升建议

**权限:** 仅教练

**逻辑:**
1. 获取教练负责的所有学员
2. 计算该季度体测平均总分
3. 按总分降序排列
4. 前 30% 标记为 `auto_suggested=true, status=suggested`
5. 其余标记为 `auto_suggested=false, status=not_recommended`

**路径参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| year | int | 年份 |
| quarter | int | 季度 (1-4) |

**响应:** 返回所有学员的晋升建议列表

### GET `/api/promotions/{year}/{quarter}` 查询季度晋升建议

### PUT `/api/promotions/{suggestion_id}/confirm` 教练确认/修改晋升建议

**请求体:**
```json
{
  "status": "confirmed",
  "notes": "教练补充说明"
}
```

| status 值 | 说明 |
|-----------|------|
| suggested | 建议（默认） |
| confirmed | 确认晋升 |
| rejected | 拒绝晋升 |

### GET `/api/promotions/student/{student_id}` 查询学员晋升历史

---

## 7. 数据库表结构

### users 用户表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| role | VARCHAR(20) | NOT NULL | 角色: coach/parent |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| phone | VARCHAR(20) | DEFAULT '' | 手机号 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### coaches 教练表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| user_id | INTEGER | FK→users, UNIQUE | 关联用户 |
| specialty | VARCHAR(100) | DEFAULT '' | 专长 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### parents 家长表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| user_id | INTEGER | FK→users, UNIQUE | 关联用户 |
| kinship | VARCHAR(20) | DEFAULT '家长' | 与学员关系 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### students 学员表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| gender | VARCHAR(10) | NOT NULL | 性别 |
| birth_date | DATE | NOT NULL | 出生日期 |
| group_name | VARCHAR(50) | DEFAULT '' | 组别 |
| enrollment_year | INTEGER | NOT NULL | 入营年份 |
| parent_id | INTEGER | FK→parents | 关联家长 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态: active/archived |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### coach_students 教练-学员关联表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| coach_id | INTEGER | FK→coaches | 教练ID |
| student_id | INTEGER | FK→students | 学员ID |
| year | INTEGER | NOT NULL | 年份 |
| is_primary | BOOLEAN | DEFAULT FALSE | 是否主带教练 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### training_records 训练记录表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| student_id | INTEGER | FK→students | 学员ID |
| coach_id | INTEGER | FK→coaches | 教练ID |
| week_number | INTEGER | NOT NULL | 训练周数 |
| year | INTEGER | NOT NULL | 年份 |
| technique_score | FLOAT | DEFAULT 0 | 技术评分 |
| fitness_score | FLOAT | DEFAULT 0 | 体能评分 |
| match_score | FLOAT | DEFAULT 0 | 比赛评分 |
| notes | TEXT | DEFAULT '' | 备注 |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

> UNIQUE(student_id, week_number, year)

### physical_assessments 体测评估表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| student_id | INTEGER | FK→students | 学员ID |
| week_number | INTEGER | NOT NULL | 训练周数 |
| year | INTEGER | NOT NULL | 年份 |
| speed_score | FLOAT | DEFAULT 0 | 速度标准分 |
| strength_score | FLOAT | DEFAULT 0 | 力量标准分 |
| endurance_score | FLOAT | DEFAULT 0 | 耐力标准分 |
| agility_score | FLOAT | DEFAULT 0 | 敏捷标准分 |
| flexibility_score | FLOAT | DEFAULT 0 | 柔韧标准分 |
| total_score | FLOAT | DEFAULT 0 | 综合得分(五项均值) |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

> UNIQUE(student_id, week_number, year)

### monthly_comments 月度评语表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| student_id | INTEGER | FK→students | 学员ID |
| coach_id | INTEGER | FK→coaches | 教练ID |
| month | INTEGER | NOT NULL | 月份(1-12) |
| year | INTEGER | NOT NULL | 年份 |
| content | TEXT | DEFAULT '' | 评语内容 |
| version | INTEGER | DEFAULT 1 | 乐观锁版本号 |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

> UNIQUE(student_id, coach_id, month, year)

### promotion_suggestions 晋升建议表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| student_id | INTEGER | FK→students | 学员ID |
| coach_id | INTEGER | FK→coaches | 教练ID |
| quarter | INTEGER | NOT NULL | 季度(1-4) |
| year | INTEGER | NOT NULL | 年份 |
| rank_percentage | FLOAT | DEFAULT 0 | 排名百分位 |
| auto_suggested | BOOLEAN | DEFAULT TRUE | 是否自动推荐 |
| status | VARCHAR(20) | DEFAULT 'suggested' | suggested/confirmed/rejected |
| notes | TEXT | DEFAULT '' | 备注 |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

### archived_students 归档学员表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| original_student_id | INTEGER | NOT NULL | 原学员ID |
| archive_year | INTEGER | NOT NULL | 归档年份 |
| snapshot_data | JSONB | NOT NULL | 快照数据(含体测/训练等) |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

## 8. Vue 页面与组件清单

### 页面 (Views)
| 页面 | 路由 | 角色 | 说明 |
|------|------|------|------|
| LoginPage | /login | 全部 | 登录表单 |
| DashboardPage | /dashboard | 全部 | 仪表盘(教练/家长不同视图) |
| StudentListPage | /students | 教练 | 学员列表+搜索+新增 |
| StudentDetailPage | /students/:id | 全部 | 学员详情(训练/体测/评语/晋升Tab) |
| TrainingPage | /training | 教练 | 周训练录入+历史记录 |
| AssessmentPage | /assessments | 教练 | 体测录入+自动计算总分 |
| CommentPage | /comments | 全部 | 月度评语管理+冲突检测 |
| GrowthCurvePage | /growth-curve/:studentId | 全部 | ECharts成长曲线图 |
| PromotionPage | /promotions | 教练 | 季度晋升建议管理 |

### 组件 (Components)
| 组件 | 说明 |
|------|------|
| AppHeader | 顶部导航栏(Logo+菜单+用户信息) |
| StudentFormDialog | 学员新增/编辑弹窗 |
| CommentConflictDialog | 评语冲突对话框(覆盖/合并) |
| GrowthChart | vue-echarts成长曲线折线图 |

---

## 9. 认证与权限

所有需认证接口需在请求头携带:
```
Authorization: Bearer <access_token>
```

### 角色权限矩阵
| 功能 | 教练(coach) | 家长(parent) |
|------|:-----------:|:------------:|
| 查看分配学员 | ✅ | ❌ |
| 查看自己孩子 | ❌ | ✅ |
| 创建/编辑学员 | ✅ | ❌ |
| 录入训练记录 | ✅ | ❌ |
| 录入体测数据 | ✅ | ❌ |
| 撰写/编辑评语 | ✅ | ❌ |
| 查看评语 | ✅(分配学员) | ✅(自己孩子) |
| 生成晋升建议 | ✅ | ❌ |
| 确认/修改晋升 | ✅ | ❌ |
| 查看成长曲线 | ✅(分配学员) | ✅(自己孩子) |
| 归档历史数据 | ✅ | ❌ |
