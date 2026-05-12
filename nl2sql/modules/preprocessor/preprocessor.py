import re
from typing import Dict, List, Optional, Any


class QueryNormalizer:
    def __init__(self):
        self._special_chars_pattern = re.compile(r'[^\w\s\u4e00-\u9fff]')
        self._multiple_spaces_pattern = re.compile(r'\s+')

    def normalize(self, query: str) -> str:
        query = query.strip()
        query = self._special_chars_pattern.sub(' ', query)
        query = self._multiple_spaces_pattern.sub(' ', query)
        return query

    def to_lowercase_keywords(self, query: str) -> str:
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'ORDER BY', 'GROUP BY', 'HAVING', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
        result = query
        for keyword in keywords:
            result = re.sub(r'\b' + keyword + r'\b', keyword.lower(), result, flags=re.IGNORECASE)
        return result


class EntityRecognizer:
    def __init__(self):
        self._table_keywords = ['表', 'table', '数据表', '表名']
        self._field_keywords = ['字段', 'field', '列', 'column', '属性']
        self._table_keyword_map = {
            '用户': 'users',
            '会员': 'users',
            '订单': 'orders',
            '商品': 'products',
            '产品': 'products',
            '明细': 'order_items',
            '地址': 'addresses',
            '收货地址': 'addresses',
            '分类': 'categories',
            '商品分类': 'categories',
            '品牌': 'brands',
            'SKU': 'product_skus',
            '规格': 'product_skus',
            '支付': 'payments',
            '付款': 'payments',
            '优惠券': 'coupons',
            '评价': 'product_reviews',
            '评论': 'product_reviews',
            '购物车': 'shopping_carts',
            '收藏': 'product_favorites',
            '秒杀': 'flash_sales',
            '限时抢购': 'flash_sales',
            '行为': 'user_behaviors',
            '用户行为': 'user_behaviors',
            '标签': 'product_tags',
            '商品标签': 'product_tags',
            '管理员': 'admin_users',
            '后台用户': 'admin_users',
            '日志': 'admin_logs',
            '操作日志': 'admin_logs',
            '库存': 'stock_logs',
            '库存流水': 'stock_logs',
            '配送': 'shipping_methods',
            '配送方式': 'shipping_methods',
            '仓库': 'warehouses',
            '供应商': 'product_suppliers',
            '采购': 'product_purchase_prices',
            '采购价': 'product_purchase_prices',
        }

    def recognize_tables(self, query: str, schema: Dict[str, Any]) -> List[str]:
        recognized = []
        tables_dict = schema.get('tables', {})
        available_tables = list(tables_dict.keys())
        query_lower = query.lower()
        
        for table in available_tables:
            if table.lower() in query_lower:
                recognized.append(table)
        
        if not recognized:
            for keyword, table in self._table_keyword_map.items():
                if keyword in query and table in available_tables:
                    recognized.append(table)
        
        return recognized

    def recognize_fields(self, query: str, schema: Dict[str, Any]) -> List[str]:
        recognized = []
        all_fields = []
        
        tables_dict = schema.get('tables', {})
        for table, table_info in tables_dict.items():
            fields = table_info.get('columns', [])
            for field in fields:
                all_fields.append(f"{table}.{field}")
                all_fields.append(field)
        
        query_lower = query.lower()
        for field in all_fields:
            if field.lower() in query_lower:
                recognized.append(field)
        
        return recognized


class IntentClassifier:
    def __init__(self):
        self._intent_patterns = {
            'SELECT': [r'查询', r'查找', r'获取', r'select', r'找', r'看看', r'列出', r'统计', r'count', r'sum', r'avg', r'max', r'min'],
            'INSERT': [r'添加', r'插入', r'新增', r'insert', r'创建', r'加入'],
            'UPDATE': [r'更新', r'修改', r'改变', r'update', r'编辑', r'调整'],
            'DELETE': [r'删除', r'移除', r'删除', r'delete', r'清除']
        }

    def classify(self, query: str) -> str:
        query_lower = query.lower()
        
        scores = {}
        for intent, patterns in self._intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            scores[intent] = score
        
        if not scores or max(scores.values()) == 0:
            return 'SELECT'
        
        return max(scores, key=scores.get)


class ContextManager:
    def __init__(self, max_history: int = 10):
        self._history: List[Dict[str, Any]] = []
        self._max_history = max_history

    def add_context(self, query: str, intent: str, tables: List[str]):
        self._history.append({
            'query': query,
            'intent': intent,
            'tables': tables
        })
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def get_last_context(self) -> Optional[Dict[str, Any]]:
        return self._history[-1] if self._history else None

    def get_related_tables(self) -> List[str]:
        tables = []
        for context in self._history:
            tables.extend(context.get('tables', []))
        return list(set(tables))


class Preprocessor:
    def __init__(self, schema: Dict[str, Any]):
        self._schema = schema
        self._normalizer = QueryNormalizer()
        self._entity_recognizer = EntityRecognizer()
        self._intent_classifier = IntentClassifier()
        self._context_manager = ContextManager()

    def process(self, query: str) -> Dict[str, Any]:
        normalized_query = self._normalizer.normalize(query)
        
        intent = self._intent_classifier.classify(normalized_query)
        
        tables = self._entity_recognizer.recognize_tables(normalized_query, self._schema)
        fields = self._entity_recognizer.recognize_fields(normalized_query, self._schema)
        
        self._context_manager.add_context(normalized_query, intent, tables)
        
        return {
            'original_query': query,
            'normalized_query': normalized_query,
            'intent': intent,
            'tables': tables,
            'fields': fields,
            'context': self._context_manager.get_last_context()
        }
