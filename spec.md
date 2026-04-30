# 校园二手物品交易平台 — 技术规范 (Specification)

> **选题**: 基于 Python Flask 的校园二手物品交易平台的设计与实现
> **版本**: v1.0
> **最后更新**: 2026-04-30

---

## 1. 技术栈 (Tech Stack)

| 层级 | 技术选型 | 版本 | 选型理由 |
|------|----------|------|----------|
| **语言** | Python | 3.11+ | Flask 生态原生语言，开发效率高，第三方库丰富 |
| **Web 框架** | Flask | 3.0+ | 毕业论文选题核心，轻量灵活，适合中小型项目 |
| **ORM** | Flask-SQLAlchemy | 3.1+ | Flask 生态事实标准，支持多数据库，迁移方便 |
| **数据库** | MySQL | 8.0+ | 关系型数据，事务支持完善，校园场景数据量可控 |
| **数据库迁移** | Flask-Migrate (Alembic) | 4.0+ | 版本化 schema 管理，团队协作必备 |
| **模板引擎** | Jinja2 | 3.1+ | Flask 内置，服务端渲染，学习曲线低 |
| **前端 UI** | Bootstrap | 5.3+ | 响应式布局，组件丰富，文档完善 |
| **前端交互** | Vanilla JS + htmx | — | 轻量 AJAX 交互，避免引入重框架 |
| **表单处理** | Flask-WTF / WTForms | 1.2+ | 服务端验证 + CSRF 保护，与 Flask 深度整合 |
| **用户认证** | Flask-Login | 0.6+ | Session 管理标准方案 |
| **密码哈希** | Werkzeug Security | built-in | Flask 内置，bcrypt/scrypt 算法 |
| **文件上传** | Werkzeug + Pillow | — | 图片上传、缩略图生成 |
| **测试** | pytest + pytest-flask | 8.0+ | Python 测试首选框架 |
| **代码质量** | Ruff (lint) + Black (format) | — | 快且现代的 Python 工具链 |
| **版本控制** | Git + GitHub | — | 代码管理 + CI |

### 1.1 数据库选型补充说明

- **开发阶段**: SQLite (零配置，快速迭代)
- **部署阶段**: MySQL 8.0 (事务安全，并发支持好)
- 通过 SQLAlchemy 抽象层实现切换，配置即可，无需改代码

---

## 2. 架构设计 (Architecture)

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    浏览器 (Browser)                   │
├─────────────────────────────────────────────────────┤
│              Jinja2 模板渲染 (SSR)                    │
│              Bootstrap 5 + htmx                      │
├─────────────────────────────────────────────────────┤
│              Flask Application                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Blueprint│ │ Blueprint│ │ Blueprint ...        │ │
│  │  auth    │ │ product  │ │                      │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────────┘ │
│       │             │               │                │
│  ┌────┴─────────────┴───────────────┴─────────────┐ │
│  │              Service Layer (业务逻辑)           │ │
│  └──────────────────────┬──────────────────────────┘ │
│  ┌──────────────────────┴──────────────────────────┐ │
│  │              Model Layer (SQLAlchemy ORM)       │ │
│  └──────────────────────┬──────────────────────────┘ │
├─────────────────────────┼────────────────────────────┤
│                  MySQL / SQLite                       │
└─────────────────────────────────────────────────────┘
```

### 2.2 设计模式

| 模式 | 说明 |
|------|------|
| **Application Factory** | `create_app()` 工厂函数，支持多环境配置 |
| **Blueprint 模块化** | 按功能域拆分 (auth, product, order, message, user, admin) |
| **Service Layer** | 业务逻辑集中在 service 层，路由只做请求/响应处理 |
| **MVC 变体** | Model (ORM) + View (Jinja2) + Controller (Blueprint Routes) + Service |

### 2.3 目录结构

```
campus_trade/
├── app/                          # 应用主包
│   ├── __init__.py               # create_app() 工厂函数
│   ├── extensions.py             # SQLAlchemy, LoginManager, Migrate 等初始化
│   ├── config.py                 # 配置类 (Dev / Test / Prod)
│   ├── models/                   # 数据模型 (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── message.py
│   │   └── favorite.py
│   ├── blueprints/               # 路由蓝图
│   │   ├── auth/                 # 登录/注册/密码重置
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── product/              # 商品发布/浏览/搜索
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── order/                # 下单/交易管理
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── message/              # 买卖双方私信
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── user/                 # 个人中心
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── admin/                # 后台管理
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── main/                 # 首页/静态页面
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── message_service.py
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── decorators.py         # 自定义装饰器 (登录验证、角色验证)
│   │   ├── helpers.py            # 图片处理、分页工具等
│   │   └── constants.py          # 枚举常量
│   ├── templates/                # Jinja2 模板
│   │   ├── base.html             # 基础布局
│   │   ├── auth/
│   │   ├── product/
│   │   ├── order/
│   │   ├── message/
│   │   ├── user/
│   │   ├── admin/
│   │   └── main/
│   └── static/                   # 静态资源
│       ├── css/
│       ├── js/
│       └── uploads/              # 用户上传图片
├── migrations/                   # Alembic 迁移文件 (自动生成)
├── tests/                        # 测试套件
│   ├── conftest.py               # pytest fixtures
│   ├── test_models/
│   ├── test_services/
│   ├── test_routes/
│   └── test_forms/
├── requirements.txt
├── run.py                        # 启动入口
├── spec.md                       # 本文件
└── README.md
```

### 2.4 Application Factory 范式

```python
# app/__init__.py
def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理
    register_error_handlers(app)

    return app
