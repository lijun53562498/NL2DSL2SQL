from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Condition:
    field: str
    operator: str
    value: Any
    logical: str = 'AND'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Join:
    join_type: str
    from_table: str
    from_field: str
    to_table: str
    to_field: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DSL:
    operation: str
    tables: List[str]
    fields: List[str] = field(default_factory=list)
    conditions: List[Condition] = field(default_factory=list)
    joins: List[Join] = field(default_factory=list)
    group_by: List[str] = field(default_factory=list)
    order_by: List[Dict[str, str]] = field(default_factory=list)
    limit: Optional[int] = None
    aggregations: List[str] = field(default_factory=list)
    annotations: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'tables': self.tables,
            'fields': self.fields,
            'conditions': [c.to_dict() for c in self.conditions],
            'joins': [j.to_dict() for j in self.joins],
            'group_by': self.group_by,
            'order_by': self.order_by,
            'limit': self.limit,
            'aggregations': self.aggregations,
            'annotations': self.annotations
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class DSLBuilder:
    def __init__(self, schema: Dict[str, Any] = None):
        self._schema = schema or {}

    def build(self, semantic_result: Dict[str, Any]) -> DSL:
        operation = semantic_result.get('intent', 'SELECT')
        
        tables = semantic_result.get('tables', [])
        if not tables and self._schema.get('tables'):
            tables = [list(self._schema['tables'].keys())[0]]

        fields = semantic_result.get('fields', ['*'])
        if not fields:
            fields = ['*']

        conditions = []
        for cond in semantic_result.get('conditions', []):
            if isinstance(cond, dict):
                conditions.append(Condition(
                    field=cond.get('field', ''),
                    operator=cond.get('operator', '='),
                    value=cond.get('value', ''),
                    logical=cond.get('logical', 'AND')
                ))

        joins = []
        for join in semantic_result.get('joins', []):
            joins.append(Join(
                join_type=join.get('type', 'INNER JOIN'),
                from_table=join.get('from_table', ''),
                from_field=join.get('from_field', ''),
                to_table=join.get('to_table', ''),
                to_field=join.get('to_field', '')
            ))

        group_by = semantic_result.get('group_by', [])
        
        order_by = []
        order_by_raw = semantic_result.get('order_by')
        if order_by_raw:
            if isinstance(order_by_raw, str):
                parts = order_by_raw.split()
                if len(parts) >= 2:
                    order_by.append({'field': parts[0], 'direction': parts[1]})
                elif len(parts) == 1:
                    order_by.append({'field': parts[0], 'direction': 'ASC'})
            elif isinstance(order_by_raw, dict):
                order_by.append(order_by_raw)

        limit = semantic_result.get('limit')
        
        aggregations = semantic_result.get('aggregations', [])
        if aggregations:
            agg_list = []
            for agg in aggregations:
                if isinstance(agg, str):
                    agg_list.append(agg)
                elif isinstance(agg, dict):
                    func = agg.get('function', agg.get('func', ''))
                    if func:
                        agg_list.append(func)
            aggregations = agg_list if agg_list else aggregations

        return DSL(
            operation=operation,
            tables=tables,
            fields=fields,
            conditions=conditions,
            joins=joins,
            group_by=group_by,
            order_by=order_by,
            limit=limit,
            aggregations=aggregations
        )


class DSLSemanticValidator:
    def __init__(self, schema: Dict[str, Any] = None):
        self._schema = schema or {}
        self._errors: List[str] = []

    def validate(self, dsl: DSL) -> bool:
        self._errors = []
        
        if not dsl.tables:
            self._errors.append("DSL must specify at least one table")

        available_tables = list(self._schema.get('tables', {}).keys())
        for table in dsl.tables:
            if table not in available_tables:
                self._errors.append(f"Unknown table: {table}")

        valid_operators = ['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL']
        for cond in dsl.conditions:
            if cond.operator not in valid_operators:
                self._errors.append(f"Invalid operator: {cond.operator}")

        return len(self._errors) == 0

    def get_errors(self) -> List[str]:
        return self._errors


class DSLNormalizer:
    def __init__(self):
        pass

    def normalize(self, dsl: DSL) -> DSL:
        if not dsl.fields:
            dsl.fields = ['*']

        for cond in dsl.conditions:
            if isinstance(cond.value, str):
                cond.value = cond.value.strip("'\"")

        if dsl.limit is not None and dsl.limit < 0:
            dsl.limit = None

        return dsl


class DSLAnnotator:
    def __init__(self):
        pass

    def annotate(self, dsl: DSL, query: str, semantic_result: Dict[str, Any]) -> DSL:
        dsl.annotations = {
            'original_query': query,
            'intent': semantic_result.get('intent', 'SELECT'),
            'confidence': semantic_result.get('confidence', 1.0),
            'reasoning': self._generate_reasoning(dsl, semantic_result)
        }
        return dsl

    def _generate_reasoning(self, dsl: DSL, semantic_result: Dict[str, Any]) -> str:
        reasoning_parts = []
        
        reasoning_parts.append(f"操作类型: {dsl.operation}")
        
        if dsl.tables:
            reasoning_parts.append(f"查询表: {', '.join(dsl.tables)}")
        
        if dsl.fields:
            reasoning_parts.append(f"查询字段: {', '.join(dsl.fields)}")
        
        if dsl.conditions:
            cond_strs = [f"{c.field} {c.operator} {c.value}" for c in dsl.conditions]
            reasoning_parts.append(f"查询条件: {' AND '.join(cond_strs)}")
        
        if dsl.aggregations:
            reasoning_parts.append(f"聚合操作: {', '.join(dsl.aggregations)}")
        
        if dsl.group_by:
            reasoning_parts.append(f"分组字段: {', '.join(dsl.group_by)}")
        
        if dsl.order_by:
            order_strs = [f"{o.get('field', '')} {o.get('direction', '')}" for o in dsl.order_by]
            reasoning_parts.append(f"排序: {', '.join(order_strs)}")
        
        if dsl.joins:
            join_strs = [f"{j.from_table}.{j.from_field} = {j.to_table}.{j.to_field}" for j in dsl.joins]
            reasoning_parts.append(f"表关联: {' AND '.join(join_strs)}")
        
        return "; ".join(reasoning_parts)


class DSLGenerator:
    def __init__(self, schema: Dict[str, Any] = None):
        self._schema = schema or {}
        self._builder = DSLBuilder(schema)
        self._validator = DSLSemanticValidator(schema)
        self._normalizer = DSLNormalizer()
        self._annotator = DSLAnnotator()

    def process(self, query: str, semantic_result: Dict[str, Any]) -> DSL:
        dsl = self._builder.build(semantic_result)
        
        is_valid = self._validator.validate(dsl)
        if not is_valid:
            raise ValueError(f"DSL validation failed: {self._validator.get_errors()}")
        
        dsl = self._normalizer.normalize(dsl)
        
        dsl = self._annotator.annotate(dsl, query, semantic_result)
        
        return dsl
