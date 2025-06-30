import json
from typing import Any, Dict, List, Optional, Union, Type
import os

class JsonModelError(Exception):
    """Exceção personalizada para erros de modelagem JSON."""
    pass

class JsonModel:
    """
    Classe responsável por carregar, validar e gerenciar um modelo JSON baseado
    em um esquema __meta__.
    """
    
    # Tipos suportados e suas classes Python correspondentes
    SUPPORTED_TYPES = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "object": dict,
    }
    
    def __init__(self, model_path: str = None, model_dict: Dict = None):
        """
        Inicializa o modelo JSON.
        
        Args:
            model_path: Caminho para o arquivo de modelo.
            model_dict: Dicionário contendo o modelo (alternativa ao arquivo).
        """
        self.model_path = model_path
        self.meta = {}
        
        if model_path and os.path.exists(model_path):
            self.load_model_from_file(model_path)
        elif model_dict:
            self.load_model_from_dict(model_dict)
    
    def load_model_from_file(self, file_path: str) -> None:
        """
        Carrega o modelo a partir de um arquivo JSON.
        
        Args:
            file_path: Caminho para o arquivo de modelo.
        
        Raises:
            JsonModelError: Se o arquivo não for encontrado ou não contiver __meta__.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
                
            if "__meta__" not in model_data:
                raise JsonModelError("O arquivo de modelo não contém a seção __meta__")
                
            self.meta = model_data["__meta__"]
            self.model_path = file_path
            self._validate_meta()
            
        except json.JSONDecodeError:
            raise JsonModelError(f"Erro ao decodificar o arquivo JSON: {file_path}")
        except FileNotFoundError:
            raise JsonModelError(f"Arquivo de modelo não encontrado: {file_path}")
    
    def load_model_from_dict(self, model_dict: Dict) -> None:
        """
        Carrega o modelo a partir de um dicionário.
        
        Args:
            model_dict: Dicionário contendo o modelo.
            
        Raises:
            JsonModelError: Se o dicionário não contiver __meta__.
        """
        if "__meta__" not in model_dict:
            raise JsonModelError("O dicionário de modelo não contém a seção __meta__")
            
        self.meta = model_dict["__meta__"]
        self._validate_meta()
    
    def _validate_meta(self) -> None:
        """
        Valida a estrutura do modelo __meta__.
        
        Raises:
            JsonModelError: Se o modelo contiver tipos não suportados ou estiver mal formado.
        """
        if not self.meta or not isinstance(self.meta, dict):
            raise JsonModelError("Meta inválido: deve ser um dicionário não vazio")
            
        for field_name, field_spec in self.meta.items():
            if not isinstance(field_spec, dict):
                raise JsonModelError(f"Especificação inválida para o campo '{field_name}'")
                
            # Verificar presença de atributos obrigatórios
            if "type" not in field_spec:
                raise JsonModelError(f"Tipo não especificado para o campo '{field_name}'")
                
            field_type = field_spec["type"]
            
            # Validar tipo básico
            base_type = field_type.split('[')[0] if '[' in field_type else field_type
            if base_type not in self.SUPPORTED_TYPES:
                raise JsonModelError(f"Tipo não suportado '{field_type}' para o campo '{field_name}'")
                
            # Verificar required (opcional, padrão False)
            if "required" in field_spec and not isinstance(field_spec["required"], bool):
                raise JsonModelError(f"Valor 'required' inválido para o campo '{field_name}'")
    
    def validate_entry(self, entry: Dict) -> List[str]:
        """
        Valida uma entrada de dados contra o modelo.
        
        Args:
            entry: Dicionário contendo os dados a serem validados.
            
        Returns:
            Lista de mensagens de erro. Lista vazia se não houver erros.
        """
        errors = []
        
        # Validar campos obrigatórios
        for field_name, field_spec in self.meta.items():
            required = field_spec.get("required", False)
            
            if required and (field_name not in entry or entry[field_name] is None):
                errors.append(f"Campo obrigatório '{field_name}' está ausente")
                continue
                
            # Se o campo estiver presente, validar o tipo
            if field_name in entry and entry[field_name] is not None:
                field_type = field_spec["type"]
                field_value = entry[field_name]
                
                # Validar tipo simples
                if field_type in self.SUPPORTED_TYPES:
                    expected_type = self.SUPPORTED_TYPES[field_type]
                    if not isinstance(field_value, expected_type):
                        errors.append(f"Campo '{field_name}' deve ser do tipo {field_type}, "
                                     f"recebido {type(field_value).__name__}")
                
                # Validar listas tipadas (por exemplo, "list[str]")
                elif field_type.startswith("list[") and field_type.endswith("]"):
                    if not isinstance(field_value, list):
                        errors.append(f"Campo '{field_name}' deve ser uma lista")
                    else:
                        inner_type = field_type[5:-1]  # Extrair tipo interno da lista
                        if inner_type in self.SUPPORTED_TYPES:
                            expected_inner_type = self.SUPPORTED_TYPES[inner_type]
                            for i, item in enumerate(field_value):
                                if not isinstance(item, expected_inner_type):
                                    errors.append(
                                        f"Item {i} em '{field_name}' deve ser do tipo {inner_type}, "
                                        f"recebido {type(item).__name__}")
        
        # Verificar campos extras não definidos no modelo
        for field_name in entry:
            if field_name not in self.meta:
                errors.append(f"Campo '{field_name}' não está definido no modelo")
        
        return errors
    
    def validate_data(self, data: List[Dict]) -> Dict[int, List[str]]:
        """
        Valida uma lista de entradas contra o modelo.
        
        Args:
            data: Lista de dicionários para validar.
            
        Returns:
            Dicionário com índices e listas de erros para cada entrada inválida.
        """
        all_errors = {}
        
        for i, entry in enumerate(data):
            errors = self.validate_entry(entry)
            if errors:
                all_errors[i] = errors
                
        return all_errors
    
    def create_empty_entry(self) -> Dict:
        """
        Cria uma entrada vazia baseada no modelo com valores padrão para campos obrigatórios.
        
        Returns:
            Dicionário representando uma entrada vazia conforme o modelo.
        """
        entry = {}
        
        for field_name, field_spec in self.meta.items():
            required = field_spec.get("required", False)
            field_type = field_spec["type"]
            
            # Inserir valores padrão para campos obrigatórios
            if required:
                if field_type == "str":
                    entry[field_name] = ""
                elif field_type == "int":
                    entry[field_name] = 0
                elif field_type == "float":
                    entry[field_name] = 0.0
                elif field_type == "bool":
                    entry[field_name] = False
                elif field_type == "list" or field_type.startswith("list["):
                    entry[field_name] = []
                elif field_type == "dict" or field_type == "object":
                    entry[field_name] = {}
            else:
                # Campos opcionais ficam como None
                entry[field_name] = None
                
        return entry
    
    def get_field_names(self) -> List[str]:
        """
        Retorna uma lista com os nomes dos campos do modelo.
        
        Returns:
            Lista de nomes de campos.
        """
        return list(self.meta.keys())
    
    def get_field_type(self, field_name: str) -> str:
        """
        Retorna o tipo de um campo específico.
        
        Args:
            field_name: Nome do campo.
            
        Returns:
            Tipo do campo como string.
        """
        if field_name in self.meta:
            return self.meta[field_name]["type"]
        return None
    
    def is_field_required(self, field_name: str) -> bool:
        """
        Verifica se um campo é obrigatório.
        
        Args:
            field_name: Nome do campo.
            
        Returns:
            True se o campo for obrigatório, False caso contrário.
        """
        if field_name in self.meta:
            return self.meta[field_name].get("required", False)
        return False