```

---

## 3. 功能模块 (Feature Modules)

| 模块 | 功能点 | 优先级 |
|------|--------|--------|
| **用户认证** | 注册 (学号+邮箱验证)、登录、注销、密码重置、个人信息编辑 | P0 |
| **商品管理** | 发布商品、上传图片、编辑/下架商品、浏览商品列表、按分类/关键词/价格筛选、商品详情 | P0 |
| **收藏** | 收藏/取消收藏商品、查看收藏列表 | P1 |
| **交易订单** | 下单、确认交易、取消订单、交易历史 | P0 |
| **私信** | 买卖双方站内私信、消息列表、未读提醒 | P1 |
| **用户评价** | 交易完成后互评 (评分+文字)、查看信用记录 | P2 |
| **个人中心** | 我的商品、我的订单、我的收藏、我的消息、编辑资料 | P0 |
| **后台管理** | 用户管理、商品审核、分类管理、数据统计 | P2 |

---

## 4. 数据模型 (Data Model)

### 4.1 ER 图 (实体关系)

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   User   │───┐   │ Category │   ┌──│  Order   │
└────┬─────┘   │   └────┬─────┘   │  └────┬─────┘
     │         │        │         │       │
     │ 1:N     │        │ 1:N     │       │ N:1
     ▼         │        ▼         │       ▼
┌──────────┐   │   ┌──────────┐   │  ┌──────────┐
│ Product  │◄──┘   │ Product  │   │  │ Product  │
└────┬─────┘       └──────────┘   │  └──────────┘
     │                            │
     │ 1:N    ┌──────────┐        │
     ├───────►│ProductImg│        │
     │        └──────────┘        │
     │                            │
     │ N:M    ┌──────────┐        │
     ├───────►│ Favorite │        │
     │        └──────────┘        │
     │                            │
     │ 1:N    ┌──────────┐        │
     └───────►│ Message  │        │
              └──────────┘        │
                                  │
              ┌──────────┐        │
              │  Review  │◄───────┘
              └──────────┘
```

### 4.2 表结构设计

#### 4.2.1 `users` — 用户表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| username | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | 用户名 |
| student_id | VARCHAR(20) | UNIQUE, NOT NULL | 学号 |
| email | VARCHAR(128) | UNIQUE, NOT NULL | 邮箱 |
| phone | VARCHAR(20) | NULLABLE | 手机号 |
| password_hash | VARCHAR(256) | NOT NULL | 密码哈希 |
| real_name | VARCHAR(32) | NULLABLE | 真实姓名 (选填) |
| avatar | VARCHAR(256) | DEFAULT 'default.jpg' | 头像路径 |
| campus | VARCHAR(64) | NOT NULL | 所在校区 |
| role | VARCHAR(16) | DEFAULT 'user' | 角色: user / admin |
| credit_score | INTEGER | DEFAULT 100 | 信用分 (评价积分) |
| is_active | BOOLEAN | DEFAULT TRUE | 账号状态 |
| created_at | DATETIME | DEFAULT NOW | 注册时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

#### 4.2.2 `categories` — 商品分类表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| name | VARCHAR(64) | NOT NULL | 分类名称 |
| description | VARCHAR(256) | NULLABLE | 分类描述 |
| icon | VARCHAR(64) | NULLABLE | 图标标识 (Bootstrap Icons) |
| sort_order | INTEGER | DEFAULT 0 | 排序权重 |

分类预设数据: 图书教材, 电子产品, 生活用品, 运动器材, 衣物鞋帽, 学习用品, 其他

