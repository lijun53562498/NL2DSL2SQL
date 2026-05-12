from typing import Dict, List, Any, Optional
from ..dsl_generator.dsl_generator import DSL


class SemanticEquivalenceChecker:
    def __init__(self):
        pass

    def check(self, dsl1: DSL, dsl2: DSL) -> bool:
        if dsl1.operation != dsl2.operation:
            return False

        if set(dsl1.tables) != set(dsl2.tables):
            return False

        if set(dsl1.fields) != set(dsl2.fields):
            return False

        if self._normalize_conditions(dsl1.conditions) != self._normalize_conditions(dsl2.conditions):
            return False

        return True

    def _normalize_conditions(self, conditions: List) -> List[Dict]:
        normalized = []
        for cond in conditions:
            normalized.append({
                'field': cond.field,
                'operator': cond.operator,
                'value': str(cond.value)
            })
        return sorted(normalized, key=lambda x: x['field'])


class PerformanceOptimizer:
    def __init__(self):
        pass

    def optimize(self, dsl: DSL) -> DSL:
        dsl = self._optimize_joins(dsl)
        dsl = self._optimize_fields(dsl)
        dsl = self._optimize_conditions(dsl)
        
        return dsl

    def _optimize_joins(self, dsl: DSL) -> DSL:
        seen = set()
        unique_joins = []
        
        for join in dsl.joins:
            key = (join.from_table, join.from_field, join.to_table, join.to_field)
            if key not in seen:
                seen.add(key)
                unique_joins.append(join)
        
        dsl.joins = unique_joins
        return dsl

    def _optimize_fields(self, dsl: DSL) -> DSL:
        if '*' in dsl.fields and not dsl.aggregations:
            table_fields = []
            for table in dsl.tables:
                table_fields.append(f"{table}.*")
            
            if len(dsl.tables) == 1:
                dsl.fields = ['*']
            else:
                dsl.fields = table_fields
        
        return dsl

    def _optimize_conditions(self, dsl: DSL) -> DSL:
        unique_conditions = []
        seen = set()
        
        for cond in dsl.conditions:
            key = (cond.field, cond.operator, str(cond.value))
            if key not in seen:
                seen.add(key)
                unique_conditions.append(cond)
        
        dsl.conditions = unique_conditions
        return dsl


class SecurityValidator:
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._allowed_operations = self._config.get('allowed_operations', ['SELECT'])
        self._max_query_depth = self._config.get('max_query_depth', 10)
        
        self._dangerous_keywords = [
            'DROP', 'TRUNCATE', 'ALTER', 'CREATE',
            'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
        ]

    def validate(self, dsl: DSL) -> tuple[bool, List[str]]:
        errors = []
        
        if dsl.operation not in self._allowed_operations:
            errors.append(f"Operation {dsl.operation} is not allowed")
        
        if len(dsl.tables) > self._max_query_depth:
            errors.append(f"Query depth {len(dsl.tables)} exceeds maximum {self._max_query_depth}")
        
        for keyword in self._dangerous_keywords:
            if keyword in [c.operator.upper() for c in dsl.conditions]:
                errors.append(f"Dangerous keyword detected: {keyword}")
        
        return len(errors) == 0, errors

    def sanitize_value(self, value: str) -> str:
        dangerous_patterns = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        
        sanitized = value
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '')
        
        return sanitized


class DSLStandardizer:
    def __init__(self):
        pass

    def standardize(self, dsl: DSL) -> DSL:
        dsl.operation = dsl.operation.upper()
        
        dsl.tables = [t.strip() for t in dsl.tables]
        dsl.tables = list(set(dsl.tables))
        
        dsl.fields = [f.strip() for f in dsl.fields]
        dsl.fields = list(set(dsl.fields))
        
        if dsl.group_by:
            dsl.group_by = [g.strip() for g in dsl.group_by]
        
        for cond in dsl.conditions:
            cond.field = cond.field.strip()
            cond.operator = cond.operator.upper()
        
        for join in dsl.joins:
            join.join_type = join.join_type.upper()
        
        return dsl


class DSLOptimizer:
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._equivalence_checker = SemanticEquivalenceChecker()
        self._performance_optimizer = PerformanceOptimizer()
        self._security_validator = SecurityValidator(config)
        self._standardizer = DSLStandardizer()

    def process(self, dsl: DSL) -> DSL:
        is_valid, errors = self._security_validator.validate(dsl)
        if not is_valid:
            raise ValueError(f"Security validation failed: {errors}")
        
        dsl = self._standardizer.standardize(dsl)
        
        dsl = self._performance_optimizer.optimize(dsl)
        
        return dsl

    def get_optimization_report(self, original_dsl: DSL, optimized_dsl: DSL) -> Dict[str, Any]:
        return {
            'original': original_dsl.to_dict(),
            'optimized': optimized_dsl.to_dict(),
            'changes': {
                'fields_optimized': original_dsl.fields != optimized_dsl.fields,
                'joins_optimized': len(original_dsl.joins) != len(optimized_dsl.joins),
                'conditions_optimized': len(original_dsl.conditions) != len(optimized_dsl.conditions)
            }
        }
