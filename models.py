from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120), default='')
    role = db.Column(db.String(20), default='editor', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        # Explicit PBKDF2 keeps the app compatible with Python 3.9 builds
        # that do not expose hashlib.scrypt.
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False, comment='订单号')
    customer_name = db.Column(db.String(100), nullable=False, comment='客户名称')
    product_name = db.Column(db.String(200), nullable=False, comment='产品名称')
    order_date = db.Column(db.Date, default=datetime.utcnow().date, comment='下单日期')
    delivery_date = db.Column(db.Date, comment='交货日期')
    quantity = db.Column(db.Integer, default=0, comment='数量')
    notes = db.Column(db.Text, comment='备注')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = db.relationship('ProcessStep', backref='order', lazy='joined',
                            order_by='ProcessStep.seq',
                            cascade='all, delete-orphan')
    materials = db.relationship('OrderMaterial', backref='order', lazy='joined',
                                cascade='all, delete-orphan')
    checkin_records = db.relationship('CheckinRecord', backref='order', lazy='dynamic',
                                      cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'customer_name': self.customer_name,
            'product_name': self.product_name,
            'order_date': self.order_date.strftime('%Y-%m-%d') if self.order_date else '',
            'delivery_date': self.delivery_date.strftime('%Y-%m-%d') if self.delivery_date else '',
            'quantity': self.quantity,
            'notes': self.notes or '',
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'steps': [s.to_dict() for s in self.steps],
        }

    def current_status(self):
        """计算订单当前整体状态"""
        if not self.steps:
            return 'draft'
        all_completed = all(s.status == 'completed' for s in self.steps)
        if all_completed:
            return 'completed'
        any_in_progress = any(s.status == 'in_progress' for s in self.steps)
        if any_in_progress:
            return 'in_progress'
        return 'pending'

    def current_step_name(self):
        """获取当前进行到的步骤名称"""
        for s in self.steps:
            if s.status == 'in_progress':
                return s.step_name
        for s in self.steps:
            if s.status == 'pending':
                return s.step_name
        return '全部完成'


class ProcessStep(db.Model):
    __tablename__ = 'process_steps'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    seq = db.Column(db.Integer, nullable=False, comment='步骤顺序')
    category = db.Column(db.String(50), default='common', comment='类别: common/sampling/production/inspection')
    step_name = db.Column(db.String(100), nullable=False, comment='步骤名称')
    step_type = db.Column(db.String(50), comment='类型选项: 自己做/外面做/不需要')
    status = db.Column(db.String(20), default='pending', comment='pending/in_progress/completed/skipped')
    planned_date = db.Column(db.Date, comment='计划日期')
    completed_date = db.Column(db.Date, comment='完成日期')
    assignee = db.Column(db.String(100), comment='负责人')
    notes = db.Column(db.Text, comment='备注')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'seq': self.seq,
            'category': self.category,
            'step_name': self.step_name,
            'step_type': self.step_type or '',
            'status': self.status,
            'planned_date': self.planned_date.strftime('%Y-%m-%d') if self.planned_date else '',
            'completed_date': self.completed_date.strftime('%Y-%m-%d') if self.completed_date else '',
            'assignee': self.assignee or '',
            'notes': self.notes or '',
        }


class Material(db.Model):
    """物料主数据"""
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='物料名称')
    spec = db.Column(db.String(200), default='', comment='规格')
    unit = db.Column(db.String(20), default='个', comment='单位')
    category = db.Column(db.String(50), default='包材', comment='类别: 包材/五金/电子/辅料/其他')
    stock_qty = db.Column(db.Float, default=0, comment='当前库存数量')
    min_stock = db.Column(db.Float, default=0, comment='最低库存警戒')
    note = db.Column(db.Text, default='', comment='备注')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    records = db.relationship('InventoryRecord', backref='material', lazy='dynamic',
                              cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'spec': self.spec or '',
            'unit': self.unit,
            'category': self.category,
            'stock_qty': self.stock_qty,
            'min_stock': self.min_stock or 0,
            'note': self.note or '',
        }


