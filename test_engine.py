#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from nl2sql.core.engine import NL2SQLEngine
from nl2sql.core.schema import create_sample_schema
from nl2sql.config.config import EngineConfig


class DatabaseExecutor:
    def __init__(self, config):
        self.conn = None
        
        db_config = config.database.connection
        sqlite_path = db_config.get('sqlite_path', 'nl2sql_test.db') if db_config else 'nl2sql_test.db'
        
        if not os.path.isabs(sqlite_path):
            sqlite_path = os.path.join(current_dir, sqlite_path)
        
        try:
            import sqlite3
            self.sqlite3 = sqlite3
            self.conn = sqlite3.connect(sqlite_path)
            self.conn.row_factory = sqlite3.Row
            print(f"数据库连接成功: {sqlite_path}")
        except Exception as e:
            print(f"警告: 数据库连接失败: {e}")
            print("将仅展示SQL，不执行验证")
            self.conn = None
    
    def execute(self, sql):
        if not self.conn:
            return None, "数据库未连接"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            
            if sql.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                cursor.close()
                return rows, None
            else:
                cursor.close()
                return None, "非查询语句"
        except Exception as e:
            return None, str(e)
    
    def close(self):
        if self.conn:
            self.conn.close()


def main():
    schema = create_sample_schema()
    
    config_path = os.path.join(current_dir, 'config', 'default.yaml')
    config = EngineConfig.from_yaml(config_path)
    
    engine = NL2SQLEngine(schema=schema, config=config)
    db_executor = DatabaseExecutor(config)

    test_queries = [
        "查询所有用户的用户名和邮箱",
        "查找年龄大于25岁的用户",
        "统计每个用户的订单总数",
        "查询价格最高的5个商品",
        "查看状态为已完成的订单",
        "查询所有订单及其对应的用户姓名",
        "查询每个用户购买的所有商品名称",
        "查询库存低于10的商品",
        "统计每个分类的商品数量",
        "查询用户名为张三的订单",
        "查询2024年之后的注册用户",
        "统计每个品牌的商品数量",
        "查询热销商品(销量前10)",
        "查询用户收藏的所有商品",
        "查询购物车中的商品",
        "查询用户已使用的优惠券",
        "查询商品的评价信息",
        "查询每个商品的平均评分",
        "查询限时秒杀活动中的商品",
        "查询订单总金额超过1000元的订单",
        "查询使用了优惠券的订单",
        "查询每个用户的累计消费金额",
        "查询同时购买了商品A和商品B的用户",
        "查询近7天登录过的用户",
        "查询分类为电子产品的商品",
        "查询库存变动的商品记录",
        "统计每个仓库的库存总量",
        "查询所有启用的配送方式",
        "查询商品带有的所有标签",
        "查询某个管理员的所有操作日志",
        "统计每个供应商的商品数量",
        "查询采购价格低于100的商品",
        "查询用户浏览次数最多的商品",
        "查询订单中包含赠品的订单",
        "统计每个商品分类的平均价格",
        "查询同时有库存和销量大于100的商品",
        "查询用户最近一周的行为记录",
        "查询被标记为热门的商品有哪些",
        "查询利润最高的商品(售价-成本)",
        "统计每个品牌的平均评分",
        "查询供应商评分高于4.5的供应商",
        "查询今天创建的订单数量",
        "查询每个用户平均订单金额"
    ]
    
    print("=" * 60)
    print("NL2DSL2SQL 智能引擎测试")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for query in test_queries:
        print(f"输入: {query}")
        print("-" * 40)
        
        result = engine.process(query)
        
        if result.success:
            print(f"SQL: {result.sql}")
            print(f"耗时: {result.duration:.2f}ms")
            
            if db_executor.conn:
                rows, error = db_executor.execute(result.sql)
                if error:
                    print(f"执行结果: 错误 - {error}")
                    fail_count += 1
                else:
                    print(f"执行结果: 成功 - {len(rows)} 条记录")
                    if rows and len(rows) > 0:
                        print(f"示例数据: {rows[0]}")
                    success_count += 1
            else:
                print("执行结果: 数据库未连接")
            
            if result.explanation:
                print(f"解释: {result.explanation}")
        else:
            print(f"错误: {result.error}")
            fail_count += 1
        
        print()
        print("=" * 60)
        print()
    
    if db_executor.conn:
        db_executor.close()
    
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"总测试数: {len(test_queries)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/len(test_queries)*100:.1f}%")


if __name__ == "__main__":
    main()
