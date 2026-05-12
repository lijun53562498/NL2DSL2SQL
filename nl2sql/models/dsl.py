from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class Condition:
    field: str
    operator: str
    value: Any
    logical: str = 'AND'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'field': self.field,
            'operator': self.operator,
            'value': self.value,
            'logical': self.logical
        }


@dataclass
class Join:
    join_type: str
    from_table: str
    from_field: str
    to_table: str
    to_field: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'join_type': self.join_type,
            'from_table': self.from_table,
            'from_field': self.from_field,
            'to_table': self.to_table,
            'to_field': self.to_field
        }


@dataclass
class DSL:
    operation: str
    tables: List[str] = field(default_factory=list)
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
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
