import json
import os
from typing import Any, Dict, List, Generator, Optional, Union
import logging
import tempfile
import shutil
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("json_utils")

class JsonProcessingError(Exception):
    """Exceção para erros de processamento JSON."""
    pass

def stream_json_array(file_path: str, chunk_size: int = 1000) -> Generator[List[Dict], None, None]:
    """
    Processa um arquivo JSON grande que contenha um array, gerando chunks de objetos.
    Útil para arquivos que não cabem na memória.
    
    Args:
        file_path: Caminho para o arquivo JSON
        chunk_size: Número de objetos a serem lidos por vez
        
    Yields:
        Lista de objetos JSON (dicionários)
        
    Raises:
        JsonProcessingError: Se ocorrer um erro durante o processamento
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Verificar se o arquivo começa com [
            char = f.read(1)
            if char != '[':
                raise JsonProcessingError(f"Arquivo não contém um array JSON: {file_path}")
            
            # Retornar ao início
            f.seek(0)
            
            # Criar um decodificador JSON iterativo
            decoder = json.JSONDecoder()
            content = f.read()
            pos = 0
            
            # Pular o primeiro [
            content = content.strip()
            if content[0] == '[':
                pos = 1
            
            # Preparar para coletar objetos
            items = []
            
            # Processar objetos até o final do arquivo
            while pos < len(content):
                # Pular espaços em branco
                match = content[pos:].lstrip()
                if not match:
                    break
                    
                pos = pos + len(content[pos:]) - len(match)
                
                try:
                    # Decodificar o próximo objeto
                    obj, pos = decoder.raw_decode(content, pos)
                    items.append(obj)
                    
                    # Verificar se chegamos ao tamanho do chunk
                    if len(items) >= chunk_size:
                        yield items
                        items = []
                        
                    # Pular a vírgula entre objetos
                    if pos < len(content) and content[pos] == ',':
                        pos += 1
                        
                except json.JSONDecodeError as e:
                    # Se estamos no final do array, pode haver um erro de decodificação
                    if content[pos:].strip().startswith(']'):
                        break
                    else:
                        raise JsonProcessingError(f"Erro ao decodificar JSON na posição {pos}: {str(e)}")
            
            # Retornar quaisquer itens restantes
            if items:
                yield items
                
    except Exception as e:
        if isinstance(e, JsonProcessingError):
            raise
        else:
            raise JsonProcessingError(f"Erro ao processar arquivo JSON {file_path}: {str(e)}")

def save_json_with_backup(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Salva dados JSON em um arquivo, criando um backup do arquivo existente.
    
    Args:
        data: Dados a serem salvos (deve ser serializável para JSON)
        file_path: Caminho para o arquivo
        indent: Número de espaços para indentação
        
    Raises:
        JsonProcessingError: Se ocorrer um erro durante o salvamento
    """
    try:
        # Criar diretório de backup se não existir
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Criar nome de arquivo de backup com timestamp
        file_name = os.path.basename(file_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"{file_name}.{timestamp}.bak")
        
        # Fazer backup se o arquivo existir
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
        
        # Salvar arquivo usando arquivo temporário para garantir operação atômica
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            json.dump(data, temp_file, ensure_ascii=False, indent=indent)
            temp_path = temp_file.name
            
        # Substituir arquivo original pelo temporário
        shutil.move(temp_path, file_path)
        logger.info(f"Arquivo salvo: {file_path}")
        
    except Exception as e:
        raise JsonProcessingError(f"Erro ao salvar arquivo JSON {file_path}: {str(e)}")

def convert_csv_to_json(csv_file_path: str, json_file_path: str, 
                        delimiter: str = ',', has_header: bool = True) -> None:
    """
    Converte um arquivo CSV para JSON.
    
    Args:
        csv_file_path: Caminho para o arquivo CSV de entrada
        json_file_path: Caminho para o arquivo JSON de saída
        delimiter: Delimitador usado no CSV
        has_header: Se True, a primeira linha é tratada como cabeçalho
        
    Raises:
        JsonProcessingError: Se ocorrer um erro durante a conversão
    """
    try:
        import csv
        
        with open(csv_file_path, 'r', encoding='utf-8', newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            
            # Ler cabeçalho se houver
            headers = next(csv_reader) if has_header else None
            
            # Se não houver cabeçalho, gerar nomes de coluna padrão e voltar ao início
            if not headers:
                # Ler primeira linha para determinar número de colunas
                first_row = next(csv_reader)
                num_cols = len(first_row)
                headers = [f"column{i}" for i in range(num_cols)]
                # Voltar ao início
                csv_file.seek(0)
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
            
            # Converter linhas para objetos JSON
            data = []
            for row in csv_reader:
                # Pular linha de cabeçalho se necessário
                if has_header and csv_reader.line_num == 1:
                    continue
                    
                # Criar objeto com valores das colunas
                entry = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        # Tentar converter para tipo apropriado
                        try:
                            # Tentar como número
                            if value.isdigit():
                                entry[headers[i]] = int(value)
                            elif value.replace('.', '', 1).isdigit():
                                entry[headers[i]] = float(value)
                            # Tentar como booleano
                            elif value.lower() in ['true', 'yes', 'sim', '1']:
                                entry[headers[i]] = True
                            elif value.lower() in ['false', 'no', 'não', '0']:
                                entry[headers[i]] = False
                            # Caso contrário, manter como string
                            else:
                                entry[headers[i]] = value
                        except:
                            # Em caso de erro, manter como string
                            entry[headers[i]] = value
                
                data.append(entry)
            
            # Salvar como JSON
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=2)
                
            logger.info(f"Arquivo CSV convertido para JSON: {json_file_path}")
            
    except Exception as e:
        raise JsonProcessingError(f"Erro ao converter CSV para JSON: {str(e)}")

