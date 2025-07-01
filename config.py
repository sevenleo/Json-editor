"""
Configurações para o Editor de Banco de Dados JSON.
Este arquivo permite personalizar o comportamento do sistema sem modificar o código-fonte.
"""

import os
import json
from typing import Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("config")

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretórios padrão
DEFAULT_DIRS = {
    "examples": os.path.join(BASE_DIR, "examples"),
    "backups": os.path.join(BASE_DIR, "backups"),
    "exports": os.path.join(BASE_DIR, "exports")
}

# Configurações padrão
DEFAULT_CONFIG = {
    # Diretórios
    "directories": DEFAULT_DIRS,
    
    # Interface
    "ui": {
        "window_width": 1000,
        "window_height": 700,
        "dark_mode_default": False,
        "font_size": 10,
        "enable_drag_drop": True,
        "confirm_before_delete": True,
        "max_history_size": 50,
        "show_field_types_in_headers": True,
        "show_tooltips": True
    },
    
    # Arquivos
    "files": {
        "create_backups": True,
        "auto_save_interval": 300,  # Segundos (0 = desativado)
        "large_file_threshold_mb": 10.0,
        "default_encoding": "utf-8",
        "recent_files_count": 10
    },
    
    # Exportação/Importação
    "export": {
        "default_json_indent": 2,
        "csv_delimiter": ",",
        "csv_include_header": True,
        "excel_sheet_name": "JSON Data"
    },
    
    # Validação
    "validation": {
        "validate_on_load": True,
        "validate_on_save": True,
        "validate_on_edit": True,
        "strict_type_checking": True,
        "allow_extra_fields": False
    }
}

# Caminho para o arquivo de configuração do usuário
USER_CONFIG_PATH = os.path.join(BASE_DIR, "user_config.json")

class Config:
    """Classe para gerenciar configurações do sistema."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carrega configurações do arquivo de configuração do usuário ou usa os padrões."""
        self._config = DEFAULT_CONFIG.copy()
        
        try:
            if os.path.exists(USER_CONFIG_PATH):
                with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Atualizar configuração padrão com valores do usuário
                self._update_nested_dict(self._config, user_config)
                logger.info(f"Configurações do usuário carregadas de {USER_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações do usuário: {str(e)}")
            logger.info("Usando configurações padrão")
        
        # Garantir que diretórios existam
        for dir_name, dir_path in self._config["directories"].items():
            os.makedirs(dir_path, exist_ok=True)
    
    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Atualiza um dicionário aninhado recursivamente.
        
        Args:
            d: Dicionário a ser atualizado
            u: Dicionário com valores a atualizar
            
        Returns:
            Dicionário atualizado
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração usando notação de ponto para acessar chaves aninhadas.
        
        Args:
            key: Chave usando notação de ponto (ex: "ui.dark_mode_default")
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou default se não encontrado
        """
        try:
            parts = key.split('.')
            value = self._config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Define um valor de configuração usando notação de ponto.
        
        Args:
            key: Chave usando notação de ponto (ex: "ui.dark_mode_default")
            value: Valor a ser definido
        """
        parts = key.split('.')
        config = self._config
        
        # Navegar até o nível correto
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Definir o valor
        config[parts[-1]] = value
    
    def save(self) -> None:
        """Salva as configurações no arquivo de configuração do usuário."""
        try:
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configurações salvas em {USER_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {str(e)}")
    
    def reset(self) -> None:
        """Redefine as configurações para os valores padrão."""
        self._config = DEFAULT_CONFIG.copy()
        
        # Se houver um arquivo de configuração do usuário, removê-lo
        if os.path.exists(USER_CONFIG_PATH):
            try:
                os.remove(USER_CONFIG_PATH)
                logger.info(f"Arquivo de configuração do usuário removido: {USER_CONFIG_PATH}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de configuração do usuário: {str(e)}")
    
    def get_all(self) -> Dict:
        """Retorna todas as configurações como um dicionário."""
        return self._config.copy()

# Instância global para acesso às configurações
config = Config()

# Função de conveniência para acessar configurações
def get_config(key: str, default: Any = None) -> Any:
    """
    Função auxiliar para obter um valor de configuração.
    
    Args:
        key: Chave usando notação de ponto (ex: "ui.dark_mode_default")
        default: Valor padrão se a chave não existir
        
    Returns:
        Valor da configuração ou default se não encontrado
    """
    return config.get(key, default)