#### 4.2.3 `products` — 商品表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| title | VARCHAR(128) | NOT NULL | 商品标题 |
| description | TEXT | NOT NULL | 商品描述 |
| price | DECIMAL(10,2) | NOT NULL | 售价 (元) |
| original_price | DECIMAL(10,2) | NULLABLE | 原价 (可选) |
| condition | VARCHAR(16) | NOT NULL | 成色: brand_new / like_new / used / defective |
| category_id | INTEGER | FK → categories.id | 分类 |
| seller_id | INTEGER | FK → users.id, NOT NULL | 卖家 |
| campus | VARCHAR(64) | NOT NULL | 交易校区 |
| status | VARCHAR(16) | DEFAULT 'active' | active / reserved / sold / withdrawn |
| view_count | INTEGER | DEFAULT 0 | 浏览量 |
| created_at | DATETIME | DEFAULT NOW | 发布时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

索引: `(status, category_id)`, `(seller_id)`, `(campus)`, 全文索引 `(title, description)`

#### 4.2.4 `product_images` — 商品图片表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| product_id | INTEGER | FK → products.id, CASCADE | 所属商品 |
| filename | VARCHAR(256) | NOT NULL | 文件名 (UUID 命名) |
| is_cover | BOOLEAN | DEFAULT FALSE | 是否为封面图 |
| sort_order | INTEGER | DEFAULT 0 | 排序 |
| created_at | DATETIME | DEFAULT NOW | 上传时间 |

#### 4.2.5 `favorites` — 收藏表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| user_id | INTEGER | FK → users.id, CASCADE | 用户 |
| product_id | INTEGER | FK → products.id, CASCADE | 商品 |
| created_at | DATETIME | DEFAULT NOW | 收藏时间 |

约束: `UNIQUE(user_id, product_id)` — 同一用户不能重复收藏同一商品

#### 4.2.6 `orders` — 订单/交易表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| buyer_id | INTEGER | FK → users.id, NOT NULL | 买家 |
| seller_id | INTEGER | FK → users.id, NOT NULL | 卖家 |
| product_id | INTEGER | FK → products.id, NOT NULL | 商品 |
| amount | DECIMAL(10,2) | NOT NULL | 成交金额 |
| status | VARCHAR(16) | DEFAULT 'pending' | pending / confirmed / completed / cancelled |
| trade_location | VARCHAR(128) | NULLABLE | 约定交易地点 |
| trade_time | DATETIME | NULLABLE | 约定交易时间 |
| buyer_message | VARCHAR(256) | NULLABLE | 买家留言 |
| created_at | DATETIME | DEFAULT NOW | 下单时间 |
| updated_at | DATETIME | ON UPDATE NOW | 更新时间 |

约束: 买家不能是自己的卖家 (`CHECK buyer_id != seller_id`)
索引: `(buyer_id)`, `(seller_id)`, `(status)`

#### 4.2.7 `messages` — 私信表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| sender_id | INTEGER | FK → users.id, NOT NULL | 发送者 |
| receiver_id | INTEGER | FK → users.id, NOT NULL | 接收者 |
| product_id | INTEGER | FK → products.id, NULLABLE | 关联商品 |
| content | TEXT | NOT NULL | 消息内容 |
| is_read | BOOLEAN | DEFAULT FALSE | 是否已读 |
| created_at | DATETIME | DEFAULT NOW | 发送时间 |

索引: `(receiver_id, is_read)` — 快速查询某用户未读消息

#### 4.2.8 `reviews` — 评价表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO_INCREMENT | 主键 |
| order_id | INTEGER | FK → orders.id, CASCADE, UNIQUE | 关联订单 (一单一评) |
| reviewer_id | INTEGER | FK → users.id, NOT NULL | 评价者 |
| target_user_id | INTEGER | FK → users.id, NOT NULL | 被评价者 |
| rating | INTEGER | NOT NULL, CHECK 1-5 | 评分 (1-5星) |
| content | VARCHAR(512) | NULLABLE | 评价内容 |
| created_at | DATETIME | DEFAULT NOW | 评价时间 |

---

## 5. 测试策略 (Testing Strategy)

### 5.1 测试金字塔

```
         ┌──────┐
         │ E2E  │  ← 少量: 核心流程 (手动 + 可选)
         ├──────┤
         │ 集成  │  ← 中等: 路由 + 数据库 + 表单
         ├──────┤
         │ 单元  │  ← 大量: 模型 + Service + 工具函数
         └──────┘
```

### 5.2 测试分类

