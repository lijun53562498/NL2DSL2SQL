from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os


class LLMConfig(BaseModel):
    provider: str = Field(default='openai', description='LLM provider: openai, anthropic, local')
    model: str = Field(default='gpt-4', description='Model name')
    temperature: float = Field(default=0.0, description='Temperature for generation')
    api_key: Optional[str] = Field(default=None, description='API key')
    base_url: Optional[str] = Field(default=None, description='Base URL for API')

    def __init__(self, **data):
        if 'api_key' in data and data['api_key']:
            if data['api_key'].startswith('${') and data['api_key'].endswith('}'):
                env_var = data['api_key'][2:-1]
                data['api_key'] = os.getenv(env_var, '')
        super().__init__(**data)


class DatabaseConfig(BaseModel):
    default_dialect: str = Field(default='postgresql', description='Default SQL dialect')
    supported_dialects: list = Field(
        default=['postgresql', 'mysql', 'sqlite'],
        description='Supported SQL dialects'
    )
    connection: dict = Field(
        default_factory=dict,
        description='Database connection settings'
    )


class SecurityConfig(BaseModel):
    enable_sql_injection_check: bool = Field(default=True, description='Enable SQL injection check')
    max_query_depth: int = Field(default=10, description='Maximum query depth')
    allowed_operations: list = Field(default=['SELECT'], description='Allowed SQL operations')


class LoggingConfig(BaseModel):
    level: str = Field(default='INFO', description='Log level')
    format: str = Field(default='%(asctime)s - %(name)s - %(levelname)s - %(message)s', description='Log format')


class EngineConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output_format: str = Field(default='plain', description='Output format: plain, json, markdown')

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'EngineConfig':
        llm_config = LLMConfig(**config.get('llm', {}))
        database_config = DatabaseConfig(**config.get('database', {}))
        security_config = SecurityConfig(**config.get('security', {}))
        logging_config = LoggingConfig(**config.get('logging', {}))
        
        return cls(
            llm=llm_config,
            database=database_config,
            security=security_config,
            logging=logging_config,
            output_format=config.get('output_format', 'plain')
        )

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'EngineConfig':
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return cls.from_dict(config)

    @classmethod
    def default(cls) -> 'EngineConfig':
        return cls()

    def create_llm_client(self):
        if not self.llm.api_key:
            return None
        
        try:
            from langchain_openai import ChatOpenAI
            
            client = ChatOpenAI(
                model=self.llm.model,
                temperature=self.llm.temperature,
                api_key=self.llm.api_key,
                base_url=self.llm.base_url
            )
            return client
        except ImportError:
            return None
        except Exception as e:
            print(f"Failed to create LLM client: {e}")
            return None
