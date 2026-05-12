from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseSchema:
    tables: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relations: List[Dict[str, str]] = field(default_factory=list)
    field_mappings: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseSchema':
        tables = data.get('tables', {})
        relations = data.get('relations', [])
        field_mappings = data.get('field_mappings', {})
        return cls(tables=tables, relations=relations, field_mappings=field_mappings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tables': self.tables,
            'relations': self.relations,
            'field_mappings': self.field_mappings
        }

    def get_table_columns(self, table_name: str) -> List[str]:
        table_info = self.tables.get(table_name, {})
        return table_info.get('columns', [])

    def get_table_description(self, table_name: str) -> Optional[str]:
        return self.tables.get(table_name, {}).get('description')

    def get_column_description(self, table_name: str, column_name: str) -> Optional[str]:
        column_descriptions = self.tables.get(table_name, {}).get('column_descriptions', {})
        return column_descriptions.get(column_name)

    def get_column_type(self, table_name: str, column_name: str) -> Optional[str]:
        column_types = self.tables.get(table_name, {}).get('column_types', {})
        return column_types.get(column_name)

    def get_field_mappings(self) -> Dict[str, Dict[str, str]]:
        return self.field_mappings

    def get_field_mapping_prompt(self) -> str:
        if not self.field_mappings:
            return ""
        
        lines = []
        for table, mappings in self.field_mappings.items():
            lines.append(f"- {table}表:")
            for wrong_name, correct_name in mappings.items():
                lines.append(f"  - {wrong_name} -> {correct_name}")
        
        return "字段别名映射说明:\n" + "\n".join(lines)

    def get_relations_for_table(self, table_name: str) -> List[Dict[str, str]]:
        relations = []
        for rel in self.relations:
            if rel.get('from_table') == table_name or rel.get('to_table') == table_name:
                relations.append(rel)
        return relations

    def get_table_names(self) -> List[str]:
        return list(self.tables.keys())