| 测试类型 | 工具 | 覆盖目标 | 说明 |
|----------|------|----------|------|
| **模型层测试** | pytest | 100% | 验证字段约束、关系、默认值、`__repr__` |
| **Service 层测试** | pytest + pytest-flask | 95%+ | 核心业务逻辑 (发布商品、下单、状态流转) |
| **表单验证测试** | pytest | 100% | 各表单的 valid/invalid 数据，自定义 validator |
| **路由集成测试** | pytest-flask test client | 85%+ | 各端点 GET/POST、状态码、重定向、Flash 消息 |
| **安全测试** | pytest | 关键路径 | 未登录拦截、越权访问、CSRF 保护 |
| **覆盖率汇总** | coverage.py | ≥ 80% | CI 门禁 |

### 5.3 pytest Fixtures 设计

```python
# tests/conftest.py 核心 fixtures
@pytest.fixture(scope="session")
def app():
    """创建测试用 Flask 应用 (SQLite 内存数据库)"""
    ...

@pytest.fixture
def client(app):
    """测试客户端"""
    ...

@pytest.fixture
def db(app):
    """每个测试用例独立的新数据库"""
    ...

@pytest.fixture
def logged_in_user(client, db):
    """已登录的普通用户"""
    ...

@pytest.fixture
def sample_product(db):
    """预置商品数据"""
    ...
```

### 5.4 关键测试场景清单

| # | 场景 | 类型 |
|---|------|------|
| 1 | 新用户注册 → 邮箱格式/学号唯一性/密码强度验证 | 单元 + 集成 |
| 2 | 登录 → 正确/错误密码、不存在的用户、已禁用账号 | 集成 |
| 3 | 发布商品 → 必填字段、图片上传、价格校验 | 单元 + 集成 |
| 4 | 商品列表 → 分页、分类筛选、关键词搜索、排序 | 集成 |
| 5 | 收藏商品 → 收藏/取消收藏、重复收藏拦截 | Service + 集成 |
| 6 | 下单 → 自己不能买自己的商品、已售商品不能下单 | Service + 集成 |
| 7 | 订单状态流转: pending → confirmed → completed | Service |
| 8 | 取消订单 → 只有 pending 状态可取消 | Service |
| 9 | 私信 → 发送、未读计数、关联商品 | 集成 |
| 10 | 权限控制 → 未登录访问受保护页面 → 302 /login | 集成 |
| 11 | 越权防护 → 用户 A 不能编辑用户 B 的商品 | 集成 |
| 12 | 评价 → 仅交易双方、一单一评、评分范围 | Service |

### 5.5 测试命令

```bash
# 运行全部测试 + 覆盖率
pytest --cov=app --cov-report=html --cov-report=term

# 仅运行模型测试
pytest tests/test_models/ -v

# 仅运行集成测试
pytest tests/test_routes/ -v

# 覆盖率门禁 (CI)
pytest --cov=app --cov-fail-under=80
```

---

## 6. 配置管理 (Configuration)

### 6.1 多环境配置

```python
# app/config.py
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 上传限制

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
```

### 6.2 环境变量

```
FLASK_CONFIG=development       # development / testing / production
SECRET_KEY=<随机密钥>
DATABASE_URL=mysql://user:pass@localhost/campus_trade  # 生产环境
UPLOAD_FOLDER=app/static/uploads
```

---

## 7. 非功能需求

| 类别 | 要求 |
|------|------|
| **性能** | 首页加载 < 2s，搜索响应 < 1s (SQL 索引支持) |
| **安全** | 密码哈希存储、CSRF 保护、文件上传类型校验、SQL 注入防护 (ORM) |
| **可用性** | 响应式设计，PC + 移动端适配 (Bootstrap 栅格) |
| **可维护性** | 代码遵循 PEP 8，blueprint 模块化，注释覆盖关键逻辑 |
| **数据完整性** | 外键约束 + 数据库事务 + 逻辑删除 (用户/商品) |

---

## 8. 开发路线图

| 阶段 | 内容 | 预计产出 |
|------|------|----------|
| **Phase 1: 基础搭建** | 项目骨架、配置、数据库模型、迁移 | 可运行的 Flask 应用 + 建表 |
| **Phase 2: 用户系统** | 注册/登录/认证/个人中心 | 完整的用户闭环 |
| **Phase 3: 商品系统** | 发布/浏览/搜索/收藏 | 商品 CRUD + 列表展示 |
| **Phase 4: 交易系统** | 下单/订单管理/状态流转 | 核心交易闭环 |
| **Phase 5: 辅助功能** | 私信/评价/后台管理 | 完整功能集 |
| **Phase 6: 测试补全** | 单元测试 + 集成测试 + 覆盖率达标 | 测试报告 |
| **Phase 7: 论文撰写** | 需求分析、设计文档、实现描述、测试章节 | 毕业论文 |

---

> **下一步**: 请确认以上技术选型和架构决策，确认后进入 Phase 1 代码实现。
