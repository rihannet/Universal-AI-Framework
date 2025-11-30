"""Pre-built worker templates for common use cases"""
from typing import Dict, Any, List


class WorkerTemplates:
    """Pre-configured worker templates"""
    
    @staticmethod
    def browser_worker(worker_id: str, name: str) -> Dict[str, Any]:
        """Browser automation worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "browser",
            "capabilities": ["web_scraping", "browser_automation", "url_fetch"],
            "api_keys": {},
            "endpoints": {},
            "model_config": {"temperature": 0.3, "max_tokens": 1024}
        }
    
    @staticmethod
    def terminal_worker(worker_id: str, name: str) -> Dict[str, Any]:
        """Terminal/shell execution worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "terminal",
            "capabilities": ["shell_execution", "command_line", "system_commands"],
            "api_keys": {},
            "endpoints": {},
            "model_config": {"temperature": 0.2, "max_tokens": 512}
        }
    
    @staticmethod
    def api_worker(
        worker_id: str,
        name: str,
        api_key: str,
        base_endpoint: str
    ) -> Dict[str, Any]:
        """API integration worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "api",
            "capabilities": ["api_calls", "http_requests", "data_fetch"],
            "api_keys": {"api_key": api_key},
            "endpoints": {"default": base_endpoint},
            "model_config": {"temperature": 0.5, "max_tokens": 2048}
        }
    
    @staticmethod
    def news_worker(worker_id: str, name: str, news_api_key: str) -> Dict[str, Any]:
        """News fetching worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "api",
            "capabilities": ["news_fetch", "articles", "headlines"],
            "api_keys": {"api_key": news_api_key},
            "endpoints": {"default": "https://newsapi.org/v2/top-headlines"},
            "model_config": {"temperature": 0.5, "max_tokens": 2048}
        }
    
    @staticmethod
    def dbms_worker(
        worker_id: str,
        name: str,
        db_connection_string: str
    ) -> Dict[str, Any]:
        """Database management worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "dbms",
            "capabilities": ["database_query", "sql_execution", "data_management"],
            "api_keys": {"connection_string": db_connection_string},
            "endpoints": {},
            "model_config": {"temperature": 0.1, "max_tokens": 1024}
        }
    
    @staticmethod
    def file_worker(worker_id: str, name: str) -> Dict[str, Any]:
        """File system operations worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "file",
            "capabilities": ["file_read", "file_write", "file_list"],
            "api_keys": {},
            "endpoints": {},
            "model_config": {"temperature": 0.2, "max_tokens": 1024}
        }
    
    @staticmethod
    def app_execution_worker(worker_id: str, name: str) -> Dict[str, Any]:
        """Application execution worker"""
        return {
            "worker_id": worker_id,
            "name": name,
            "worker_type": "app",
            "capabilities": ["app_launch", "process_management", "app_control"],
            "api_keys": {},
            "endpoints": {},
            "model_config": {"temperature": 0.3, "max_tokens": 1024}
        }
    
    @staticmethod
    def list_templates() -> List[str]:
        """List all available templates"""
        return [
            "browser_worker",
            "terminal_worker",
            "api_worker",
            "news_worker",
            "dbms_worker",
            "file_worker",
            "app_execution_worker"
        ]