def create_sample_schema() -> DatabaseSchema:
    return DatabaseSchema(
        tables={
            'users': {
                'description': '用户表，存储会员基本信息',
                'columns': ['id', 'username', 'password', 'real_name', 'email', 'phone', 'gender', 'birthday', 'avatar_url', 'status', 'user_level', 'total_points', 'registered_at', 'last_login_at', 'address_id'],
                'column_descriptions': {
                    'id': '用户ID',
                    'username': '用户名',
                    'password': '密码',
                    'real_name': '真实姓名',
                    'email': '电子邮箱',
                    'phone': '手机号码',
                    'gender': '性别',
                    'birthday': '出生日期',
                    'avatar_url': '头像URL',
                    'status': '账号状态',
                    'user_level': '会员等级',
                    'total_points': '积分余额',
                    'registered_at': '注册时间',
                    'last_login_at': '最后登录时间',
                    'address_id': '默认地址ID'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'username': 'VARCHAR(50)',
                    'password': 'VARCHAR(255)',
                    'real_name': 'VARCHAR(100)',
                    'email': 'VARCHAR(100)',
                    'phone': 'VARCHAR(20)',
                    'gender': 'VARCHAR(10)',
                    'birthday': 'DATE',
                    'avatar_url': 'VARCHAR(500)',
                    'status': 'VARCHAR(20)',
                    'user_level': 'INTEGER',
                    'total_points': 'INTEGER',
                    'registered_at': 'TIMESTAMP',
                    'last_login_at': 'TIMESTAMP',
                    'address_id': 'INTEGER'
                }
            },
            'addresses': {
                'description': '收货地址表',
                'columns': ['id', 'user_id', 'receiver_name', 'phone', 'province', 'city', 'district', 'detail_address', 'postal_code', 'is_default', 'created_at'],
                'column_descriptions': {
                    'id': '地址ID',
                    'user_id': '用户ID',
                    'receiver_name': '收货人姓名',
                    'phone': '联系电话',
                    'province': '省份',
                    'city': '城市',
                    'district': '区县',
                    'detail_address': '详细地址',
                    'postal_code': '邮政编码',
                    'is_default': '是否默认地址',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'receiver_name': 'VARCHAR(100)',
                    'phone': 'VARCHAR(20)',
                    'province': 'VARCHAR(50)',
                    'city': 'VARCHAR(50)',
                    'district': 'VARCHAR(50)',
                    'detail_address': 'VARCHAR(255)',
                    'postal_code': 'VARCHAR(10)',
                    'is_default': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'categories': {
                'description': '商品分类表',
                'columns': ['id', 'parent_id', 'name', 'description', 'icon_url', 'sort_order', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '分类ID',
                    'parent_id': '父分类ID',
                    'name': '分类名称',
                    'description': '分类描述',
                    'icon_url': '分类图标',
                    'sort_order': '排序权重',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'parent_id': 'INTEGER',
                    'name': 'VARCHAR(100)',
                    'description': 'VARCHAR(500)',
                    'icon_url': 'VARCHAR(500)',
                    'sort_order': 'INTEGER',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'products': {
                'description': '商品表',
                'columns': ['id', 'category_id', 'brand_id', 'name', 'subtitle', 'description', 'price', 'original_price', 'cost', 'stock', 'stock_alert', 'unit', 'weight', 'barcode', 'main_image', 'images', 'is_on_sale', 'is_hot', 'is_new', 'is_recommend', 'sales_count', 'view_count', 'rating', 'created_at', 'updated_at'],
                'column_descriptions': {
                    'id': '商品ID',
                    'category_id': '分类ID',
                    'brand_id': '品牌ID',
                    'name': '商品名称',
                    'subtitle': '商品副标题',
                    'description': '商品描述',
                    'price': '售价',
                    'original_price': '原价',
                    'cost': '成本价',
                    'stock': '库存数量',
                    'stock_alert': '库存预警值',
                    'unit': '单位',
                    'weight': '重量(kg)',
                    'barcode': '条形码',
                    'main_image': '主图URL',
                    'images': '图片列表JSON',
                    'is_on_sale': '是否上架',
                    'is_hot': '是否热销',
                    'is_new': '是否新品',
                    'is_recommend': '是否推荐',
                    'sales_count': '销量',
                    'view_count': '浏览量',
                    'rating': '评分',
                    'created_at': '创建时间',
                    'updated_at': '更新时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'category_id': 'INTEGER',
                    'brand_id': 'INTEGER',
                    'name': 'VARCHAR(200)',
                    'subtitle': 'VARCHAR(500)',
                    'description': 'TEXT',
                    'price': 'DECIMAL(10,2)',
                    'original_price': 'DECIMAL(10,2)',
                    'cost': 'DECIMAL(10,2)',
                    'stock': 'INTEGER',
                    'stock_alert': 'INTEGER',
                    'unit': 'VARCHAR(20)',
                    'weight': 'DECIMAL(8,3)',
                    'barcode': 'VARCHAR(50)',
                    'main_image': 'VARCHAR(500)',
                    'images': 'JSON',
                    'is_on_sale': 'BOOLEAN',
                    'is_hot': 'BOOLEAN',
                    'is_new': 'BOOLEAN',
                    'is_recommend': 'BOOLEAN',
                    'sales_count': 'INTEGER',
                    'view_count': 'INTEGER',
                    'rating': 'DECIMAL(3,2)',
                    'created_at': 'TIMESTAMP',
                    'updated_at': 'TIMESTAMP'
                }
            },
            'brands': {
                'description': '品牌表',
                'columns': ['id', 'name', 'logo_url', 'description', 'country', 'website', 'sort_order', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '品牌ID',
                    'name': '品牌名称',
                    'logo_url': '品牌Logo',
                    'description': '品牌描述',
                    'country': '国家',
                    'website': '官网地址',
                    'sort_order': '排序权重',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(100)',
                    'logo_url': 'VARCHAR(500)',
                    'description': 'VARCHAR(1000)',
                    'country': 'VARCHAR(50)',
                    'website': 'VARCHAR(255)',
                    'sort_order': 'INTEGER',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_skus': {
                'description': '商品SKU表，存储商品规格组合',
                'columns': ['id', 'product_id', 'sku_code', 'specs', 'price', 'stock', 'sales_count', 'image_url', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': 'SKU ID',
                    'product_id': '商品ID',
                    'sku_code': 'SKU编码',
                    'specs': '规格属性JSON',
                    'price': 'SKU价格',
                    'stock': 'SKU库存',
                    'sales_count': 'SKU销量',
                    'image_url': 'SKU图片',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'sku_code': 'VARCHAR(50)',
                    'specs': 'JSON',
                    'price': 'DECIMAL(10,2)',
                    'stock': 'INTEGER',
                    'sales_count': 'INTEGER',
                    'image_url': 'VARCHAR(500)',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'orders': {
                'description': '订单主表',
                'columns': ['id', 'order_no', 'user_id', 'order_status', 'payment_status', 'shipping_status', 'total_amount', 'discount_amount', 'freight_amount', 'pay_amount', 'points_discount', 'coupon_discount', 'address_id', 'shipping_method', 'shipping_no', 'invoice_title', 'remark', 'created_at', 'paid_at', 'shipped_at', 'received_at', 'completed_at', 'canceled_at'],
                'column_descriptions': {
                    'id': '订单ID',
                    'order_no': '订单编号',
                    'user_id': '用户ID',
                    'order_status': '订单状态',
                    'payment_status': '支付状态',
                    'shipping_status': '发货状态',
                    'total_amount': '商品总金额',
                    'discount_amount': '优惠金额',
                    'freight_amount': '运费金额',
                    'pay_amount': '实付金额',
                    'points_discount': '积分抵扣',
                    'coupon_discount': '优惠券抵扣',
                    'address_id': '收货地址ID',
                    'shipping_method': '配送方式',
                    'shipping_no': '快递单号',
                    'invoice_title': '发票抬头',
                    'remark': '订单备注',
                    'created_at': '下单时间',
                    'paid_at': '支付时间',
                    'shipped_at': '发货时间',
                    'received_at': '收货时间',
                    'completed_at': '完成时间',
                    'canceled_at': '取消时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'order_no': 'VARCHAR(32)',
                    'user_id': 'INTEGER',
                    'order_status': 'VARCHAR(20)',
                    'payment_status': 'VARCHAR(20)',
                    'shipping_status': 'VARCHAR(20)',
                    'total_amount': 'DECIMAL(10,2)',
                    'discount_amount': 'DECIMAL(10,2)',
                    'freight_amount': 'DECIMAL(10,2)',
                    'pay_amount': 'DECIMAL(10,2)',
                    'points_discount': 'DECIMAL(10,2)',
                    'coupon_discount': 'DECIMAL(10,2)',
                    'address_id': 'INTEGER',
                    'shipping_method': 'VARCHAR(50)',
                    'shipping_no': 'VARCHAR(100)',
                    'invoice_title': 'VARCHAR(200)',
                    'remark': 'VARCHAR(500)',
                    'created_at': 'TIMESTAMP',
                    'paid_at': 'TIMESTAMP',
                    'shipped_at': 'TIMESTAMP',
                    'received_at': 'TIMESTAMP',
                    'completed_at': 'TIMESTAMP',
                    'canceled_at': 'TIMESTAMP'
                }
            },
            'order_items': {
                'description': '订单明细表',
                'columns': ['id', 'order_id', 'product_id', 'sku_id', 'product_name', 'sku_specs', 'price', 'quantity', 'subtotal', 'discount', 'is_gift', 'created_at'],
                'column_descriptions': {
                    'id': '明细ID',
                    'order_id': '订单ID',
                    'product_id': '商品ID',
                    'sku_id': 'SKU ID',
                    'product_name': '商品名称',
                    'sku_specs': 'SKU规格',
                    'price': '商品单价',
                    'quantity': '购买数量',
                    'subtotal': '小计金额',
                    'discount': '优惠金额',
                    'is_gift': '是否赠品',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'order_id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'sku_id': 'INTEGER',
                    'product_name': 'VARCHAR(200)',
                    'sku_specs': 'VARCHAR(500)',
                    'price': 'DECIMAL(10,2)',
                    'quantity': 'INTEGER',
                    'subtotal': 'DECIMAL(10,2)',
                    'discount': 'DECIMAL(10,2)',
                    'is_gift': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'payments': {
                'description': '支付记录表',
                'columns': ['id', 'payment_no', 'order_id', 'user_id', 'payment_method', 'amount', 'status', 'transaction_id', 'paid_at', 'created_at'],
                'column_descriptions': {
                    'id': '支付ID',
                    'payment_no': '支付流水号',
                    'order_id': '订单ID',
                    'user_id': '用户ID',
                    'payment_method': '支付方式',
                    'amount': '支付金额',
                    'status': '支付状态',
                    'transaction_id': '第三方交易号',
                    'paid_at': '支付时间',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'payment_no': 'VARCHAR(64)',
                    'order_id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'payment_method': 'VARCHAR(50)',
                    'amount': 'DECIMAL(10,2)',
                    'status': 'VARCHAR(20)',
                    'transaction_id': 'VARCHAR(100)',
                    'paid_at': 'TIMESTAMP',
                    'created_at': 'TIMESTAMP'
                }
            },
            'coupons': {
                'description': '优惠券表',
                'columns': ['id', 'name', 'type', 'amount', 'min_amount', 'discount', 'max_discount', 'total_count', 'remain_count', 'per_limit', 'start_at', 'end_at', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '优惠券ID',
                    'name': '优惠券名称',
                    'type': '优惠券类型',
                    'amount': '面额',
                    'min_amount': '使用门槛',
                    'discount': '折扣率',
                    'max_discount': '最高优惠',
                    'total_count': '发放总量',
                    'remain_count': '剩余数量',
                    'per_limit': '每人限领',
                    'start_at': '开始时间',
                    'end_at': '结束时间',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(100)',
                    'type': 'VARCHAR(20)',
                    'amount': 'DECIMAL(10,2)',
                    'min_amount': 'DECIMAL(10,2)',
                    'discount': 'DECIMAL(5,2)',
                    'max_discount': 'DECIMAL(10,2)',
                    'total_count': 'INTEGER',
                    'remain_count': 'INTEGER',
                    'per_limit': 'INTEGER',
                    'start_at': 'TIMESTAMP',
                    'end_at': 'TIMESTAMP',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'user_coupons': {
                'description': '用户优惠券表',
                'columns': ['id', 'user_id', 'coupon_id', 'order_id', 'status', 'received_at', 'used_at'],
                'column_descriptions': {
                    'id': '用户优惠券ID',
                    'user_id': '用户ID',
                    'coupon_id': '优惠券ID',
                    'order_id': '使用订单ID',
                    'status': '状态',
                    'received_at': '领取时间',
                    'used_at': '使用时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'coupon_id': 'INTEGER',
                    'order_id': 'INTEGER',
                    'status': 'VARCHAR(20)',
                    'received_at': 'TIMESTAMP',
                    'used_at': 'TIMESTAMP'
                }
            },
            'product_reviews': {
                'description': '商品评价表',
                'columns': ['id', 'order_id', 'order_item_id', 'product_id', 'user_id', 'rating', 'content', 'images', 'reply', 'reply_at', 'is_anonymous', 'is_show', 'like_count', 'created_at'],
                'column_descriptions': {
                    'id': '评价ID',
                    'order_id': '订单ID',
                    'order_item_id': '订单明细ID',
                    'product_id': '商品ID',
                    'user_id': '用户ID',
                    'rating': '评分',
                    'content': '评价内容',
                    'images': '评价图片',
                    'reply': '商家回复',
                    'reply_at': '回复时间',
                    'is_anonymous': '是否匿名',
                    'is_show': '是否显示',
                    'like_count': '点赞数',
                    'created_at': '评价时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'order_id': 'INTEGER',
                    'order_item_id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'rating': 'INTEGER',
                    'content': 'TEXT',
                    'images': 'JSON',
                    'reply': 'TEXT',
                    'reply_at': 'TIMESTAMP',
                    'is_anonymous': 'BOOLEAN',
                    'is_show': 'BOOLEAN',
                    'like_count': 'INTEGER',
                    'created_at': 'TIMESTAMP'
                }
            },
            'shopping_carts': {
                'description': '购物车表',
                'columns': ['id', 'user_id', 'product_id', 'sku_id', 'quantity', 'selected', 'created_at', 'updated_at'],
                'column_descriptions': {
                    'id': '购物车ID',
                    'user_id': '用户ID',
                    'product_id': '商品ID',
                    'sku_id': 'SKU ID',
                    'quantity': '数量',
                    'selected': '是否选中',
                    'created_at': '添加时间',
                    'updated_at': '更新时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'sku_id': 'INTEGER',
                    'quantity': 'INTEGER',
                    'selected': 'BOOLEAN',
                    'created_at': 'TIMESTAMP',
                    'updated_at': 'TIMESTAMP'
                }
            },
            'product_favorites': {
                'description': '商品收藏表',
                'columns': ['id', 'user_id', 'product_id', 'created_at'],
                'column_descriptions': {
                    'id': '收藏ID',
                    'user_id': '用户ID',
                    'product_id': '商品ID',
                    'created_at': '收藏时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_specs': {
                'description': '商品规格表',
                'columns': ['id', 'product_id', 'name', 'values', 'is_color', 'is_size', 'sort_order'],
                'column_descriptions': {
                    'id': '规格ID',
                    'product_id': '商品ID',
                    'name': '规格名称',
                    'values': '规格值列表JSON',
                    'is_color': '是否颜色规格',
                    'is_size': '是否尺寸规格',
                    'sort_order': '排序'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'name': 'VARCHAR(50)',
                    'values': 'JSON',
                    'is_color': 'BOOLEAN',
                    'is_size': 'BOOLEAN',
                    'sort_order': 'INTEGER'
                }
            },
            'flash_sales': {
                'description': '限时秒杀活动表',
                'columns': ['id', 'name', 'start_time', 'end_time', 'status', 'created_at'],
                'column_descriptions': {
                    'id': '活动ID',
                    'name': '活动名称',
                    'start_time': '开始时间',
                    'end_time': '结束时间',
                    'status': '活动状态',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(200)',
                    'start_time': 'TIMESTAMP',
                    'end_time': 'TIMESTAMP',
                    'status': 'VARCHAR(20)',
                    'created_at': 'TIMESTAMP'
                }
            },
            'flash_sale_products': {
                'description': '秒杀商品表',
                'columns': ['id', 'flash_sale_id', 'product_id', 'sku_id', 'flash_price', 'stock', 'sold_count', 'limit_per_user', 'created_at'],
                'column_descriptions': {
                    'id': '秒杀商品ID',
                    'flash_sale_id': '活动ID',
                    'product_id': '商品ID',
                    'sku_id': 'SKU ID',
                    'flash_price': '秒杀价',
                    'stock': '秒杀库存',
                    'sold_count': '已售数量',
                    'limit_per_user': '每人限购',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'flash_sale_id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'sku_id': 'INTEGER',
                    'flash_price': 'DECIMAL(10,2)',
                    'stock': 'INTEGER',
                    'sold_count': 'INTEGER',
                    'limit_per_user': 'INTEGER',
                    'created_at': 'TIMESTAMP'
                }
            },
            'user_behaviors': {
                'description': '用户行为日志表',
                'columns': ['id', 'user_id', 'behavior_type', 'target_type', 'target_id', 'duration', 'source', 'ip_address', 'device_info', 'location', 'referer_url', 'created_at'],
                'column_descriptions': {
                    'id': '日志ID',
                    'user_id': '用户ID',
                    'behavior_type': '行为类型(浏览/收藏/加购/搜索)',
                    'target_type': '目标类型(商品/分类/品牌)',
                    'target_id': '目标ID',
                    'duration': '停留时长(秒)',
                    'source': '来源渠道',
                    'ip_address': 'IP地址',
                    'device_info': '设备信息JSON',
                    'location': '地理位置',
                    'referer_url': '来源URL',
                    'created_at': '发生时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'user_id': 'INTEGER',
                    'behavior_type': 'VARCHAR(20)',
                    'target_type': 'VARCHAR(20)',
                    'target_id': 'INTEGER',
                    'duration': 'INTEGER',
                    'source': 'VARCHAR(50)',
                    'ip_address': 'VARCHAR(45)',
                    'device_info': 'JSON',
                    'location': 'VARCHAR(100)',
                    'referer_url': 'VARCHAR(500)',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_tags': {
                'description': '商品标签表',
                'columns': ['id', 'name', 'color', 'description', 'sort_order', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '标签ID',
                    'name': '标签名称',
                    'color': '标签颜色',
                    'description': '标签描述',
                    'sort_order': '排序权重',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(50)',
                    'color': 'VARCHAR(20)',
                    'description': 'VARCHAR(200)',
                    'sort_order': 'INTEGER',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_tag_mapping': {
                'description': '商品标签关联表',
                'columns': ['id', 'product_id', 'tag_id', 'created_at'],
                'column_descriptions': {
                    'id': '关联ID',
                    'product_id': '商品ID',
                    'tag_id': '标签ID',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'tag_id': 'INTEGER',
                    'created_at': 'TIMESTAMP'
                }
            },
            'admin_users': {
                'description': '管理员表',
                'columns': ['id', 'username', 'password', 'real_name', 'email', 'phone', 'role', 'permissions', 'status', 'last_login_at', 'created_at'],
                'column_descriptions': {
                    'id': '管理员ID',
                    'username': '用户名',
                    'password': '密码',
                    'real_name': '真实姓名',
                    'email': '电子邮箱',
                    'phone': '手机号码',
                    'role': '角色',
                    'permissions': '权限JSON',
                    'status': '账号状态',
                    'last_login_at': '最后登录时间',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'username': 'VARCHAR(50)',
                    'password': 'VARCHAR(255)',
                    'real_name': 'VARCHAR(100)',
                    'email': 'VARCHAR(100)',
                    'phone': 'VARCHAR(20)',
                    'role': 'VARCHAR(50)',
                    'permissions': 'JSON',
                    'status': 'VARCHAR(20)',
                    'last_login_at': 'TIMESTAMP',
                    'created_at': 'TIMESTAMP'
                }
            },
            'admin_logs': {
                'description': '管理员操作日志表',
                'columns': ['id', 'admin_id', 'action', 'module', 'target_type', 'target_id', 'old_value', 'new_value', 'ip_address', 'user_agent', 'created_at'],
                'column_descriptions': {
                    'id': '日志ID',
                    'admin_id': '管理员ID',
                    'action': '操作类型',
                    'module': '操作模块',
                    'target_type': '目标类型',
                    'target_id': '目标ID',
                    'old_value': '旧值JSON',
                    'new_value': '新值JSON',
                    'ip_address': 'IP地址',
                    'user_agent': '用户代理',
                    'created_at': '操作时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'admin_id': 'INTEGER',
                    'action': 'VARCHAR(50)',
                    'module': 'VARCHAR(50)',
                    'target_type': 'VARCHAR(50)',
                    'target_id': 'INTEGER',
                    'old_value': 'JSON',
                    'new_value': 'JSON',
                    'ip_address': 'VARCHAR(45)',
                    'user_agent': 'VARCHAR(500)',
                    'created_at': 'TIMESTAMP'
                }
            },
            'stock_logs': {
                'description': '库存流水表',
                'columns': ['id', 'product_id', 'sku_id', 'warehouse_id', 'change_type', 'change_quantity', 'before_stock', 'after_stock', 'order_id', 'reason', 'operator_id', 'created_at'],
                'column_descriptions': {
                    'id': '流水ID',
                    'product_id': '商品ID',
                    'sku_id': 'SKU ID',
                    'warehouse_id': '仓库ID',
                    'change_type': '变动类型(入库/出库/调整)',
                    'change_quantity': '变动数量',
                    'before_stock': '变动前库存',
                    'after_stock': '变动后库存',
                    'order_id': '关联订单ID',
                    'reason': '变动原因',
                    'operator_id': '操作人ID',
                    'created_at': '变动时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'sku_id': 'INTEGER',
                    'warehouse_id': 'INTEGER',
                    'change_type': 'VARCHAR(20)',
                    'change_quantity': 'INTEGER',
                    'before_stock': 'INTEGER',
                    'after_stock': 'INTEGER',
                    'order_id': 'INTEGER',
                    'reason': 'VARCHAR(200)',
                    'operator_id': 'INTEGER',
                    'created_at': 'TIMESTAMP'
                }
            },
            'shipping_methods': {
                'description': '配送方式表',
                'columns': ['id', 'name', 'carrier', 'base_fee', 'weight_fee_per_kg', 'free_shipping_threshold', 'estimated_days', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '方式ID',
                    'name': '配送方式名称',
                    'carrier': '承运商',
                    'base_fee': '基础费用',
                    'weight_fee_per_kg': '续重费用/千克',
                    'free_shipping_threshold': '免费配送门槛',
                    'estimated_days': '预计天数',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(50)',
                    'carrier': 'VARCHAR(100)',
                    'base_fee': 'DECIMAL(10,2)',
                    'weight_fee_per_kg': 'DECIMAL(10,2)',
                    'free_shipping_threshold': 'DECIMAL(10,2)',
                    'estimated_days': 'INTEGER',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'warehouses': {
                'description': '仓库表',
                'columns': ['id', 'name', 'province', 'city', 'district', 'address', 'contact', 'phone', 'capacity', 'used_capacity', 'manager_id', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '仓库ID',
                    'name': '仓库名称',
                    'province': '省份',
                    'city': '城市',
                    'district': '区县',
                    'address': '详细地址',
                    'contact': '联系人',
                    'phone': '联系电话',
                    'capacity': '总容量',
                    'used_capacity': '已用容量',
                    'manager_id': '仓库管理员ID',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(100)',
                    'province': 'VARCHAR(50)',
                    'city': 'VARCHAR(50)',
                    'district': 'VARCHAR(50)',
                    'address': 'VARCHAR(255)',
                    'contact': 'VARCHAR(100)',
                    'phone': 'VARCHAR(20)',
                    'capacity': 'INTEGER',
                    'used_capacity': 'INTEGER',
                    'manager_id': 'INTEGER',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_suppliers': {
                'description': '商品供应商表',
                'columns': ['id', 'name', 'contact_person', 'phone', 'email', 'address', 'payment_terms', 'lead_time_days', 'rating', 'status', 'created_at'],
                'column_descriptions': {
                    'id': '供应商ID',
                    'name': '供应商名称',
                    'contact_person': '联系人',
                    'phone': '联系电话',
                    'email': '电子邮箱',
                    'address': '地址',
                    'payment_terms': '付款条款',
                    'lead_time_days': '交货周期(天)',
                    'rating': '供应商评分',
                    'status': '合作状态',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'name': 'VARCHAR(200)',
                    'contact_person': 'VARCHAR(100)',
                    'phone': 'VARCHAR(20)',
                    'email': 'VARCHAR(100)',
                    'address': 'VARCHAR(255)',
                    'payment_terms': 'VARCHAR(100)',
                    'lead_time_days': 'INTEGER',
                    'rating': 'DECIMAL(3,2)',
                    'status': 'VARCHAR(20)',
                    'created_at': 'TIMESTAMP'
                }
            },
            'product_purchase_prices': {
                'description': '商品采购价格表',
                'columns': ['id', 'product_id', 'supplier_id', 'purchase_price', 'moq', 'discount_rate', 'valid_from', 'valid_to', 'is_active', 'created_at'],
                'column_descriptions': {
                    'id': '采购价ID',
                    'product_id': '商品ID',
                    'supplier_id': '供应商ID',
                    'purchase_price': '采购价格',
                    'moq': '最小订购量',
                    'discount_rate': '折扣率',
                    'valid_from': '生效开始日期',
                    'valid_to': '生效结束日期',
                    'is_active': '是否启用',
                    'created_at': '创建时间'
                },
                'column_types': {
                    'id': 'INTEGER',
                    'product_id': 'INTEGER',
                    'supplier_id': 'INTEGER',
                    'purchase_price': 'DECIMAL(10,2)',
                    'moq': 'INTEGER',
                    'discount_rate': 'DECIMAL(5,2)',
                    'valid_from': 'DATE',
                    'valid_to': 'DATE',
                    'is_active': 'BOOLEAN',
                    'created_at': 'TIMESTAMP'
                }
            }
        },
        relations=[
            {'from_table': 'addresses', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'products', 'from_field': 'category_id', 'to_table': 'categories', 'to_field': 'id'},
            {'from_table': 'products', 'from_field': 'brand_id', 'to_table': 'brands', 'to_field': 'id'},
            {'from_table': 'product_skus', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'orders', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'orders', 'from_field': 'address_id', 'to_table': 'addresses', 'to_field': 'id'},
            {'from_table': 'order_items', 'from_field': 'order_id', 'to_table': 'orders', 'to_field': 'id'},
            {'from_table': 'order_items', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'order_items', 'from_field': 'sku_id', 'to_table': 'product_skus', 'to_field': 'id'},
            {'from_table': 'payments', 'from_field': 'order_id', 'to_table': 'orders', 'to_field': 'id'},
            {'from_table': 'payments', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'user_coupons', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'user_coupons', 'from_field': 'coupon_id', 'to_table': 'coupons', 'to_field': 'id'},
            {'from_table': 'user_coupons', 'from_field': 'order_id', 'to_table': 'orders', 'to_field': 'id'},
            {'from_table': 'product_reviews', 'from_field': 'order_id', 'to_table': 'orders', 'to_field': 'id'},
            {'from_table': 'product_reviews', 'from_field': 'order_item_id', 'to_table': 'order_items', 'to_field': 'id'},
            {'from_table': 'product_reviews', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'product_reviews', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'shopping_carts', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'shopping_carts', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'shopping_carts', 'from_field': 'sku_id', 'to_table': 'product_skus', 'to_field': 'id'},
            {'from_table': 'product_favorites', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'product_favorites', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'product_specs', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'flash_sale_products', 'from_field': 'flash_sale_id', 'to_table': 'flash_sales', 'to_field': 'id'},
            {'from_table': 'flash_sale_products', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'flash_sale_products', 'from_field': 'sku_id', 'to_table': 'product_skus', 'to_field': 'id'},
            {'from_table': 'categories', 'from_field': 'parent_id', 'to_table': 'categories', 'to_field': 'id'},
            {'from_table': 'user_behaviors', 'from_field': 'user_id', 'to_table': 'users', 'to_field': 'id'},
            {'from_table': 'product_tag_mapping', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'product_tag_mapping', 'from_field': 'tag_id', 'to_table': 'product_tags', 'to_field': 'id'},
            {'from_table': 'admin_logs', 'from_field': 'admin_id', 'to_table': 'admin_users', 'to_field': 'id'},
            {'from_table': 'stock_logs', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'stock_logs', 'from_field': 'sku_id', 'to_table': 'product_skus', 'to_field': 'id'},
            {'from_table': 'stock_logs', 'from_field': 'order_id', 'to_table': 'orders', 'to_field': 'id'},
            {'from_table': 'stock_logs', 'from_field': 'operator_id', 'to_table': 'admin_users', 'to_field': 'id'},
            {'from_table': 'warehouses', 'from_field': 'manager_id', 'to_table': 'admin_users', 'to_field': 'id'},
            {'from_table': 'product_purchase_prices', 'from_field': 'product_id', 'to_table': 'products', 'to_field': 'id'},
            {'from_table': 'product_purchase_prices', 'from_field': 'supplier_id', 'to_table': 'product_suppliers', 'to_field': 'id'},
            {'from_table': 'stock_logs', 'from_field': 'warehouse_id', 'to_table': 'warehouses', 'to_field': 'id'}
        ],
        field_mappings={
            'orders': {
                'amount': 'pay_amount',
                'total_amount': 'pay_amount',
                'order_amount': 'pay_amount'
            },
            'stock_logs': {
                'stock': 'change_quantity',
                'quantity': 'change_quantity',
                'warehouse': 'warehouse_id'
            },
            'products': {
                'cost_price': 'cost',
                'profit': '(price - cost)'
            }
        }
    )
