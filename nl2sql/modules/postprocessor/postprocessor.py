from typing import Dict, List, Any, Optional, Tuple
import re


class ResultValidator:
    def __init__(self, schema: Dict[str, Any] = None):
        self._schema = schema or {}

    def validate(self, sql: str, dsl) -> Tuple[bool, List[str]]:
        errors = []
        
        if not sql or not sql.strip():
            errors.append("SQL is empty")
        
        if not self._validate_tables(sql):
            errors.append("SQL references unknown tables")
        
        if not self._validate_syntax_basic(sql):
            errors.append("SQL has basic syntax errors")
        
        return len(errors) == 0, errors

    def _validate_tables(self, sql: str) -> bool:
        tables_dict = self._schema.get('tables', {})
        if not tables_dict:
            return True
        
        available_tables = set(tables_dict.keys())
        
        for table in available_tables:
            if re.search(r'\b' + re.escape(table) + r'\b', sql, re.IGNORECASE):
                return True
        
        return True

    def _validate_syntax_basic(self, sql: str) -> bool:
        sql_upper = sql.upper().strip()
        
        valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        for start in valid_starts:
            if sql_upper.startswith(start):
                return True
        
        return False


class OutputFormatter:
    def __init__(self, format_type: str = 'plain'):
        self._format_type = format_type

    def format(self, result: Dict[str, Any]) -> str:
        if self._format_type == 'json':
            return self._format_json(result)
        elif self._format_type == 'markdown':
            return self._format_markdown(result)
        else:
            return self._format_plain(result)

    def _format_json(self, result: Dict[str, Any]) -> str:
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _format_markdown(self, result: Dict[str, Any]) -> str:
        lines = []
        
        lines.append("## 查询结果")
        lines.append("")
        
        if 'sql' in result:
            lines.append("### SQL")
            lines.append("```sql")
            lines.append(result['sql'])
            lines.append("```")
            lines.append("")
        
        if 'dsl' in result:
            lines.append("### DSL")
            lines.append("```json")
            lines.append(result['dsl'])
            lines.append("```")
            lines.append("")
        
        if 'explanation' in result:
            lines.append("### 解释")
            lines.append(result['explanation'])
            lines.append("")
        
        if 'error' in result:
            lines.append("### 错误")
            lines.append(f"```\n{result['error']}\n```")
            lines.append("")
        
        return '\n'.join(lines)

    def _format_plain(self, result: Dict[str, Any]) -> str:
        lines = []
        
        if 'sql' in result:
            lines.append("SQL:")
            lines.append(result['sql'])
            lines.append("")
        
        if 'explanation' in result:
            lines.append("解释:")
            lines.append(result['explanation'])
            lines.append("")
        
        if 'error' in result:
            lines.append("错误:")
            lines.append(result['error'])
            lines.append("")
        
        return '\n'.join(lines)


class ErrorHandler:
    def __init__(self):
        self._error_log: List[Dict[str, Any]] = []

    def handle(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'handled': True
        }
        
        self._error_log.append(error_info)
        
        return error_info

    def get_error_message(self, error: Exception) -> str:
        error_type = type(error).__name__
        
        user_friendly_messages = {
            'ValueError': '输入数据验证失败，请检查查询内容',
            'KeyError': '缺少必要的配置信息',
            'AttributeError': '处理过程中发生错误',
            'RuntimeError': '运行时错误，请稍后重试',
            'LLMError': '大模型调用失败，请检查网络或API配置',
            'SecurityError': '安全检查未通过'
        }
        
        return user_friendly_messages.get(error_type, str(error))

    def get_error_log(self) -> List[Dict[str, Any]]:
        return self._error_log


class LogRecorder:
    def __init__(self, logger=None):
        self._logger = logger

    def record(self, level: str, message: str, context: Dict[str, Any] = None):
        if self._logger:
            if level == 'debug':
                self._logger.debug(message, extra=context or {})
            elif level == 'info':
                self._logger.info(message, extra=context or {})
            elif level == 'warning':
                self._logger.warning(message, extra=context or {})
            elif level == 'error':
                self._logger.error(message, extra=context or {})
            elif level == 'critical':
                self._logger.critical(message, extra=context or {})

    def record_query(self, query: str, sql: str, dsl, success: bool, duration: float):
        context = {
            'original_query': query,
            'generated_sql': sql,
            'dsl': dsl.to_dict() if dsl else None,
            'success': success,
            'duration': duration
        }
        
        level = 'info' if success else 'error'
        message = f"Query processed: {'success' if success else 'failed'}"
        
        self.record(level, message, context)


class Postprocessor:
    def __init__(self, schema: Dict[str, Any] = None, config: Dict[str, Any] = None):
        self._schema = schema or {}
        self._config = config or {}
        
        self._result_validator = ResultValidator(schema)
        self._formatter = OutputFormatter(config.get('format', 'plain'))
        self._error_handler = ErrorHandler()
        self._logger = None

    def set_logger(self, logger):
        self._logger = logger
        self._log_recorder = LogRecorder(logger)

    def process(self, sql: str, dsl, query: str, duration: float = 0) -> Dict[str, Any]:
        result = {
            'sql': sql,
            'dsl': dsl.to_json() if dsl else None,
            'success': True
        }
        
        is_valid, errors = self._result_validator.validate(sql, dsl)
        if not is_valid:
            result['validation_errors'] = errors
        
        if dsl and dsl.annotations:
            result['explanation'] = dsl.annotations.get('reasoning', '')
        
        result['formatted'] = self._formatter.format(result)
        
        if hasattr(self, '_log_recorder'):
            self._log_recorder.record_query(query, sql, dsl, True, duration)
        
        return result

    def process_error(self, error: Exception, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        error_info = self._error_handler.handle(error, context or {})
        
        result = {
            'success': False,
            'error': self._error_handler.get_error_message(error),
            'error_type': error_info['error_type'],
            'formatted': self._formatter.format({
                'error': error_info['error_message'],
                'query': query
            })
        }
        
        if hasattr(self, '_log_recorder'):
            self._log_recorder.record_query(query, '', None, False, 0)
        
        return result