def convert_json_to_csv(json_file_path: str, csv_file_path: str, 
                        delimiter: str = ',', include_header: bool = True) -> None:
    """
    Converte um arquivo JSON para CSV.
    
    Args:
        json_file_path: Caminho para o arquivo JSON de entrada
        csv_file_path: Caminho para o arquivo CSV de saída
        delimiter: Delimitador a ser usado no CSV
        include_header: Se True, inclui linha de cabeçalho
        
    Raises:
        JsonProcessingError: Se ocorrer um erro durante a conversão
    """
    try:
        import csv
        
        # Carregar dados JSON
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # Garantir que temos uma lista de objetos
        if not isinstance(data, list):
            if isinstance(data, dict):
                # Encontrar uma lista dentro do objeto, se houver
                for key, value in data.items():
                    if isinstance(value, list):
                        data = value
                        break
                else:
                    # Se não encontrar uma lista, transformar o próprio objeto em uma lista
                    data = [data]
            else:
                raise JsonProcessingError("O arquivo JSON não contém uma lista ou objeto")
        
        if not data:
            logger.warning("Lista JSON vazia, criando arquivo CSV vazio")
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
                csv_file.write("")
            return
        
        # Determinar cabeçalhos a partir de todas as chaves em todos os objetos
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        headers = sorted(list(all_keys))
        
        # Escrever no CSV
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=delimiter)
            
            # Escrever cabeçalho se necessário
            if include_header:
                csv_writer.writerow(headers)
            
            # Escrever dados
            for item in data:
                if isinstance(item, dict):
                    row = [str(item.get(key, "")) for key in headers]
                    csv_writer.writerow(row)
                else:
                    # Se o item não for um dicionário, escrever como valor único
                    csv_writer.writerow([str(item)])
        
        logger.info(f"Arquivo JSON convertido para CSV: {csv_file_path}")
        
    except Exception as e:
        raise JsonProcessingError(f"Erro ao converter JSON para CSV: {str(e)}")

def validate_json_schema(data: Dict, schema: Dict) -> List[str]:
    """
    Valida um objeto JSON contra um esquema simples.
    
    Args:
        data: Dicionário de dados a validar
        schema: Dicionário de esquema contendo validações
        
    Returns:
        Lista de mensagens de erro. Lista vazia se não houver erros.
    """
    errors = []
    
    # Verificar se schema tem uma seção __meta__
    if "__meta__" not in schema:
        return ["Esquema não contém seção __meta__"]
    
    meta = schema["__meta__"]
    
    # Validar campos obrigatórios
    for field_name, field_spec in meta.items():
        if not isinstance(field_spec, dict):
            errors.append(f"Especificação inválida para o campo '{field_name}'")
            continue
            
        required = field_spec.get("required", False)
        
        if required and (field_name not in data or data[field_name] is None):
            errors.append(f"Campo obrigatório '{field_name}' está ausente")
            continue
            
        # Se o campo estiver presente, validar o tipo
        if field_name in data and data[field_name] is not None:
            if "type" not in field_spec:
                errors.append(f"Tipo não especificado para o campo '{field_name}'")
                continue
                
            field_type = field_spec["type"]
            field_value = data[field_name]
            
            # Validar tipo
            valid = False
            
            if field_type == "str" and isinstance(field_value, str):
                valid = True
            elif field_type == "int" and isinstance(field_value, int):
                valid = True
            elif field_type == "float" and isinstance(field_value, (int, float)):
                valid = True
            elif field_type == "bool" and isinstance(field_value, bool):
                valid = True
            elif field_type == "list" and isinstance(field_value, list):
                valid = True
            elif field_type.startswith("list[") and isinstance(field_value, list):
                # Validar tipo interno da lista
                inner_type = field_type[5:-1]
                all_valid = True
                
                for i, item in enumerate(field_value):
                    if inner_type == "str" and not isinstance(item, str):
                        errors.append(f"Item {i} em '{field_name}' deve ser string")
                        all_valid = False
                    elif inner_type == "int" and not isinstance(item, int):
                        errors.append(f"Item {i} em '{field_name}' deve ser inteiro")
                        all_valid = False
                    elif inner_type == "float" and not isinstance(item, (int, float)):
                        errors.append(f"Item {i} em '{field_name}' deve ser número")
                        all_valid = False
                    elif inner_type == "bool" and not isinstance(item, bool):
                        errors.append(f"Item {i} em '{field_name}' deve ser booleano")
                        all_valid = False
                
                valid = all_valid
            elif (field_type == "dict" or field_type == "object") and isinstance(field_value, dict):
                valid = True
            
            if not valid and not errors:  # Evitar mensagem duplicada
                errors.append(f"Valor do campo '{field_name}' não corresponde ao tipo {field_type}")
    
    # Verificar campos extras
    for field_name in data:
        if field_name not in meta:
            errors.append(f"Campo '{field_name}' não está definido no esquema")
    
    return errors

def is_json_file_large(file_path: str, threshold_mb: float = 10.0) -> bool:
    """
    Verifica se um arquivo JSON é considerado grande.
    
    Args:
        file_path: Caminho para o arquivo
        threshold_mb: Tamanho limite em MB
        
    Returns:
        True se o arquivo for maior que o limite, False caso contrário
    """
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return file_size_mb > threshold_mb
    except Exception:
        return False