class InventoryRecord(db.Model):
    """库存出入库流水"""
    __tablename__ = 'inventory_records'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    type = db.Column(db.String(10), nullable=False, comment='purchase:购进/consume:消耗')
    quantity = db.Column(db.Float, nullable=False, comment='数量')
    before_qty = db.Column(db.Float, default=0, comment='操作前库存')
    after_qty = db.Column(db.Float, default=0, comment='操作后库存')
    operator = db.Column(db.String(50), default='', comment='操作人')
    note = db.Column(db.Text, default='', comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'order_id': self.order_id,
            'type': self.type,
            'quantity': self.quantity,
            'before_qty': self.before_qty,
            'after_qty': self.after_qty,
            'operator': self.operator or '',
            'note': self.note or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class OrderMaterial(db.Model):
    """订单物料用量清单"""
    __tablename__ = 'order_materials'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    required_qty = db.Column(db.Float, default=0, comment='需求量')
    used_qty = db.Column(db.Float, default=0, comment='已使用量')
    note = db.Column(db.Text, default='', comment='备注')

    material = db.relationship('Material', backref='order_usage', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else '',
            'material_unit': self.material.unit if self.material else '',
            'required_qty': self.required_qty,
            'used_qty': self.used_qty,
            'note': self.note or '',
        }


# ============================================================
#  新增：步骤定义（打卡用） - 先单独设置，其他人才能选择
# ============================================================

class StepDefinition(db.Model):
    """打卡步骤定义 - 管理员预先设置好的可选步骤列表"""
    __tablename__ = 'step_definitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='步骤名称')
    category = db.Column(db.String(50), default='production', comment='步骤分类')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


# ============================================================
#  新增：打卡记录
# ============================================================

class CheckinRecord(db.Model):
    """打卡记录 - 记录每个订单每个步骤的打卡情况"""
    __tablename__ = 'checkin_records'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False, comment='步骤名称')
    status = db.Column(db.String(20), default='in_progress', comment='in_progress/completed')
    completed_qty = db.Column(db.Float, default=0, comment='已完成数量')
    operator = db.Column(db.String(50), default='', comment='操作人')
    note = db.Column(db.Text, default='', comment='备注')
    checkin_date = db.Column(db.Date, default=datetime.utcnow().date, comment='打卡日期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_no': self.order.order_no if self.order else '',
            'product_name': self.order.product_name if self.order else '',
            'step_name': self.step_name,
            'status': self.status,
            'completed_qty': self.completed_qty,
            'operator': self.operator or '',
            'note': self.note or '',
            'checkin_date': self.checkin_date.strftime('%Y-%m-%d') if self.checkin_date else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class CapacityPlan(db.Model):
    """产能预期记录"""
    __tablename__ = 'capacity_plans'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    product_name = db.Column(db.String(200), default='', comment='产品名称')
    total_qty = db.Column(db.Float, default=0, comment='总数量')
    hourly_rate = db.Column(db.Float, default=0, comment='单人每小时产能')
    workers = db.Column(db.Float, default=1, comment='参与人数')
    hours_per_day = db.Column(db.Float, default=8, comment='每天工作小时数')
    daily_output = db.Column(db.Float, default=0, comment='日产能（自动计算）')
    est_days = db.Column(db.Float, default=0, comment='预计天数（自动计算）')
    start_date = db.Column(db.Date, comment='起始日期')
    est_end_date = db.Column(db.Date, comment='预计完成日期')
    completed_qty = db.Column(db.Float, default=0, comment='已完成数量（从打卡同步）')
    note = db.Column(db.Text, default='', comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_name': self.product_name,
            'total_qty': self.total_qty,
            'hourly_rate': self.hourly_rate,
            'workers': self.workers,
            'hours_per_day': self.hours_per_day,
            'daily_output': self.daily_output,
            'est_days': self.est_days,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'est_end_date': self.est_end_date.strftime('%Y-%m-%d') if self.est_end_date else '',
            'completed_qty': self.completed_qty,
            'note': self.note or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


# 预定义的标准流程步骤
DEFAULT_STEPS = [
    {'seq': 1, 'category': 'sampling', 'step_name': '产品打样', 'has_type': True},
    {'seq': 2, 'category': 'sampling', 'step_name': '寄样'},
    {'seq': 3, 'category': 'sampling', 'step_name': '客户确认样品'},
    {'seq': 4, 'category': 'sampling', 'step_name': '包装确认'},
    {'seq': 5, 'category': 'sampling', 'step_name': 'QA样'},
    {'seq': 6, 'category': 'common', 'step_name': '确认物料齐全'},
    {'seq': 7, 'category': 'production', 'step_name': '机芯生产'},
    {'seq': 8, 'category': 'production', 'step_name': '蜡壳生产'},
    {'seq': 9, 'category': 'production', 'step_name': '组装'},
    {'seq': 10, 'category': 'production', 'step_name': '包装'},
    {'seq': 11, 'category': 'inspection', 'step_name': '验货'},
    {'seq': 12, 'category': 'testing', 'step_name': '准备测试样'},
    {'seq': 13, 'category': 'testing', 'step_name': '测试'},
]
