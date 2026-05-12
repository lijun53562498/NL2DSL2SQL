from typing import Dict, Any, Optional
import time

from ..config.config import EngineConfig
from ..core.schema import DatabaseSchema
from ..models.query_result import QueryResult
from ..utils.logger import setup_logger
from ..utils.exceptions import NL2SQLError

from ..modules.preprocessor.preprocessor import Preprocessor
from ..modules.llm_understanding.llm_understanding import LLMUnderstanding
from ..modules.dsl_generator.dsl_generator import DSLGenerator
from ..modules.dsl_optimizer.dsl_optimizer import DSLOptimizer
from ..modules.sql_generator.sql_generator import SQLGenerator
from ..modules.postprocessor.postprocessor import Postprocessor


class NL2SQLEngine:
    def __init__(
        self,
        schema: DatabaseSchema,
        config: Optional[EngineConfig] = None,
        llm_client=None
    ):
        self._schema = schema
        self._config = config or EngineConfig.default()
        
        if llm_client is None and self._config.llm.api_key:
            llm_client = self._config.create_llm_client()
        
        self._llm_client = llm_client
        
        self._logger = setup_logger('nl2sql', self._config.logging.level)
        
        self._init_modules()

    def _init_modules(self):
        schema_dict = self._schema.to_dict()
        
        self._preprocessor = Preprocessor(schema_dict)
        
        self._llm_understanding = LLMUnderstanding(
            llm_client=self._llm_client,
            schema=schema_dict
        )
        
        self._dsl_generator = DSLGenerator(schema_dict)
        
        self._dsl_optimizer = DSLOptimizer(self._config.security.model_dump())
        
        self._sql_generator = SQLGenerator(
            dialect=self._config.database.default_dialect,
            config=self._config.model_dump(),
            llm_client=self._llm_client,
            schema=self._schema
        )
        
        self._postprocessor = Postprocessor(
            schema=schema_dict,
            config={'format': self._config.output_format}
        )
        self._postprocessor.set_logger(self._logger)

    def process(self, natural_language_query: str) -> QueryResult:
        start_time = time.time()
        
        try:
            self._logger.info(f"Processing query: {natural_language_query}")
            
            preprocessed = self._preprocessor.process(natural_language_query)
            self._logger.debug(f"Preprocessed: {preprocessed}")
            
            semantic_result = self._llm_understanding.process(
                natural_language_query,
                preprocessed
            )
            self._logger.debug(f"Semantic result: {semantic_result}")
            
            dsl = self._dsl_generator.process(natural_language_query, semantic_result)
            self._logger.debug(f"Generated DSL: {dsl.to_json()}")
            
            optimized_dsl = self._dsl_optimizer.process(dsl)
            self._logger.debug(f"Optimized DSL: {optimized_dsl.to_json()}")
            
            sql = self._sql_generator.process(optimized_dsl)
            self._logger.info(f"Generated SQL: {sql}")
            
            duration = (time.time() - start_time) * 1000
            
            result_dict = self._postprocessor.process(sql, optimized_dsl, natural_language_query, duration)
            
            return QueryResult(
                original_query=natural_language_query,
                sql=result_dict.get('sql', ''),
                dsl_json=result_dict.get('dsl'),
                explanation=result_dict.get('explanation'),
                success=True,
                duration=duration,
                metadata={
                    'preprocessed': preprocessed,
                    'semantic_result': semantic_result
                }
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._logger.error(f"Error processing query: {str(e)}")
            
            result_dict = self._postprocessor.process_error(
                e,
                natural_language_query,
                {'stage': 'unknown'}
            )
            
            return QueryResult(
                original_query=natural_language_query,
                sql='',
                success=False,
                error=result_dict.get('error', str(e)),
                error_type=result_dict.get('error_type'),
                duration=duration
            )

    def get_intermediate_dsl(self, natural_language_query: str) -> Optional[Any]:
        try:
            preprocessed = self._preprocessor.process(natural_language_query)
            semantic_result = self._llm_understanding.process(natural_language_query, preprocessed)
            dsl = self._dsl_generator.process(natural_language_query, semantic_result)
            return dsl
        except Exception as e:
            self._logger.error(f"Error generating intermediate DSL: {str(e)}")
            return None

    def validate_query(self, sql: str) -> tuple[bool, list]:
        from ..modules.sql_generator.sql_generator import SQLSecurityChecker
        checker = SQLSecurityChecker()
        return checker.check(sql)
