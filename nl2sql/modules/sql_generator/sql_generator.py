from typing import Dict, List, Any, Optional
import re


class DSLToSQLMapper:
    def __init__(self, dialect: str = 'postgresql'):
        self._dialect = dialect
        self._dialect_quirks = {
            'postgresql': {
                'limit': 'LIMIT',
                'concat': '||',
                'escape': "\\\\"
            },
            'mysql': {
                'limit': 'LIMIT',
                'concat': 'CONCAT',
                'escape': "\\\\"
            },
            'sqlite': {
                'limit': 'LIMIT',
                'concat': '||',
                'escape': "\\\\"
            }
        }

    def map(self, dsl) -> str:
        if dsl.operation.upper() == 'SELECT':
            return self._map_select(dsl)
        else:
            raise ValueError(f"Unsupported operation: {dsl.operation}")

    def _map_select(self, dsl) -> str:
        parts = []
        
        parts.append('SELECT')
        
        if dsl.aggregations:
            agg_fields = []
            for agg in dsl.aggregations:
                if agg == 'COUNT':
                    agg_fields.append('COUNT(*)')
                else:
                    agg_fields.append(f"{agg}(*)")
            parts.append(', '.join(agg_fields))
        else:
            if dsl.fields:
                parts.append(', '.join(dsl.fields))
            else:
                parts.append('*')
        
        parts.append('FROM')
        if dsl.joins and len(dsl.tables) > 0:
            parts.append(dsl.tables[0])
        else:
            parts.append(', '.join(dsl.tables))
        
        if dsl.joins:
            for join in dsl.joins:
                join_sql = f"{join.join_type} {join.to_table} ON {join.from_table}.{join.from_field} = {join.to_table}.{join.to_field}"
                parts.append(join_sql)
        
        if dsl.conditions:
            where_parts = []
            for i, cond in enumerate(dsl.conditions):
                if i > 0:
                    where_parts.append(cond.logical)
                
                value = self._format_value(cond.value, cond.operator)
                where_parts.append(f"{cond.field} {cond.operator} {value}")
            
            parts.append('WHERE')
            parts.append(' '.join(where_parts))
        
        if dsl.group_by:
            parts.append('GROUP BY')
            parts.append(', '.join(dsl.group_by))
        
        if dsl.order_by:
            order_parts = []
            for order in dsl.order_by:
                if isinstance(order, dict):
                    field = order.get('field', '')
                    direction = order.get('direction', 'ASC')
                    order_parts.append(f"{field} {direction}")
            if order_parts:
                parts.append('ORDER BY')
                parts.append(', '.join(order_parts))
        
        if dsl.limit is not None:
            parts.append(f"LIMIT {dsl.limit}")
        
        return ' '.join(parts)

    def _format_value(self, value: Any, operator: str) -> str:
        if operator.upper() == 'LIKE':
            return f"'%{value}%'"
        elif isinstance(value, str):
            return f"'{value}'"
        elif value is None:
            return 'NULL'
        else:
            return str(value)


class SQLSyntaxValidator:
    def __init__(self):
        pass

    def validate(self, sql: str) -> tuple[bool, List[str]]:
        errors = []
        
        sql_upper = sql.upper()
        
        if not sql_upper.strip().startswith('SELECT'):
            errors.append("Only SELECT queries are allowed")
            return False, errors
        
        keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE', 'GRANT', 'REVOKE']
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', sql_upper):
                errors.append(f"{keyword} is not allowed")
        
        if errors:
            return False, errors
        
        return True, []


class SQLPerformanceOptimizer:
    def __init__(self):
        pass

    def optimize(self, sql: str) -> str:
        sql = re.sub(r'\s+', ' ', sql)
        
        return sql.strip()


class SQLSecurityChecker:
    def __init__(self):
        self._dangerous_patterns = [
            (r'\bDROP\b', 'DROP statement is not allowed'),
            (r'\bDELETE\b', 'DELETE statement is not allowed'),
            (r'\bTRUNCATE\b', 'TRUNCATE statement is not allowed'),
            (r'\bALTER\b', 'ALTER statement is not allowed'),
            (r'\bGRANT\b', 'GRANT statement is not allowed'),
            (r'\bREVOKE\b', 'REVOKE statement is not allowed'),
            (r'\bEXEC\b', 'EXEC statement is not allowed'),
            (r'\bEXECUTE\b', 'EXECUTE statement is not allowed'),
            (r'\b--\b', 'Inline comment detected'),
            (r'/\*.*\*/', 'Block comment detected'),
        ]

    def check(self, sql: str) -> tuple[bool, List[str]]:
        errors = []
        
        for pattern, message in self._dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                errors.append(message)
        
        if errors:
            return False, errors
        
        return True, []


class SQLGenerator:
    def __init__(self, dialect: str = 'postgresql', config: Dict[str, Any] = None, llm_client=None, schema=None):
        self._dialect = dialect
        self._config = config or {}
        self._mapper = DSLToSQLMapper(dialect)
        self._llm_client = llm_client
        self._syntax_validator = SQLSyntaxValidator()
        self._performance_optimizer = SQLPerformanceOptimizer()
        self._security_checker = SQLSecurityChecker()
        self._schema = schema

    def process(self, dsl) -> str:
        if self._llm_client:
            sql = self._generate_with_llm(dsl)
        else:
            sql = self._mapper.map(dsl)
        
        is_secure, security_errors = self._security_checker.check(sql)
        if not is_secure:
            raise ValueError(f"Security check failed: {security_errors}")
        
        is_valid, syntax_errors = self._syntax_validator.validate(sql)
        if not is_valid:
            raise ValueError(f"SQL syntax validation failed: {syntax_errors}")
        
        sql = self._performance_optimizer.optimize(sql)
        
        return sql
    
    def _generate_with_llm(self, dsl) -> str:
        import json
        dsl_dict = dsl.to_dict()
        dsl_json = json.dumps(dsl_dict, ensure_ascii=False, indent=2)
        
        dialect = self._dialect
        
        field_mapping_prompt = ""
        if self._schema:
            field_mapping_prompt = self._schema.get_field_mapping_prompt()
        
        prompt = f"""你是一个SQL生成器。根据以下DSL（Domain Specific Language）定义，生成对应的SQL查询语句。

DSL定义:
{dsl_json}

当前数据库类型: {dialect}
{field_mapping_prompt}

要求:
1. 只生成SELECT查询语句（禁止INSERT、UPDATE、DELETE等其他任何语句）
2. 根据DSL中的tables, fields, conditions, joins, group_by, order_by, limit等信息生成完整的SQL
3. 根据指定的数据库类型({dialect})生成正确语法:
   - PostgreSQL: 使用 DATE_SUB 的正确语法
   - MySQL: 使用 DATE_SUB(CURDATE(), INTERVAL 25 YEAR)
   - SQLite: 使用 date('now', '-25 years') 或 date('now', '-7 days')
4. 确保SQL语法正确
5. 只返回SQL语句，不要其他内容"""

        try:
            response = self._llm_client.invoke(prompt)
            sql = response.content.strip()
            sql = sql.strip('```sql').strip('```').strip()
            
            sql_upper = sql.upper().strip()
            if not sql_upper.startswith('SELECT'):
                raise ValueError(f"LLM generated non-SELECT SQL: {sql}")
            
            return sql
        except Exception as e:
            return self._mapper.map(dsl)
