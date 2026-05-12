from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class QueryResult:
    original_query: str
    sql: str
    dsl_json: Optional[str] = None
    explanation: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_query': self.original_query,
            'sql': self.sql,
            'dsl': self.dsl_json,
            'explanation': self.explanation,
            'success': self.success,
            'error': self.error,
            'error_type': self.error_type,
            'duration': self.duration,
            'validation_errors': self.validation_errors,
            'metadata': self.metadata
        }

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        if self.success:
            return f"QueryResult(success=True, sql='{self.sql}', duration={self.duration:.2f}ms)"
        else:
            return f"QueryResult(success=False, error='{self.error}')"
