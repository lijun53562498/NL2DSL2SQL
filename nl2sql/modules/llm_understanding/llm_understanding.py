from typing import Dict, List, Any, Optional
import json
import re


class LLMParser:
    def __init__(self, llm_client=None, schema: Dict[str, Any] = None):
        self._llm_client = llm_client
        self._schema = schema

    def _filter_schema(self, schema: Dict[str, Any], relevant_tables: List[str]) -> Dict[str, Any]:
        if not relevant_tables:
            return schema
        
        tables_dict = schema.get('tables', {})
        relations = schema.get('relations', [])
        
        filtered_tables = {}
        for table_name in relevant_tables:
            if table_name in tables_dict:
                filtered_tables[table_name] = tables_dict[table_name]
        
        table_set = set(relevant_tables)
        filtered_relations = []
        for rel in relations:
            if rel.get('from_table') in table_set or rel.get('to_table') in table_set:
                filtered_relations.append(rel)
        
        return {
            'tables': filtered_tables,
            'relations': filtered_relations
        }

    def parse(self, query: str, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        if self._llm_client:
            return self._parse_with_llm(query, preprocessed)
        else:
            return self._parse_rule_based(query, preprocessed)

    def _parse_with_llm(self, query: str, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        relevant_tables = preprocessed.get('tables', [])
        
        filtered_schema = self._filter_schema(self._schema, relevant_tables)
        schema_str = json.dumps(filtered_schema, ensure_ascii=False, indent=2)
        
        relations = filtered_schema.get('relations', [])
        relations_str = json.dumps(relations, ensure_ascii=False, indent=2)
        
        prompt = f"""你是一个SQL查询解析器。根据用户的自然语言查询和数据库schema，解析出查询意图。

数据库schema:
{schema_str}

表之间的关联关系:
{relations_str}

用户查询: {query}

请返回JSON格式的解析结果，包含以下字段:
- intent: 查询意图 (只支持SELECT)
- tables: 涉及的表名列表
- fields: 需要查询/操作的字段列表
- conditions: 查询条件列表
- aggregations: 聚合函数列表
- order_by: 排序字段
- group_by: 分组字段
- limit: 限制数量(默认300，最多300条)
- joins: 关联查询信息（多表关联时需要，包含from_table, from_field, to_table, to_field）

只返回JSON，不要其他内容。"""

        try:
            response = self._llm_client.invoke(prompt)
            result = json.loads(response.content)
            
            result['intent'] = 'SELECT'
            
            if result.get('limit') is None:
                result['limit'] = 300
            else:
                result['limit'] = min(int(result['limit']), 300)
            
            return result
        except Exception as e:
            return self._parse_rule_based(query, preprocessed)

    def _parse_rule_based(self, query: str, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'intent': preprocessed.get('intent', 'SELECT'),
            'tables': preprocessed.get('tables', []),
            'fields': preprocessed.get('fields', []),
            'conditions': self._extract_conditions(query),
            'aggregations': self._extract_aggregations(query),
            'order_by': self._extract_order_by(query),
            'group_by': self._extract_group_by(query),
            'limit': self._extract_limit(query)
        }

    def _extract_conditions(self, query: str) -> List[Dict[str, Any]]:
        conditions = []
        operators = {
            '大于': '>', '小于': '<', '等于': '=', '不等于': '!=',
            '大于等于': '>=', '小于等于': '<=', '包含': 'LIKE',
            'gt': '>', 'lt': '<', 'eq': '=', 'ne': '!='
        }

        for op_chinese, op_sql in operators.items():
            if op_chinese in query:
                parts = query.split(op_chinese)
                if len(parts) == 2:
                    field_part = parts[0].strip()
                    value_part = parts[1].strip()
                    if field_part and value_part and not field_part.startswith('DSL'):
                        conditions.append({
                            'field': field_part,
                            'operator': op_sql,
                            'value': value_part
                        })

        return conditions

    def _extract_aggregations(self, query: str) -> List[str]:
        aggs = []
        agg_keywords = {
            '统计': 'COUNT', '数量': 'COUNT', 'count': 'COUNT',
            '求和': 'SUM', '总和': 'SUM', 'sum': 'SUM',
            '平均': 'AVG', '平均值': 'AVG', 'avg': 'AVG',
            '最大': 'MAX', '最大值': 'MAX', 'max': 'MAX',
            '最小': 'MIN', '最小值': 'MIN', 'min': 'MIN'
        }

        for keyword, agg_func in agg_keywords.items():
            if keyword in query:
                aggs.append(agg_func)

        return list(set(aggs))

    def _extract_order_by(self, query: str) -> Optional[Dict[str, str]]:
        order_patterns = [
            r'按(.+?)排序',
            r'按照(.+?)排序',
            r'按(.+?)升序',
            r'按(.+?)降序',
            r'order by (\w+)',
        ]

        for pattern in order_patterns:
            match = re.search(pattern, query)
            if match:
                field = match.group(1)
                direction = 'DESC' if '降序' in match.group(0) else 'ASC'
                return {'field': field, 'direction': direction}

        return None

    def _extract_group_by(self, query: str) -> List[str]:
        group_patterns = [
            r'按(.+?)分组',
            r'按照(.+?)分组',
            r'group by (\w+)',
        ]

        groups = []
        for pattern in group_patterns:
            match = re.search(pattern, query)
            if match:
                groups.append(match.group(1))

        return groups

    def _extract_limit(self, query: str) -> Optional[int]:
        limit_patterns = [
            r'前(\d+)条',
            r'前(\d+)个',
            r'limit (\d+)',
            r'只取(\d+)',
        ]

        for pattern in limit_patterns:
            match = re.search(pattern, query)
            if match:
                limit_val = int(match.group(1))
                return min(limit_val, 300)

        return 300


class IntentExtractor:
    def __init__(self):
        pass

    def extract(self, query: str, preprocessed: Dict[str, Any]) -> str:
        return 'SELECT'


class EntityExtractor:
    def __init__(self, schema: Dict[str, Any]):
        self._schema = schema

    def extract_tables(self, query: str, preprocessed: Dict[str, Any]) -> List[str]:
        if preprocessed.get('tables'):
            return preprocessed['tables']

        tables = []
        tables_dict = self._schema.get('tables', {})
        available_tables = list(tables_dict.keys())
        query_lower = query.lower()

        for table in available_tables:
            if table.lower() in query_lower:
                tables.append(table)

        return tables

    def extract_fields(self, query: str, preprocessed: Dict[str, Any]) -> List[str]:
        if preprocessed.get('fields'):
            return preprocessed.get('fields', [])

        fields = []
        all_fields = []
        
        tables_dict = self._schema.get('tables', {})
        for table, table_info in tables_dict.items():
            field_list = table_info.get('columns', [])
            for field in field_list:
                all_fields.append(field)

        query_lower = query.lower()
        for field in all_fields:
            if field.lower() in query_lower:
                fields.append(field)

        return fields


class RelationReasoner:
    def __init__(self, schema: Dict[str, Any]):
        self._schema = schema

    def infer_joins(self, tables: List[str]) -> List[Dict[str, Any]]:
        joins = []
        relations = self._schema.get('relations', [])

        for relation in relations:
            if relation['from_table'] in tables and relation['to_table'] in tables:
                joins.append({
                    'type': 'INNER JOIN',
                    'from_table': relation['from_table'],
                    'from_field': relation['from_field'],
                    'to_table': relation['to_table'],
                    'to_field': relation['to_field']
                })

        return joins

    def infer_relationships(self, tables: List[str]) -> Dict[str, Any]:
        relationships = {
            'direct_relations': [],
            'indirect_relations': []
        }

        relations = self._schema.get('relations', [])
        for relation in relations:
            if relation['from_table'] in tables or relation['to_table'] in tables:
                relationships['direct_relations'].append(relation)

        return relationships


class LLMUnderstanding:
    def __init__(self, llm_client=None, schema: Dict[str, Any] = None):
        self._schema = schema or {}
        self._llm_client = llm_client
        
        self._parser = LLMParser(llm_client, schema)
        self._intent_extractor = IntentExtractor()
        self._entity_extractor = EntityExtractor(schema)
        self._relation_reasoner = RelationReasoner(schema)

    def process(self, query: str, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        parsed = self._parser.parse(query, preprocessed)
        
        intent = self._intent_extractor.extract(query, preprocessed)
        
        tables = parsed.get('tables') or self._entity_extractor.extract_tables(query, preprocessed)
        fields = parsed.get('fields') or self._entity_extractor.extract_fields(query, preprocessed)
        
        joins = self._relation_reasoner.infer_joins(tables)
        relationships = self._relation_reasoner.infer_relationships(tables)

        return {
            'intent': intent,
            'tables': tables,
            'fields': fields,
            'conditions': parsed.get('conditions', []),
            'aggregations': parsed.get('aggregations', []),
            'order_by': parsed.get('order_by'),
            'group_by': parsed.get('group_by', []),
            'limit': parsed.get('limit'),
            'joins': joins,
            'relationships': relationships,
            'raw_parsing': parsed
        }
