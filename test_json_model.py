import unittest
import json
import os
import tempfile
from json_model import JsonModel, JsonModelError

class TestJsonModel(unittest.TestCase):
    """Testes para a classe JsonModel."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Criar modelo de teste
        self.test_meta = {
            "__meta__": {
                "name": {"type": "str", "required": True},
                "email": {"type": "str", "required": False},
                "age": {"type": "int", "required": False},
                "active": {"type": "bool", "required": True},
                "tags": {"type": "list[str]", "required": False}
            }
        }
        
        # Criar arquivo temporário de modelo
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w+")
        json.dump(self.test_meta, self.temp_file)
        self.temp_file.close()
        
        # Instanciar modelo a partir do dicionário
        self.model = JsonModel(model_dict=self.test_meta)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_model_from_file(self):
        """Testa o carregamento do modelo a partir de um arquivo."""
        model = JsonModel(self.temp_file.name)
        self.assertEqual(len(model.meta), len(self.test_meta["__meta__"]))
        self.assertTrue("name" in model.meta)
        self.assertEqual(model.meta["name"]["type"], "str")
        self.assertTrue(model.meta["name"]["required"])
    
    def test_load_model_from_dict(self):
        """Testa o carregamento do modelo a partir de um dicionário."""
        model = JsonModel(model_dict=self.test_meta)
        self.assertEqual(len(model.meta), len(self.test_meta["__meta__"]))
        self.assertTrue("name" in model.meta)
        self.assertEqual(model.meta["name"]["type"], "str")
        self.assertTrue(model.meta["name"]["required"])
    
    def test_validate_entry_valid(self):
        """Testa a validação de uma entrada válida."""
        valid_entry = {
            "name": "Teste",
            "email": "teste@exemplo.com",
            "age": 30,
            "active": True,
            "tags": ["teste", "exemplo"]
        }
        
        errors = self.model.validate_entry(valid_entry)
        self.assertEqual(len(errors), 0, "A entrada válida não deveria ter erros")
    
    def test_validate_entry_missing_required(self):
        """Testa a validação de uma entrada com campo obrigatório ausente."""
        invalid_entry = {
            "name": "Teste",
            "email": "teste@exemplo.com",
            # active está ausente (obrigatório)
            "tags": ["teste", "exemplo"]
        }
        
        errors = self.model.validate_entry(invalid_entry)
        self.assertTrue(len(errors) > 0, "Deveria identificar campo obrigatório ausente")
        self.assertTrue(any("'active'" in error for error in errors))
    
    def test_validate_entry_wrong_type(self):
        """Testa a validação de uma entrada com tipo incorreto."""
        invalid_entry = {
            "name": "Teste",
            "email": "teste@exemplo.com",
            "age": "trinta", # Deveria ser int, não string
            "active": True,
            "tags": ["teste", "exemplo"]
        }
        
        errors = self.model.validate_entry(invalid_entry)
        self.assertTrue(len(errors) > 0, "Deveria identificar tipo incorreto")
        self.assertTrue(any("'age'" in error and "int" in error for error in errors))
    
    def test_validate_entry_extra_field(self):
        """Testa a validação de uma entrada com campo extra não definido no modelo."""
        invalid_entry = {
            "name": "Teste",
            "email": "teste@exemplo.com",
            "age": 30,
            "active": True,
            "tags": ["teste", "exemplo"],
            "extra_field": "valor não definido no modelo"  # Campo extra
        }
        
        errors = self.model.validate_entry(invalid_entry)
        self.assertTrue(len(errors) > 0, "Deveria identificar campo extra")
        self.assertTrue(any("'extra_field'" in error for error in errors))
    
    def test_validate_entry_list_type(self):
        """Testa a validação de uma lista tipada."""
        invalid_entry = {
            "name": "Teste",
            "email": "teste@exemplo.com",
            "age": 30,
            "active": True,
            "tags": ["teste", 123]  # Um item não é string
        }
        
        errors = self.model.validate_entry(invalid_entry)
        self.assertTrue(len(errors) > 0, "Deveria identificar tipo incorreto na lista")
    
    def test_create_empty_entry(self):
        """Testa a criação de uma entrada vazia."""
        empty_entry = self.model.create_empty_entry()
        
        self.assertTrue("name" in empty_entry)
        self.assertTrue("active" in empty_entry)
        self.assertEqual(empty_entry["name"], "")  # Campo string obrigatório
        self.assertEqual(empty_entry["active"], False)  # Campo booleano obrigatório
        
        # Campos opcionais devem ser None
        self.assertEqual(empty_entry["email"], None)
        self.assertEqual(empty_entry["age"], None)
        self.assertEqual(empty_entry["tags"], None)
    
    def test_get_field_names(self):
        """Testa a obtenção dos nomes dos campos."""
        field_names = self.model.get_field_names()
        expected = ["name", "email", "age", "active", "tags"]
        
        # Verificar se todos os campos esperados estão na lista
        for field in expected:
            self.assertIn(field, field_names)
        
        # Verificar se o tamanho é o mesmo
        self.assertEqual(len(field_names), len(expected))
    
    def test_get_field_type(self):
        """Testa a obtenção do tipo de um campo."""
        self.assertEqual(self.model.get_field_type("name"), "str")
        self.assertEqual(self.model.get_field_type("age"), "int")
        self.assertEqual(self.model.get_field_type("active"), "bool")
        self.assertEqual(self.model.get_field_type("tags"), "list[str]")
    
    def test_is_field_required(self):
        """Testa a verificação se um campo é obrigatório."""
        self.assertTrue(self.model.is_field_required("name"))
        self.assertTrue(self.model.is_field_required("active"))
        self.assertFalse(self.model.is_field_required("email"))
        self.assertFalse(self.model.is_field_required("age"))
        self.assertFalse(self.model.is_field_required("tags"))

if __name__ == "__main__":
    unittest.main()