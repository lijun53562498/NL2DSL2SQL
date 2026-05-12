#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from nl2sql.core.schema import create_sample_schema
from faker import Faker

fake = Faker('zh_CN')


class DatabaseInitializer:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(current_dir, 'nl2sql_test.db')
        self.conn = None
        self.cursor = None
        
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"已连接到数据库: {self.db_path}")
        except Exception as e:
            print(f"连接数据库失败: {e}")
            sys.exit(1)
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("数据库连接已关闭")
    
    def drop_all_tables(self):
        print("\n删除所有表...")
        tables = [
            'product_purchase_prices', 'product_suppliers', 'warehouses',
            'shipping_methods', 'stock_logs', 'admin_logs', 'admin_users',
            'product_tag_mapping', 'product_tags', 'user_behaviors',
            'flash_sale_products', 'flash_sales', 'product_specs',
            'product_favorites', 'shopping_carts', 'product_reviews',
            'user_coupons', 'coupons', 'payments', 'order_items', 'orders',
            'product_skus', 'brands', 'products', 'categories', 'addresses', 'users'
        ]
        for table in tables:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                print(f"删除表 {table} 失败: {e}")
        self.conn.commit()
        print("所有表已删除")
    
    def get_sqlite_type(self, sql_type):
        type_mapping = {
            'INTEGER': 'INTEGER',
            'VARCHAR(50)': 'TEXT',
            'VARCHAR(100)': 'TEXT',
            'VARCHAR(200)': 'TEXT',
            'VARCHAR(255)': 'TEXT',
            'VARCHAR(500)': 'TEXT',
            'VARCHAR(1000)': 'TEXT',
            'VARCHAR(20)': 'TEXT',
            'VARCHAR(45)': 'TEXT',
            'VARCHAR(10)': 'TEXT',
            'DATE': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'DECIMAL(10,2)': 'REAL',
            'DECIMAL(8,3)': 'REAL',
            'DECIMAL(5,2)': 'REAL',
            'DECIMAL(3,2)': 'REAL',
            'BOOLEAN': 'INTEGER',
            'TEXT': 'TEXT',
            'JSON': 'TEXT',
            'JSONB': 'TEXT',
        }
        return type_mapping.get(sql_type, 'TEXT')
    
    def create_tables(self, schema):
        print("\n创建数据库表...")
        tables = schema.tables
        
        for table_name, table_info in tables.items():
            columns = table_info.get('columns', [])
            column_types = table_info.get('column_types', {})
            
            col_defs = []
            for col in columns:
                sqlite_type = self.get_sqlite_type(column_types.get(col, 'TEXT'))
                col_defs.append(f'"{col}" {sqlite_type}')
            
            create_sql = f'CREATE TABLE {table_name} (\n    '
            create_sql += ',\n    '.join(col_defs)
            create_sql += '\n);'
            
            try:
                self.cursor.execute(create_sql)
                print(f"  创建表 {table_name} 成功")
            except Exception as e:
                print(f"  创建表 {table_name} 失败: {e}")
        
        self.conn.commit()
        print("所有表创建完成")
    
    def create_indexes(self):
        print("\n创建索引...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);",
            "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);",
            "CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);",
            "CREATE INDEX IF NOT EXISTS idx_products_brand_id ON products(brand_id);",
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);",
            "CREATE INDEX IF NOT EXISTS idx_products_is_on_sale ON products(is_on_sale);",
            "CREATE INDEX IF NOT EXISTS idx_products_is_hot ON products(is_hot);",
            "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_orders_order_status ON orders(order_status);",
            "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);",
            "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);",
            "CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id ON product_reviews(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_product_reviews_user_id ON product_reviews(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_shopping_carts_user_id ON shopping_carts(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_product_favorites_user_id ON product_favorites(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_behaviors_user_id ON user_behaviors(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_behaviors_created_at ON user_behaviors(created_at);",
        ]
        
        for idx_sql in indexes:
            try:
                self.cursor.execute(idx_sql)
            except Exception as e:
                pass
        
        self.conn.commit()
        print("索引创建完成")
    
    def generate_test_data(self, schema):
        print("\n生成测试数据...")
        
        self._generate_users(50)
        self._generate_addresses(100)
        self._generate_categories()
        self._generate_brands(30)
        self._generate_products(200)
        self._generate_product_skus(500)
        self._generate_orders(300)
        self._generate_order_items(800)
        self._generate_payments(300)
        self._generate_coupons(50)
        self._generate_user_coupons(200)
        self._generate_product_reviews(500)
        self._generate_shopping_carts(100)
        self._generate_product_favorites(150)
        self._generate_product_specs(200)
        self._generate_flash_sales()
        self._generate_flash_sale_products(100)
        self._generate_user_behaviors(1000)
        self._generate_product_tags(30)
        self._generate_product_tag_mapping(300)
        self._generate_admin_users(10)
        self._generate_admin_logs(200)
        self._generate_shipping_methods(5)
        self._generate_warehouses(8)
        self._generate_product_suppliers(20)
        self._generate_product_purchase_prices(200)
        self._generate_stock_logs(500)
        
        self.conn.commit()
        print("测试数据生成完成")
    
    def _format_datetime(self, dt):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_users(self, count):
        print(f"  生成 users 表数据 ({count} 条)...")
        statuses = ['active', 'inactive', 'suspended']
        user_levels = [1, 2, 3, 4, 5]
        
        users = []
        for i in range(1, count + 1):
            registered_at = fake.date_time_between(start_date='-2y', end_date='now')
            users.append((
                i, f'user_{i}', 'hashed_password', fake.name(), fake.email(),
                fake.phone_number(), random.choice(['男', '女']),
                fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%Y-%m-%d'),
                f'https://example.com/avatar/{i}.jpg', random.choice(statuses),
                random.choice(user_levels), random.randint(0, 10000),
                self._format_datetime(registered_at), 
                self._format_datetime(fake.date_time_between(start_date=registered_at, end_date='now')),
                random.randint(1, count) if random.random() > 0.3 else None
            ))
        
        sql = """INSERT INTO users (id, username, password, real_name, email, phone, gender, birthday, avatar_url, status, user_level, total_points, registered_at, last_login_at, address_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, users)
    
    def _generate_addresses(self, count):
        print(f"  生成 addresses 表数据 ({count} 条)...")
        provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '四川省', '湖北省', '湖南省']
        
        addresses = []
        for i in range(1, count + 1):
            user_id = random.randint(1, 50)
            addresses.append((
                i, user_id, fake.name(), fake.phone_number(),
                random.choice(provinces), fake.city(), fake.district(),
                fake.address(), f"{random.randint(100000, 999999)}", 1 if random.random() > 0.5 else 0,
                self._format_datetime(fake.date_time_between(start_date='-1y', end_date='now'))
            ))
        
        sql = """INSERT INTO addresses (id, user_id, receiver_name, phone, province, city, district, detail_address, postal_code, is_default, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, addresses)
    
    def _generate_categories(self):
        print("  生成 categories 表数据...")
        categories_data = [
            (1, None, '电子产品', '手机、电脑、数码配件', 'electronics', 1, 1, self._format_datetime(datetime.now())),
            (2, 1, '手机', '各类智能手机', 'phones', 1, 1, self._format_datetime(datetime.now())),
            (3, 1, '电脑', '笔记本电脑、台式机', 'computers', 2, 1, self._format_datetime(datetime.now())),
            (4, 1, '数码配件', '耳机、充电器等', 'accessories', 3, 1, self._format_datetime(datetime.now())),
            (5, None, '服装', '男装、女装、童装', 'clothing', 2, 1, self._format_datetime(datetime.now())),
            (6, 5, '男装', '男士服装', 'men', 1, 1, self._format_datetime(datetime.now())),
            (7, 5, '女装', '女士服装', 'women', 2, 1, self._format_datetime(datetime.now())),
            (8, None, '食品', '水果、蔬菜、零食', 'food', 3, 1, self._format_datetime(datetime.now())),
            (9, 8, '水果', '新鲜水果', 'fruits', 1, 1, self._format_datetime(datetime.now())),
            (10, 8, '零食', '各类零食', 'snacks', 2, 1, self._format_datetime(datetime.now())),
            (11, None, '家居', '家具、家纺', 'home', 4, 1, self._format_datetime(datetime.now())),
            (12, 11, '家具', '床、沙发、桌子', 'furniture', 1, 1, self._format_datetime(datetime.now())),
            (13, 11, '家纺', '床品、窗帘', 'textiles', 2, 1, self._format_datetime(datetime.now())),
            (14, None, '运动', '运动器材、户外装备', 'sports', 5, 1, self._format_datetime(datetime.now())),
            (15, 14, '运动器材', '球类、健身器材', 'equipment', 1, 1, self._format_datetime(datetime.now())),
        ]
        
        sql = """INSERT INTO categories (id, parent_id, name, description, icon_url, sort_order, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, categories_data)
    
    def _generate_brands(self, count):
        print(f"  生成 brands 表数据 ({count} 条)...")
        brand_names = ['Apple', 'Samsung', '华为', '小米', 'OPPO', 'vivo', '联想', '戴尔', '惠普', '华硕',
                       'Nike', 'Adidas', '优衣库', '海澜之家', 'Zara', 'H&M', '宜家', '顾家', '美的', '海尔',
                       '格力', '小米生态', '索尼', '佳能', '尼康', 'beats', '森海塞尔', '罗技', '雷蛇', '樱桃']
        
        brands = []
        for i, name in enumerate(brand_names[:count], 1):
            brands.append((
                i, name, f'https://example.com/brand/{i}.png', f'{name}官方品牌',
                random.choice(['中国', '美国', '日本', '韩国', '德国', '英国']),
                f'https://www.{name.lower()}.com', i, 1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO brands (id, name, logo_url, description, country, website, sort_order, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, brands)
    
    def _generate_products(self, count):
        print(f"  生成 products 表数据 ({count} 条)...")
        
        product_names = [
            'iPhone 15 Pro Max', 'Samsung Galaxy S24', '华为Mate 60', '小米14 Ultra',
            'MacBook Pro 16寸', 'ThinkPad X1 Carbon', '戴尔XPS 15', '华硕ROG游戏本',
            'AirPods Pro 2', '索尼WH-1000XM5', 'Beats Studio3', '小米手环8',
            'Nike Air Max 90', 'Adidas Ultraboost', '优衣库联名T恤', 'Zara休闲裤',
            '红富士苹果', '进口车厘子', '有机草莓', '海南芒果',
            '宜家马尔姆床', '顾家真皮沙发', '美的空调', '海尔冰箱',
            '佳能EOS R5', '尼康Z8', '罗技MX Master 3', '雷蛇黑寡妇键盘'
        ]
        
        products = []
        for i in range(1, count + 1):
            name = product_names[i % len(product_names)] + f' {i}'
            price = round(random.uniform(99, 9999), 2)
            cost = round(price * random.uniform(0.4, 0.7), 2)
            products.append((
                i, random.randint(1, 15), random.randint(1, 30), name,
                f'{name}的详细描述', price, round(price * 1.2, 2), cost,
                random.randint(0, 1000), random.randint(10, 100), random.choice(['个', '件', '台', '斤']),
                round(random.uniform(0.5, 10), 3), f'{random.randint(100000, 999999)}',
                f'https://example.com/product/{i}/main.jpg', '[]',
                1 if random.random() > 0.1 else 0, 1 if random.random() > 0.7 else 0, 
                1 if random.random() > 0.8 else 0, 1 if random.random() > 0.8 else 0,
                random.randint(0, 5000), random.randint(100, 10000), round(random.uniform(3.5, 5.0), 2),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 365))),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(0, 30)))
            ))
        
        sql = """INSERT INTO products (id, category_id, brand_id, name, description, price, original_price, cost, stock, stock_alert, unit, weight, barcode, main_image, images, is_on_sale, is_hot, is_new, is_recommend, sales_count, view_count, rating, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, products)
    
    def _generate_product_skus(self, count):
        print(f"  生成 product_skus 表数据 ({count} 条)...")
        
        specs_list = [
            '{"颜色": "黑色", "内存": "8GB"}', '{"颜色": "白色", "内存": "8GB"}',
            '{"颜色": "黑色", "内存": "16GB"}', '{"颜色": "白色", "内存": "16GB"}',
            '{"颜色": "红色", "内存": "8GB"}', '{"尺码": "S"}', '{"尺码": "M"}',
            '{"尺码": "L"}', '{"尺码": "XL"}', '{"容量": "128GB"}', '{"容量": "256GB"}',
            '{"容量": "512GB"}', '{"版本": "标准版"}', '{"版本": "尊享版"}'
        ]
        
        skus = []
        for i in range(1, count + 1):
            product_id = random.randint(1, 200)
            price = round(random.uniform(99, 9999), 2)
            skus.append((
                i, product_id, f'SKU{i:06d}', random.choice(specs_list),
                price, random.randint(0, 500), random.randint(0, 1000),
                f'https://example.com/sku/{i}.jpg', 1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO product_skus (id, product_id, sku_code, specs, price, stock, sales_count, image_url, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, skus)
    
    def _generate_orders(self, count):
        print(f"  生成 orders 表数据 ({count} 条)...")
        
        order_statuses = ['pending', 'paid', 'shipped', 'completed', 'canceled']
        payment_statuses = ['unpaid', 'paid', 'refunded']
        shipping_statuses = ['unshipped', 'shipped', 'delivered']
        
        orders = []
        for i in range(1, count + 1):
            user_id = random.randint(1, 50)
            created_at = fake.date_time_between(start_date='-6m', end_date='now')
            total_amount = round(random.uniform(100, 5000), 2)
            discount_amount = round(total_amount * random.uniform(0, 0.2), 2)
            freight_amount = round(random.uniform(0, 20), 2)
            pay_amount = total_amount - discount_amount + freight_amount
            
            order_status = random.choice(order_statuses)
            paid_at = shipped_at = received_at = completed_at = canceled_at = None
            
            if order_status in ['paid', 'shipped', 'completed']:
                paid_at = created_at + timedelta(hours=random.randint(1, 24))
            if order_status in ['shipped', 'completed']:
                shipped_at = paid_at + timedelta(days=random.randint(1, 3))
            if order_status == 'completed':
                received_at = shipped_at + timedelta(days=random.randint(1, 5))
                completed_at = received_at + timedelta(days=1)
            if order_status == 'canceled':
                canceled_at = created_at + timedelta(days=random.randint(1, 7))
            
            orders.append((
                i, f'ORD{i:010d}', user_id, order_status, 
                random.choice(payment_statuses) if order_status != 'canceled' else 'refunded',
                random.choice(shipping_statuses),
                total_amount, discount_amount, freight_amount, pay_amount,
                random.randint(0, 100), random.randint(0, 50),
                random.randint(1, 100), random.choice(['顺丰', '中通', '圆通', '韵达']),
                f'SF{random.randint(100000, 999999)}' if order_status != 'pending' else None,
                f'{fake.company()}发票', f'订单备注{i}',
                self._format_datetime(created_at), 
                self._format_datetime(paid_at), 
                self._format_datetime(shipped_at), 
                self._format_datetime(received_at), 
                self._format_datetime(completed_at), 
                self._format_datetime(canceled_at)
            ))
        
        sql = """INSERT INTO orders (id, order_no, user_id, order_status, payment_status, shipping_status, total_amount, discount_amount, freight_amount, pay_amount, points_discount, coupon_discount, address_id, shipping_method, shipping_no, invoice_title, remark, created_at, paid_at, shipped_at, received_at, completed_at, canceled_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, orders)
    
    def _generate_order_items(self, count):
        print(f"  生成 order_items 表数据 ({count} 条)...")
        
        items = []
        for i in range(1, count + 1):
            order_id = random.randint(1, 300)
            product_id = random.randint(1, 200)
            sku_id = random.randint(1, 500) if random.random() > 0.3 else None
            product_name = f'商品{product_id}'
            price = round(random.uniform(10, 1000), 2)
            quantity = random.randint(1, 5)
            subtotal = price * quantity
            discount = round(subtotal * random.uniform(0, 0.1), 2)
            
            items.append((
                i, order_id, product_id, sku_id, product_name,
                '{}' if sku_id is None else '{"规格": "标准"}',
                price, quantity, subtotal, discount,
                1 if random.random() > 0.9 else 0, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO order_items (id, order_id, product_id, sku_id, product_name, sku_specs, price, quantity, subtotal, discount, is_gift, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, items)
    
    def _generate_payments(self, count):
        print(f"  生成 payments 表数据 ({count} 条)...")
        
        payment_methods = ['alipay', 'wechat', 'unionpay', 'credit_card']
        statuses = ['pending', 'completed', 'failed', 'refunded']
        
        payments = []
        for i in range(1, count + 1):
            order_id = random.randint(1, 300)
            user_id = random.randint(1, 50)
            amount = round(random.uniform(50, 5000), 2)
            status = random.choice(statuses)
            created_at = fake.date_time_between(start_date='-6m', end_date='now')
            paid_at = created_at + timedelta(hours=random.randint(1, 2)) if status == 'completed' else None
            
            payments.append((
                i, f'PAY{i:012d}', order_id, user_id,
                random.choice(payment_methods), amount, status,
                f'TXN{random.randint(100000, 999999)}' if status == 'completed' else None,
                self._format_datetime(paid_at), self._format_datetime(created_at)
            ))
        
        sql = """INSERT INTO payments (id, payment_no, order_id, user_id, payment_method, amount, status, transaction_id, paid_at, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, payments)
    
    def _generate_coupons(self, count):
        print(f"  生成 coupons 表数据 ({count} 条)...")
        
        coupon_types = ['cash', 'discount']
        coupons = []
        for i in range(1, count + 1):
            start_at = datetime.now() - timedelta(days=random.randint(30, 60))
            end_at = datetime.now() + timedelta(days=random.randint(30, 180))
            
            if random.choice(coupon_types) == 'cash':
                amount = random.choice([10, 20, 50, 100, 200])
                discount = None
                max_discount = None
            else:
                amount = None
                discount = round(random.uniform(0.8, 0.95), 2)
                max_discount = random.choice([50, 100, 200])
            
            coupons.append((
                i, f'优惠券{i}', random.choice(coupon_types), amount, 
                random.randint(100, 1000), discount, max_discount,
                random.randint(100, 1000), random.randint(10, 100),
                random.randint(1, 5), 
                start_at.strftime('%Y-%m-%d'), end_at.strftime('%Y-%m-%d'), 
                1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO coupons (id, name, type, amount, min_amount, discount, max_discount, total_count, remain_count, per_limit, start_at, end_at, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, coupons)
    
    def _generate_user_coupons(self, count):
        print(f"  生成 user_coupons 表数据 ({count} 条)...")
        
        statuses = ['unused', 'used', 'expired']
        user_coupons = []
        for i in range(1, count + 1):
            user_id = random.randint(1, 50)
            coupon_id = random.randint(1, 50)
            received_at = fake.date_time_between(start_date='-3m', end_date='now')
            status = random.choice(statuses)
            order_id = random.randint(1, 300) if status == 'used' else None
            used_at = received_at + timedelta(days=random.randint(1, 10)) if status == 'used' else None
            
            user_coupons.append((
                i, user_id, coupon_id, order_id, status, 
                self._format_datetime(received_at), self._format_datetime(used_at)
            ))
        
        sql = """INSERT INTO user_coupons (id, user_id, coupon_id, order_id, status, received_at, used_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, user_coupons)
    
    def _generate_product_reviews(self, count):
        print(f"  生成 product_reviews 表数据 ({count} 条)...")
        
        reviews = []
        for i in range(1, count + 1):
            order_id = random.randint(1, 300)
            order_item_id = random.randint(1, 800)
            product_id = random.randint(1, 200)
            user_id = random.randint(1, 50)
            rating = random.randint(1, 5)
            created_at = fake.date_time_between(start_date='-3m', end_date='now')
            
            reviews.append((
                i, order_id, order_item_id, product_id, user_id, rating,
                fake.sentence(nb_words=20), '[]',
                fake.sentence() if random.random() > 0.7 else None,
                self._format_datetime(created_at + timedelta(days=random.randint(1, 7))) if random.random() > 0.7 else None,
                1 if random.random() > 0.8 else 0, 1 if random.random() > 0.9 else 0,
                random.randint(0, 100), self._format_datetime(created_at)
            ))
        
        sql = """INSERT INTO product_reviews (id, order_id, order_item_id, product_id, user_id, rating, content, images, reply, reply_at, is_anonymous, is_show, like_count, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, reviews)
    
    def _generate_shopping_carts(self, count):
        print(f"  生成 shopping_carts 表数据 ({count} 条)...")
        
        carts = []
        for i in range(1, count + 1):
            user_id = random.randint(1, 50)
            product_id = random.randint(1, 200)
            sku_id = random.randint(1, 500) if random.random() > 0.3 else None
            
            carts.append((
                i, user_id, product_id, sku_id, random.randint(1, 10),
                1 if random.random() > 0.2 else 0, 
                self._format_datetime(datetime.now()), 
                self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO shopping_carts (id, user_id, product_id, sku_id, quantity, selected, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, carts)
    
    def _generate_product_favorites(self, count):
        print(f"  生成 product_favorites 表数据 ({count} 条)...")
        
        favorites = []
        for i in range(1, count + 1):
            favorites.append((
                i, random.randint(1, 50), random.randint(1, 200),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 180)))
            ))
        
        sql = """INSERT INTO product_favorites (id, user_id, product_id, created_at)
                 VALUES (?, ?, ?, ?)"""
        self.cursor.executemany(sql, favorites)
    
    def _generate_product_specs(self, count):
        print(f"  生成 product_specs 表数据 ({count} 条)...")
        
        specs = []
        for i in range(1, count + 1):
            product_id = random.randint(1, 200)
            name = random.choice(['颜色', '内存', '存储', '尺码', '版本'])
            values = json.dumps(['黑色', '白色', '红色', '蓝色'][:random.randint(2, 4)], ensure_ascii=False)
            
            specs.append((
                i, product_id, name, values,
                1 if name == '颜色' else 0, 1 if name in ['尺码', '尺寸'] else 0, random.randint(1, 10)
            ))
        
        sql = """INSERT INTO product_specs (id, product_id, name, "values", is_color, is_size, sort_order)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, specs)
    
    def _generate_flash_sales(self):
        print("  生成 flash_sales 表数据...")
        
        sales = []
        for i in range(1, 6):
            start_time = datetime.now() + timedelta(days=random.randint(-7, 7))
            end_time = start_time + timedelta(hours=random.randint(2, 24))
            status = 'ended' if end_time < datetime.now() else ('active' if start_time < datetime.now() else 'pending')
            
            sales.append((
                i, f'秒杀活动{i}', 
                self._format_datetime(start_time), 
                self._format_datetime(end_time), 
                status, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO flash_sales (id, name, start_time, end_time, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, sales)
    
    def _generate_flash_sale_products(self, count):
        print(f"  生成 flash_sale_products 表数据 ({count} 条)...")
        
        flash_products = []
        for i in range(1, count + 1):
            flash_sale_id = random.randint(1, 5)
            product_id = random.randint(1, 200)
            sku_id = random.randint(1, 500)
            flash_price = round(random.uniform(9.9, 99.9), 2)
            stock = random.randint(10, 100)
            
            flash_products.append((
                i, flash_sale_id, product_id, sku_id, flash_price,
                stock, random.randint(0, stock), random.randint(1, 5),
                self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO flash_sale_products (id, flash_sale_id, product_id, sku_id, flash_price, stock, sold_count, limit_per_user, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, flash_products)
    
    def _generate_user_behaviors(self, count):
        print(f"  生成 user_behaviors 表数据 ({count} 条)...")
        
        behavior_types = ['browse', 'favorite', 'add_cart', 'search', 'share']
        target_types = ['product', 'category', 'brand']
        sources = ['search', 'recommend', 'direct', 'social']
        
        behaviors = []
        for i in range(1, count + 1):
            user_id = random.randint(1, 50) if random.random() > 0.2 else None
            behavior = random.choice(behavior_types)
            
            behaviors.append((
                i, user_id, behavior, random.choice(target_types),
                random.randint(1, 200), random.randint(10, 600),
                random.choice(sources), f'192.168.{random.randint(1,255)}.{random.randint(1,255)}',
                '{"device": "iPhone 14", "os": "iOS 17"}',
                fake.city(), f'https://example.com/referer{i}',
                self._format_datetime(datetime.now() - timedelta(hours=random.randint(1, 720)))
            ))
        
        sql = """INSERT INTO user_behaviors (id, user_id, behavior_type, target_type, target_id, duration, source, ip_address, device_info, location, referer_url, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, behaviors)
    
    def _generate_product_tags(self, count):
        print(f"  生成 product_tags 表数据 ({count} 条)...")
        
        tag_names = ['热销', '新品', '推荐', '爆款', '限时特价', '库存紧张', '预售',
                    '进口', '国产', '有机', '环保', '高端', '性价比', '明星同款', 
                    '网红', '爆款', '限量', '独家', '新品上市', '季末清仓',
                    '会员专享', '新人礼', '满减', '包邮', '赠品', '秒杀', '拼团']
        
        tags = []
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'gray']
        for i, name in enumerate(tag_names[:count], 1):
            tags.append((
                i, name, random.choice(colors), f'{name}标签描述',
                i, 1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO product_tags (id, name, color, description, sort_order, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, tags)
    
    def _generate_product_tag_mapping(self, count):
        print(f"  生成 product_tag_mapping 表数据 ({count} 条)...")
        
        mappings = []
        for i in range(1, count + 1):
            mappings.append((
                i, random.randint(1, 200), random.randint(1, 28),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 90)))
            ))
        
        sql = """INSERT INTO product_tag_mapping (id, product_id, tag_id, created_at)
                 VALUES (?, ?, ?, ?)"""
        self.cursor.executemany(sql, mappings)
    
    def _generate_admin_users(self, count):
        print(f"  生成 admin_users 表数据 ({count} 条)...")
        
        roles = ['super_admin', 'admin', 'manager', 'editor', 'viewer']
        statuses = ['active', 'inactive']
        
        admins = []
        for i in range(1, count + 1):
            admins.append((
                i, f'admin_{i}', 'hashed_password', fake.name(), fake.email(),
                fake.phone_number(), random.choice(roles),
                '{"permissions": ["read", "write", "delete"]}',
                random.choice(statuses),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 180))),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 365)))
            ))
        
        sql = """INSERT INTO admin_users (id, username, password, real_name, email, phone, role, permissions, status, last_login_at, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, admins)
    
    def _generate_admin_logs(self, count):
        print(f"  生成 admin_logs 表数据 ({count} 条)...")
        
        actions = ['create', 'update', 'delete', 'login', 'logout', 'export', 'import']
        modules = ['users', 'products', 'orders', 'categories', 'brands', 'coupons']
        target_types = ['user', 'product', 'order', 'category', 'brand', 'coupon']
        
        logs = []
        for i in range(1, count + 1):
            logs.append((
                i, random.randint(1, 10), random.choice(actions), random.choice(modules),
                random.choice(target_types), random.randint(1, 200),
                '{}', '{}', f'192.168.{random.randint(1,255)}.{random.randint(1,255)}',
                'Mozilla/5.0', self._format_datetime(datetime.now() - timedelta(hours=random.randint(1, 720)))
            ))
        
        sql = """INSERT INTO admin_logs (id, admin_id, action, module, target_type, target_id, old_value, new_value, ip_address, user_agent, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, logs)
    
    def _generate_shipping_methods(self, count):
        print(f"  生成 shipping_methods 表数据...")
        
        methods = [
            ('顺丰速运', '顺丰', 15, 2, 99, 1),
            ('中通快递', '中通', 10, 1, 99, 2),
            ('圆通速递', '圆通', 8, 1, 88, 3),
            ('韵达快递', '韵达', 6, 1, 66, 4),
            ('EMS', '中国邮政', 12, 1.5, 0, 5),
        ]
        
        sql = """INSERT INTO shipping_methods (id, name, carrier, base_fee, weight_fee_per_kg, free_shipping_threshold, estimated_days, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, [(i+1, m[0], m[1], m[2], m[3], m[4], m[5], 1, self._format_datetime(datetime.now())) for i, m in enumerate(methods)])
    
    def _generate_warehouses(self, count):
        print(f"  生成 warehouses 表数据...")
        
        provinces = ['广东省', '江苏省', '浙江省', '山东省', '河南省', '四川省', '湖北省', '湖南省']
        warehouses = []
        
        for i in range(1, count + 1):
            province = provinces[i - 1] if i <= len(provinces) else random.choice(provinces)
            warehouses.append((
                i, f'仓库{i}', province, fake.city(), fake.district(),
                fake.address(), fake.name(), fake.phone_number(),
                random.randint(10000, 100000), random.randint(1000, 50000),
                random.randint(1, 10), 1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO warehouses (id, name, province, city, district, address, contact, phone, capacity, used_capacity, manager_id, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, warehouses)
    
    def _generate_product_suppliers(self, count):
        print(f"  生成 product_suppliers 表数据...")
        
        supplier_names = ['深圳XX电子', '东莞XX科技', '广州XX实业', '杭州XX贸易', '宁波XX供应链',
                          '义乌XX商贸', '上海XX进出口', '北京XX贸易', '武汉XX科技', '成都XX实业',
                          '西安XX电子', '南京XX贸易', '苏州XX制造', '青岛XX进出口', '天津XX商贸',
                          '重庆XX科技', '长沙XX实业', '郑州XX贸易', '沈阳XX制造', '哈尔滨XX商贸']
        
        payment_terms = ['月结30天', '月结60天', '现结', '预付30%']
        statuses = ['active', 'inactive', 'pending']
        
        suppliers = []
        for i, name in enumerate(supplier_names[:count], 1):
            suppliers.append((
                i, name, fake.name(), fake.phone_number(), fake.email(),
                fake.address(), random.choice(payment_terms), random.randint(7, 30),
                round(random.uniform(3.5, 5.0), 2), random.choice(statuses), self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO product_suppliers (id, name, contact_person, phone, email, address, payment_terms, lead_time_days, rating, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, suppliers)
    
    def _generate_product_purchase_prices(self, count):
        print(f"  生成 product_purchase_prices 表数据 ({count} 条)...")
        
        prices = []
        for i in range(1, count + 1):
            product_id = random.randint(1, 200)
            supplier_id = random.randint(1, min(20, count))
            purchase_price = round(random.uniform(50, 5000), 2)
            valid_from = datetime.now() - timedelta(days=random.randint(30, 180))
            valid_to = valid_from + timedelta(days=random.randint(180, 365))
            
            prices.append((
                i, product_id, supplier_id, purchase_price,
                random.randint(10, 100), round(random.uniform(0.85, 1.0), 2),
                valid_from.strftime('%Y-%m-%d'), valid_to.strftime('%Y-%m-%d'), 
                1, self._format_datetime(datetime.now())
            ))
        
        sql = """INSERT INTO product_purchase_prices (id, product_id, supplier_id, purchase_price, moq, discount_rate, valid_from, valid_to, is_active, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, prices)
    
    def _generate_stock_logs(self, count):
        print(f"  生成 stock_logs 表数据 ({count} 条)...")
        
        change_types = ['in', 'out', 'adjust']
        reasons = ['采购入库', '销售出库', '退货入库', '盘点调整', '报损', '领用']
        
        logs = []
        for i in range(1, count + 1):
            product_id = random.randint(1, 200)
            sku_id = random.randint(1, 500)
            warehouse_id = random.randint(1, 8)
            before_stock = random.randint(0, 500)
            change_quantity = random.randint(-50, 100) if random.random() > 0.3 else random.randint(1, 100)
            after_stock = max(0, before_stock + change_quantity)
            order_id = random.randint(1, 300) if random.random() > 0.4 else None
            
            logs.append((
                i, product_id, sku_id, warehouse_id, random.choice(change_types),
                change_quantity, before_stock, after_stock, order_id,
                random.choice(reasons), random.randint(1, 10),
                self._format_datetime(datetime.now() - timedelta(days=random.randint(1, 90)))
            ))
        
        sql = """INSERT INTO stock_logs (id, product_id, sku_id, warehouse_id, change_type, change_quantity, before_stock, after_stock, order_id, reason, operator_id, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql, logs)
    
    def initialize(self, drop_existing=True):
        schema = create_sample_schema()
        
        self.connect()
        
        if drop_existing:
            self.drop_all_tables()
        
        self.create_tables(schema)
        self.create_indexes()
        self.generate_test_data(schema)
        
        print("\n数据库初始化完成!")
        print(f"数据库文件: {self.db_path}")
        print(f"共创建了 {len(schema.tables)} 个表")
        print("数据摘要:")
        print("  - 用户: 50")
        print("  - 地址: 100")
        print("  - 分类: 15")
        print("  - 品牌: 30")
        print("  - 商品: 200")
        print("  - SKU: 500")
        print("  - 订单: 300")
        print("  - 订单明细: 800")
        print("  - 支付记录: 300")
        print("  - 优惠券: 50")
        print("  - 用户优惠券: 200")
        print("  - 商品评价: 500")
        print("  - 购物车: 100")
        print("  - 收藏: 150")
        print("  - 商品规格: 200")
        print("  - 秒杀活动: 5")
        print("  - 秒杀商品: 100")
        print("  - 用户行为: 1000")
        print("  - 商品标签: 30")
        print("  - 标签关联: 300")
        print("  - 管理员: 10")
        print("  - 操作日志: 200")
        print("  - 配送方式: 5")
        print("  - 仓库: 8")
        print("  - 供应商: 20")
        print("  - 采购价格: 200")
        print("  - 库存流水: 500")
        
        self.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='初始化NL2SQL测试数据库(SQLite)')
    parser.add_argument('--db-path', '-d', type=str, default=None,
                       help='数据库文件路径，默认为 nl2sql_test.db')
    parser.add_argument('--keep', action='store_true',
                       help='保留现有数据，不删除重建')
    args = parser.parse_args()
    
    initializer = DatabaseInitializer(args.db_path)
    initializer.initialize(drop_existing=not args.keep)


if __name__ == "__main__":
    main()
