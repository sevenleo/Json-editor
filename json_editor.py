import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid
import re
from pathlib import Path
import tempfile
from json_model import JsonModel, JsonModelError
from json_utils import save_json_with_backup, is_json_file_large
from config import get_config

class HistoryManager:
    """Gerenciador de histórico para operações de desfazer/refazer."""
    
    def __init__(self, max_history: int = 50):
        self.history = []
        self.future = []
        self.max_history = max_history
    
    def add(self, state: Any) -> None:
        """Adiciona um novo estado ao histórico."""
        self.history.append(state)
        self.future.clear()  # Limpa o futuro ao adicionar novo estado
        
        # Limitar tamanho do histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self) -> Optional[Any]:
        """Desfaz a última operação."""
        if not self.history:
            return None
            
        current = self.history.pop()
        self.future.append(current)
        
        if self.history:
            return self.history[-1]
        return None
    
    def redo(self) -> Optional[Any]:
        """Refaz a última operação desfeita."""
        if not self.future:
            return None
            
        next_state = self.future.pop()
        self.history.append(next_state)
        return next_state
    
    def can_undo(self) -> bool:
        """Verifica se é possível desfazer."""
        return len(self.history) > 1
    
    def can_redo(self) -> bool:
        """Verifica se é possível refazer."""
        return len(self.future) > 0

class CustomTheme:
    """Gerenciador de temas claro/escuro."""
    
    # Tema Claro
    LIGHT = {
        "bg": "#F0F0F0",
        "fg": "#000000",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#000000",
        "tree_bg": "#FFFFFF",
        "tree_fg": "#000000",
        "selected_bg": "#CCE4F7",
        "selected_fg": "#000000",
        "invalid_bg": "#FFD6D6",
        "tooltip_bg": "#FFFFCC",
        "tooltip_fg": "#000000",
        "highlight_bg": "#E5F3FF",
        "header_bg": "#E0E0E0",
        "success_color": "#4CAF50",
        "error_color": "#F44336",
        "warning_color": "#FF9800"
    }
    
    # Tema Escuro
    DARK = {
        "bg": "#2D2D2D",
        "fg": "#CCCCCC",
        "button_bg": "#444444",
        "button_fg": "#FFFFFF",
        "entry_bg": "#3D3D3D",
        "entry_fg": "#FFFFFF",
        "tree_bg": "#333333",
        "tree_fg": "#FFFFFF",
        "selected_bg": "#2C5D8D",
        "selected_fg": "#FFFFFF",
        "invalid_bg": "#5E3636",
        "tooltip_bg": "#4D4D00",
        "tooltip_fg": "#FFFFFF",
        "highlight_bg": "#1E3850",
        "header_bg": "#444444",
        "success_color": "#66BB6A",
        "error_color": "#EF5350",
        "warning_color": "#FFA726"
    }
    
    @classmethod
    def apply_theme(cls, root: tk.Tk, is_dark: bool = False) -> None:
        """Aplica o tema selecionado à interface."""
        theme = cls.DARK if is_dark else cls.LIGHT
        
        style = ttk.Style()
        
        # Configurar estilo para widgets ttk
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
        style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"])
        
        # Estilo para Treeview
        style.configure("Treeview",
                        background=theme["tree_bg"],
                        foreground=theme["tree_fg"],
                        fieldbackground=theme["tree_bg"])
        
        style.map("Treeview",
                 background=[("selected", theme["selected_bg"])],
                 foreground=[("selected", theme["selected_fg"])])
        
        # Estilo para cabeçalhos do Treeview
        style.configure("Treeview.Heading",
                       background=theme["header_bg"],
                       foreground=theme["fg"])
        
        # Configurar cores do root
        root.configure(bg=theme["bg"])
        
        # Ajustar tamanho da fonte, se configurado
        font_size = get_config("ui.font_size", 10)
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=font_size)
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=font_size)
        
        # Retornar o tema atual para uso em widgets não-ttk
        return theme

class DragDropHandler:
    """Manipulador de arrastar e soltar arquivos."""
    
    @staticmethod
    def register_drop_target(widget, callback):
        """
        Registra um widget como alvo para arrastar e soltar arquivos.
        
        Args:
            widget: Widget a ser registrado.
            callback: Função a ser chamada quando um arquivo for solto.
        """
        try:
            # Para Windows
            import win32gui
            import win32con
            import win32api
            
            def handle_wm_dropfiles(hwnd, msg, wparam, lparam):
                if msg == win32con.WM_DROPFILES:
                    count = win32api.DragQueryFile(wparam, -1, None, 0)
                    file_paths = []
                    for i in range(count):
                        file_path = win32api.DragQueryFile(wparam, i, None, 0)
                        file_paths.append(file_path)
                    win32api.DragFinish(wparam)
                    callback(file_paths)
                    return True
                return False
            
            old_wndproc = win32gui.GetWindowLong(widget.winfo_id(), win32con.GWL_WNDPROC)
            
            def new_wndproc(hwnd, msg, wparam, lparam):
                if handle_wm_dropfiles(hwnd, msg, wparam, lparam):
                    return 0
                return win32gui.CallWindowProc(old_wndproc, hwnd, msg, wparam, lparam)
            
            new_wndproc_ptr = win32gui.SetWindowLong(
                widget.winfo_id(),
                win32con.GWL_WNDPROC,
                new_wndproc
            )
            
            # Habilitar arrastar e soltar
            win32gui.DragAcceptFiles(widget.winfo_id(), True)
            
            # Armazenar referências para evitar coleta de lixo
            widget._wndproc_ptr = new_wndproc_ptr
            widget._old_wndproc = old_wndproc
            
            return True
            
        except ImportError:
            # Se win32gui não estiver disponível, retornar falso
            return False

class EditDialog(tk.Toplevel):
    """Diálogo para edição de um campo específico."""
    
    def __init__(self, parent, field_name: str, field_type: str, current_value: Any,
                 is_required: bool = False, theme: Dict = None):
        super().__init__(parent)
        self.parent = parent
        self.field_name = field_name
        self.field_type = field_type
        self.current_value = current_value
        self.is_required = is_required
        self.theme = theme or CustomTheme.LIGHT
        self.result = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        self.title(f"Editar {self.field_name}")
        self.configure(bg=self.theme["bg"])
        self.resizable(False, False)
        
        # Centralizar no pai
        window_width = 400
        window_height = 250
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Criar widgets
        # Usar grid em vez de pack para melhor controle do layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        
        # Frame para as informações do campo
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Label(info_frame, text=f"Campo: {self.field_name}").pack(pady=(0, 5), anchor="w")
        ttk.Label(info_frame, text=f"Tipo: {self.field_type}").pack(pady=(0, 5), anchor="w")
        
        if self.is_required:
            required_label = ttk.Label(info_frame, text="Campo obrigatório")
            required_label.pack(pady=(0, 5), anchor="w")
        
        # Frame para o widget de edição
        edit_frame = ttk.Frame(main_frame)
        edit_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Criar widget de edição apropriado para o tipo
        self.value_widget = self.create_type_widget(edit_frame)
        
        # Botões sempre visíveis na parte inferior
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Salvar", command=self.save).pack(side="right")
        
        # Tornar modal
        self.transient(self.parent)
        self.grab_set()
        self.focus_set()
    
    def create_type_widget(self, parent):
        """Cria o widget apropriado para o tipo do campo."""
        widget = None
        
        if self.field_type == "str":
            widget = ttk.Entry(parent)
            widget.insert(0, str(self.current_value) if self.current_value is not None else "")
            
        elif self.field_type == "int":
            vcmd = (self.register(self.validate_int), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            widget.insert(0, str(self.current_value) if self.current_value is not None else "0")
            
        elif self.field_type == "float":
            vcmd = (self.register(self.validate_float), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            widget.insert(0, str(self.current_value) if self.current_value is not None else "0.0")
            
        elif self.field_type == "bool":
            var = tk.BooleanVar(value=bool(self.current_value) if self.current_value is not None else False)
            widget = ttk.Checkbutton(parent, variable=var)
            widget.var = var  # Armazenar referência à variável
            
        elif self.field_type == "list" or self.field_type.startswith("list["):
            widget = ScrolledText(parent, wrap="word", height=10)
            
            # Frame para edição da lista com altura máxima definida
            list_frame = ttk.Frame(parent)
            list_frame.pack(fill="both", expand=True, pady=5)
            
            # Lista para armazenar widgets de entrada
            widget.entries = []
            widget.parent_frame = list_frame
            
            # Botões para adicionar/remover itens
            btn_frame = ttk.Frame(list_frame)
            btn_frame.pack(fill="x", side="bottom", pady=5)
            
            ttk.Button(btn_frame, text="Adicionar Item",
                      command=lambda: self.add_list_item(widget)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Remover Último",
                      command=lambda: self.remove_list_item(widget)).pack(side="left")
            
            # Adicionar itens da lista atual
            if self.current_value and isinstance(self.current_value, list):
                for item in self.current_value:
                    self.add_list_item(widget, item)
            
            # Se a lista estiver vazia, adicionar um item em branco
            if not widget.entries:
                self.add_list_item(widget)
                
        elif self.field_type == "dict" or self.field_type == "object":
            widget = ScrolledText(parent, wrap="word", height=10)
            
            # Frame para edição do dicionário com altura máxima definida
            dict_frame = ttk.Frame(parent)
            dict_frame.pack(fill="both", expand=True, pady=5)
            
            # Lista para armazenar pares de widgets de entrada (chave, valor)
            widget.entries = []
            widget.parent_frame = dict_frame
            widget.field_specs = {}  # Para armazenar especificações de subcampos
            
            # Verificar se há campos definidos no modelo
            has_defined_fields = False
            defined_fields = {}
            
            if self.field_type == "dict" or self.field_type == "object":
                if hasattr(self.parent, 'json_model') and self.parent.json_model:
                    defined_fields = self.parent.json_model.get_dict_fields(self.field_name)
                    has_defined_fields = bool(defined_fields)
                    widget.field_specs = defined_fields
            
            # Se houver campos definidos, usar layout estruturado
            if has_defined_fields:
                # Criar rótulos de cabeçalho
                header_frame = ttk.Frame(dict_frame)
                header_frame.pack(fill="x", pady=(0, 5))
                
                ttk.Label(header_frame, text="Campo", width=15).pack(side="left", padx=(0, 5))
                ttk.Label(header_frame, text="Tipo").pack(side="left", padx=5)
                ttk.Label(header_frame, text="Valor").pack(side="left", padx=5, fill="x", expand=True)
                
                # Adicionar campos definidos no modelo
                for subfield_name, subfield_spec in defined_fields.items():
                    field_frame = ttk.Frame(dict_frame)
                    field_frame.pack(fill="x", pady=2)
                    
                    # Informações do campo
                    is_required = subfield_spec.get("required", False)
                    subfield_type = subfield_spec["type"]
                    current_subvalue = self.current_value.get(subfield_name) if self.current_value else None
                    
                    # Rótulo do campo (com indicador de obrigatoriedade)
                    ttk.Label(
                        field_frame,
                        text=f"{subfield_name}{' *' if is_required else ''}",
                        width=15
                    ).pack(side="left", padx=(0, 5))
                    
                    # Rótulo do tipo
                    ttk.Label(
                        field_frame,
                        text=subfield_type,
                        width=10
                    ).pack(side="left", padx=5)
                    
                    # Widget de entrada apropriado para o tipo
                    value_entry = self.create_type_specific_widget(
                        field_frame, subfield_type, current_subvalue
                    )
                    value_entry.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Armazenar referência com nome do campo
                    widget.entries.append((subfield_name, value_entry, is_required, subfield_type))
            else:
                # Usar interface genérica de pares chave-valor
                # Botões para adicionar/remover pares
                btn_frame = ttk.Frame(dict_frame)
                btn_frame.pack(fill="x", side="bottom", pady=5)
                
                ttk.Button(btn_frame, text="Adicionar Par",
                          command=lambda: self.add_dict_pair(widget)).pack(side="left", padx=5)
                ttk.Button(btn_frame, text="Remover Último",
                          command=lambda: self.remove_dict_pair(widget)).pack(side="left")
                
                # Adicionar pares do dicionário atual
                if self.current_value and isinstance(self.current_value, dict):
                    for key, value in self.current_value.items():
                        self.add_dict_pair(widget, key, value)
                
                # Se o dicionário estiver vazio, adicionar um par em branco
                if not widget.entries:
                    self.add_dict_pair(widget)
        
        if widget:
            widget.pack(fill="both", expand=True, pady=5)
        
        return widget
        
    def create_type_specific_widget(self, parent, field_type, current_value=None):
        """Cria um widget específico para o tipo de campo informado dentro de um dicionário."""
        widget = None
        
        if field_type == "str":
            widget = ttk.Entry(parent)
            if current_value is not None:
                widget.insert(0, str(current_value))
                
        elif field_type == "int":
            vcmd = (self.register(self.validate_int), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            if current_value is not None:
                widget.insert(0, str(current_value))
            else:
                widget.insert(0, "0")
                
        elif field_type == "float":
            vcmd = (self.register(self.validate_float), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            if current_value is not None:
                widget.insert(0, str(current_value))
            else:
                widget.insert(0, "0.0")
                
        elif field_type == "bool":
            var = tk.BooleanVar(value=bool(current_value) if current_value is not None else False)
            widget = ttk.Checkbutton(parent, variable=var)
            widget.var = var  # Armazenar referência à variável
            
        elif field_type == "list" or field_type.startswith("list["):
            # Para listas dentro de dicionários, usamos um botão que abre outro diálogo
            button_frame = ttk.Frame(parent)
            
            # Exibir valor resumido
            list_preview = "[]"
            if current_value and isinstance(current_value, list):
                list_preview = f"[{len(current_value)} itens]"
                
            preview_label = ttk.Label(button_frame, text=list_preview)
            preview_label.pack(side="left", fill="x", expand=True)
            
            edit_button = ttk.Button(
                button_frame,
                text="Editar Lista",
                command=lambda: self.open_list_dialog(field_type, current_value, preview_label)
            )
            edit_button.pack(side="right")
            
            widget = button_frame
            widget.list_value = current_value if current_value else []
            
        elif field_type == "dict" or field_type == "object":
            # Para dicionários dentro de dicionários, usamos um botão que abre outro diálogo
            button_frame = ttk.Frame(parent)
            
            # Exibir valor resumido
            dict_preview = "{}"
            if current_value and isinstance(current_value, dict):
                dict_preview = f"{{{len(current_value)} pares}}"
                
            preview_label = ttk.Label(button_frame, text=dict_preview)
            preview_label.pack(side="left", fill="x", expand=True)
            
            edit_button = ttk.Button(
                button_frame,
                text="Editar Dict",
                command=lambda: self.open_dict_dialog(field_type, current_value, preview_label)
            )
            edit_button.pack(side="right")
            
            widget = button_frame
            widget.dict_value = current_value if current_value else {}
            
        else:
            # Para tipos desconhecidos, usar uma entrada de texto simples
            widget = ttk.Entry(parent)
            if current_value is not None:
                widget.insert(0, str(current_value))
                
        return widget
    
    def validate_int(self, value):
        """Valida entrada como número inteiro."""
        if value == "" or value == "-":
            return True
            
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def validate_float(self, value):
        """Valida entrada como número de ponto flutuante."""
        if value == "" or value == "-" or value == "." or value == "-.":
            return True
            
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def save(self):
        """Salva o valor editado."""
        try:
            if self.field_type == "str":
                self.result = self.value_widget.get()
                
            elif self.field_type == "int":
                value = self.value_widget.get()
                # Se o valor estiver vazio e não for um campo obrigatório, permitir null
                if not value:
                    self.result = None if not self.is_required else 0
                else:
                    self.result = int(value)
                
            elif self.field_type == "float":
                value = self.value_widget.get()
                # Se o valor estiver vazio e não for um campo obrigatório, permitir null
                if not value:
                    self.result = None if not self.is_required else 0.0
                else:
                    self.result = float(value)
                
            elif self.field_type == "bool":
                self.result = self.value_widget.var.get()
                
            elif self.field_type == "list" or self.field_type.startswith("list["):
                # Coletar valores dos campos de entrada
                list_values = []
                inner_type = self.field_type[5:-1] if self.field_type.startswith("list[") else None
                
                for entry_widget in self.value_widget.entries:
                    value = entry_widget.get()
                    if value.strip():  # Ignorar entradas vazias
                        # Converter para o tipo correto
                        if inner_type == "int":
                            try:
                                value = int(value)
                            except ValueError:
                                raise ValueError(f"O valor '{value}' não é um número inteiro válido")
                        elif inner_type == "float":
                            try:
                                value = float(value)
                            except ValueError:
                                raise ValueError(f"O valor '{value}' não é um número válido")
                        elif inner_type == "bool":
                            value = value.lower()
                            if value in ("true", "verdadeiro", "1", "sim", "s", "t"):
                                value = True
                            elif value in ("false", "falso", "0", "não", "nao", "n", "f"):
                                value = False
                            else:
                                raise ValueError(f"O valor '{value}' não é um booleano válido")
                        # Para string, mantemos como está
                        list_values.append(value)
                
                self.result = list_values
                
            elif self.field_type == "dict" or self.field_type == "object":
                # Verificar se este é um dicionário com campos definidos
                if hasattr(self.value_widget, 'field_specs') and self.value_widget.field_specs:
                    # Coletar valores dos campos definidos
                    dict_values = {}
                    
                    for field_name, widget, is_required, field_type in self.value_widget.entries:
                        # Obter valor do widget
                        if field_type == "bool":
                            if hasattr(widget, 'var'):
                                value = widget.var.get()
                            else:
                                value = False
                        elif field_type == "list" or field_type.startswith("list["):
                            value = getattr(widget, 'list_value', [])
                        elif field_type == "dict" or field_type == "object":
                            value = getattr(widget, 'dict_value', {})
                        else:
                            value = widget.get().strip()
                            
                            # Converter para o tipo correto
                            if field_type == "int" and value:
                                try:
                                    value = int(value)
                                except ValueError:
                                    raise ValueError(f"O valor para '{field_name}' não é um número inteiro válido")
                            elif field_type == "float" and value:
                                try:
                                    value = float(value)
                                except ValueError:
                                    raise ValueError(f"O valor para '{field_name}' não é um número válido")
                            elif not value and is_required:
                                raise ValueError(f"O campo '{field_name}' é obrigatório")
                        
                        dict_values[field_name] = value
                                
                    self.result = dict_values
                else:
                    # Usar a lógica original para dicionários genéricos
                    dict_values = {}
                    
                    for key_widget, value_widget in self.value_widget.entries:
                        key = key_widget.get().strip()
                        value = value_widget.get().strip()
                        
                        if key:  # Ignorar chaves vazias
                            # Tentar detectar o tipo do valor automaticamente
                            if not value:
                                # Valor vazio, manter como string
                                dict_values[key] = value
                            elif value.lower() in ("true", "verdadeiro", "1", "sim", "s", "t"):
                                dict_values[key] = True
                            elif value.lower() in ("false", "falso", "0", "não", "nao", "n", "f"):
                                dict_values[key] = False
                            else:
                                # Tentar converter para número
                                try:
                                    if "." in value or "," in value:
                                        # Substituir vírgula por ponto para float
                                        value = value.replace(",", ".")
                                        dict_values[key] = float(value)
                                    else:
                                        dict_values[key] = int(value)
                                except ValueError:
                                    # Se não for número, manter como string
                                    dict_values[key] = value
                    
                    self.result = dict_values
                
            self.destroy()
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro de formato", 
                                f"Formato JSON inválido: {str(e)}")
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e))
    
    def cancel(self):
        """Cancela a edição."""
        self.result = None
        self.destroy()
        
    def add_list_item(self, widget, value=None):
        """Adiciona um novo item à lista."""
        # Frame para o item
        item_frame = ttk.Frame(widget.parent_frame)
        item_frame.pack(fill="x", pady=2)
        
        # Entrada para o valor do item
        entry = ttk.Entry(item_frame)
        entry.pack(side="left", fill="x", expand=True)
        
        # Preencher com o valor, se fornecido
        if value is not None:
            entry.insert(0, str(value))
            
        # Adicionar à lista de entradas
        widget.entries.append(entry)
        
        return entry
        
    def remove_list_item(self, widget):
        """Remove o último item da lista."""
        if widget.entries:
            # Remover o último widget de entrada
            entry = widget.entries.pop()
            entry.master.destroy()  # Destruir o frame pai
            
    def add_dict_pair(self, widget, key=None, value=None):
        """Adiciona um novo par chave-valor ao dicionário."""
        # Frame para o par
        pair_frame = ttk.Frame(widget.parent_frame)
        pair_frame.pack(fill="x", pady=2)
        
        # Entrada para a chave
        key_entry = ttk.Entry(pair_frame, width=15)
        key_entry.pack(side="left", padx=(0, 5))
        ttk.Label(pair_frame, text=":").pack(side="left", padx=2)
        
        # Entrada para o valor
        value_entry = ttk.Entry(pair_frame)
        value_entry.pack(side="left", fill="x", expand=True)
        
        # Preencher com os valores, se fornecidos
        if key is not None:
            key_entry.insert(0, str(key))
        if value is not None:
            value_entry.insert(0, str(value))
            
        # Adicionar à lista de entradas
        widget.entries.append((key_entry, value_entry))
        
        return key_entry, value_entry
        
    def remove_dict_pair(self, widget):
        """Remove o último par do dicionário."""
        if widget.entries:
            # Remover o último par de widgets
            pair = widget.entries.pop()
            pair[0].master.destroy()  # Destruir o frame pai
            
    def open_list_dialog(self, field_type, current_value, preview_label):
        """Abre um diálogo para editar uma lista dentro de um dicionário."""
        # Criar um diálogo para editar a lista
        dialog = EditDialog(
            self,
            "Lista",
            field_type,
            current_value,
            False,
            self.theme
        )
        
        # Esperar pelo fechamento do diálogo
        self.wait_window(dialog)
        
        # Processar resultado
        if dialog.result is not None:
            # Atualizar o valor da lista no widget
            self.value_widget.list_value = dialog.result
            
            # Atualizar a visualização
            preview_text = f"[{len(dialog.result)} itens]"
            preview_label.configure(text=preview_text)
    
    def open_dict_dialog(self, field_type, current_value, preview_label):
        """Abre um diálogo para editar um dicionário dentro de um dicionário."""
        # Criar um diálogo para editar o dicionário
        dialog = EditDialog(
            self,
            "Dicionário",
            field_type,
            current_value,
            False,
            self.theme
        )
        
        # Esperar pelo fechamento do diálogo
        self.wait_window(dialog)
        
        # Processar resultado
        if dialog.result is not None:
            # Atualizar o valor do dicionário no widget
            self.value_widget.dict_value = dialog.result
            
            # Atualizar a visualização
            preview_text = f"{{{len(dialog.result)} pares}}"
            preview_label.configure(text=preview_text)

class JsonEditorApp:
    """Aplicação principal para edição de arquivos JSON."""
    
    # Importação da classe MultiFieldEditDialog
    from multi_field_edit import MultiFieldEditDialog
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Editor de JSON com Esquema")
        self.root.geometry("1000x700")
        
        # Inicializar variáveis
        self.json_model = None
        self.data_file_path = None
        self.data = []
        self.search_results = []
        self.current_search_index = -1
        
        # Histórico para desfazer/refazer
        max_history = get_config("ui.max_history_size", 50)
        self.history = HistoryManager(max_history)
        
        # Tema
        self.is_dark_mode = get_config("ui.dark_mode_default", False)
        self.theme = CustomTheme.apply_theme(self.root, self.is_dark_mode)
        
        # Configurar interface
        self.setup_ui()
        
        # Configurar manipuladores de arrastar e soltar
        if get_config("ui.enable_drag_drop", True):
            self._setup_drag_drop()
        
        # Configurar atalhos de teclado
        self._setup_shortcuts()
        
        # Configurar autosave se habilitado
        self._setup_autosave()
    
    def _setup_drag_drop(self):
        """Configura o suporte a arrastar e soltar."""
        # Tentar registrar o frame principal como alvo de arrastar e soltar
        DragDropHandler.register_drop_target(self.root, self.handle_dropped_files)
        
        # Exibir dica sobre arrastar e soltar
        drop_label = ttk.Label(
            self.main_frame, 
            text="Arraste arquivos JSON para aqui",
            foreground=self.theme["fg"]
        )
        drop_label.pack(pady=5)
    
    def _setup_shortcuts(self):
        """Configura atalhos de teclado."""
        self.root.bind("<Control-o>", lambda e: self.load_model_file())
        self.root.bind("<Control-d>", lambda e: self.load_data_file())
        self.root.bind("<Control-s>", lambda e: self.save_data())
        self.root.bind("<Control-n>", lambda e: self.add_entry())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.root.bind("<F3>", lambda e: self.find_next())
        self.root.bind("<Shift-F3>", lambda e: self.find_previous())
    
    def setup_ui(self):
        """Configura a interface principal."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para botões de arquivo
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        
        # Botões para carregar arquivos
        ttk.Button(
            file_frame, 
            text="Carregar Modelo", 
            command=self.load_model_file
        ).pack(side="left", padx=5)
        
        ttk.Button(
            file_frame, 
            text="Carregar Dados", 
            command=self.load_data_file
        ).pack(side="left", padx=5)
        
        ttk.Button(
            file_frame, 
            text="Salvar Dados", 
            command=self.save_data
        ).pack(side="left", padx=5)
        
        # Botão de alternar tema
        self.theme_button = ttk.Button(
            file_frame, 
            text="Tema Escuro", 
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right", padx=5)
        
        # Frame para pesquisa
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side="left", padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search())
        
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self.search
        ).pack(side="left", padx=5)
        
        ttk.Button(
            search_frame, 
            text="Anterior", 
            command=self.find_previous
        ).pack(side="left")
        
        ttk.Button(
            search_frame, 
            text="Próximo", 
            command=self.find_next
        ).pack(side="left", padx=5)
        
        # Frame para ações
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Adicionar", 
            command=self.add_entry
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame, 
            text="Editar", 
            command=self.edit_selected
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame, 
            text="Excluir", 
            command=self.delete_selected
        ).pack(side="left", padx=5)
        
        # Botões de desfazer/refazer
        ttk.Button(
            action_frame, 
            text="Desfazer", 
            command=self.undo
        ).pack(side="right", padx=5)
        
        ttk.Button(
            action_frame, 
            text="Refazer", 
            command=self.redo
        ).pack(side="right")
        
        # Status bar para informações sobre arquivos
        self.status_var = tk.StringVar()
        self.status_var.set("Nenhum arquivo carregado")
        
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            anchor="w"
        ).pack(fill="x")
        
        # Frame para Treeview
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Criar treeview vazio (será atualizado quando um modelo for carregado)
        self.tree = ttk.Treeview(tree_frame)
        
        # Barra de rolagem vertical
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Barra de rolagem horizontal
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar evento de duplo clique para edição
        # Quando o usuário clica duas vezes, passamos o evento para que
        # o método edit_selected possa identificar a coluna clicada
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        
        # Configurar evento de clique único na coluna para destacá-la
        self.tree.bind("<ButtonRelease-1>", self.highlight_column)
    
    def toggle_theme(self):
        """Alterna entre temas claro e escuro."""
        self.is_dark_mode = not self.is_dark_mode
        self.theme = CustomTheme.apply_theme(self.root, self.is_dark_mode)
        
        # Atualizar texto do botão
        self.theme_button.configure(
            text="Tema Claro" if self.is_dark_mode else "Tema Escuro"
        )
        
        # Atualizar visualização
        self.update_tree()
    
    def handle_dropped_files(self, file_paths):
        """Processa arquivos arrastados para a aplicação."""
        if not file_paths:
            return
            
        # Determinar tipo de arquivo com base no conteúdo
        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if "__meta__" in data:
                    # Arquivo de modelo
                    self.load_model_file(path)
                else:
                    # Arquivo de dados
                    self.load_data_file(path)
                    
                # Processar apenas um arquivo válido por vez
                break
                    
            except Exception as e:
                messagebox.showerror(
                    "Erro ao carregar arquivo", 
                    f"Não foi possível processar o arquivo {path}: {str(e)}"
                )
    
    def load_model_file(self, file_path=None):
        """Carrega um arquivo de modelo JSON."""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Selecionar arquivo de modelo",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
        if not file_path:
            return
            
        try:
            self.json_model = JsonModel(file_path)
            
            # Atualizar status
            model_name = os.path.basename(file_path)
            self.status_var.set(f"Modelo: {model_name}")
            
            # Reconfigurar treeview com base no modelo
            self.setup_tree()
            
            # Se dados já estiverem carregados, validá-los
            if self.data:
                self.validate_data()
                
            messagebox.showinfo(
                "Modelo carregado", 
                f"Modelo {model_name} carregado com sucesso."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao carregar modelo", 
                f"Não foi possível carregar o modelo: {str(e)}"
            )
            traceback.print_exc()
    
    def load_data_file(self, file_path=None):
        """Carrega um arquivo de dados JSON."""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Selecionar arquivo de dados",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Verificar se é uma lista ou um objeto
            if isinstance(data, list):
                self.data = data
            else:
                # Se for um objeto, verificar se tem alguma propriedade que é uma lista
                for key, value in data.items():
                    if isinstance(value, list):
                        self.data = value
                        break
                else:
                    # Se não encontrar uma lista, converter o objeto em um item único
                    self.data = [data]
            
            self.data_file_path = file_path
            
            # Atualizar status
            data_name = os.path.basename(file_path)
            current_status = self.status_var.get()
            if current_status.startswith("Modelo:"):
                self.status_var.set(f"{current_status} | Dados: {data_name}")
            else:
                self.status_var.set(f"Dados: {data_name}")
            
            # Adicionar ao histórico
            self.add_to_history()
            
            # Se o modelo já estiver carregado, atualizar a árvore
            if self.json_model:
                self.update_tree()
                self.validate_data()
            else:
                messagebox.showinfo(
                    "Dados carregados", 
                    "Dados carregados, mas nenhum modelo definido. "
                    "Por favor, carregue um arquivo de modelo."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Erro ao carregar dados", 
                f"Não foi possível carregar os dados: {str(e)}"
            )
            traceback.print_exc()
    
    def setup_tree(self):
        """Configura o Treeview com base no modelo carregado."""
        # Limpar treeview existente
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            
        self.tree["columns"] = ()
        
        if not self.json_model:
            return
            
        # Obter campos do modelo
        fields = self.json_model.get_field_names()
        
        # Configurar colunas
        self.tree["columns"] = fields
        self.tree["show"] = "headings"  # Ocultar coluna de identificador
        
        # Configurar cabeçalhos
        for field in fields:
            field_type = self.json_model.get_field_type(field)
            is_required = self.json_model.is_field_required(field)
            
            # Adicionar indicador para campos obrigatórios
            header = f"{field} ({field_type})"
            if is_required:
                header += " *"
                
            self.tree.heading(field, text=header)
            
            # Ajustar largura com base no tipo
            if field_type == "bool":
                width = 80
            elif field_type in ["int", "float"]:
                width = 100
            elif field_type.startswith("list") or field_type in ["dict", "object"]:
                width = 200
            else:
                width = 150
                
            self.tree.column(field, width=width, minwidth=50)
    
    def update_tree(self):
        """Atualiza o Treeview com os dados carregados."""
        # Limpar entradas existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.data or not self.json_model:
            return
            
        # Adicionar dados
        for i, entry in enumerate(self.data):
            values = []
            
            for field in self.tree["columns"]:
                if field in entry:
                    value = entry[field]
                    
                    # Formatação especial para alguns tipos
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False)
                        if len(value) > 50:
                            value = value[:47] + "..."
                            
                    values.append(value)
                else:
                    values.append("")
            
            # Inserir na árvore com ID baseado no índice
            item_id = self.tree.insert("", "end", values=values, tags=(f"item_{i}",))
            
            # Validar entrada
            errors = self.json_model.validate_entry(entry)
            if errors:
                self.tree.item(item_id, tags=(f"item_{i}", "invalid"))
    
    def validate_data(self):
        """Valida os dados carregados contra o modelo."""
        if not self.json_model or not self.data:
            return
            
        # Validar todas as entradas
        all_errors = self.json_model.validate_data(self.data)
        
        if all_errors:
            # Formatar mensagem de erro
            error_msg = "Foram encontrados problemas de validação:\n\n"
            
            for index, errors in all_errors.items():
                error_msg += f"Entrada {index + 1}:\n"
                for error in errors:
                    error_msg += f"  - {error}\n"
                    
            messagebox.showwarning("Problemas de validação", error_msg)
            
            # Destacar entradas com erros
            for index in all_errors.keys():
                items = self.tree.get_children()
                if 0 <= index < len(items):
                    self.tree.item(items[index], tags=(f"item_{index}", "invalid"))
        
        # Configurar cores para itens inválidos
        self.tree.tag_configure("invalid", background=self.theme["invalid_bg"])
    
    def add_entry(self):
        """Adiciona uma nova entrada através do diálogo de múltiplos campos."""
        if not self.json_model:
            messagebox.showerror(
                "Erro",
                "Nenhum modelo carregado. Carregue um modelo primeiro."
            )
            return
            
        # Criar entrada vazia baseada no modelo
        new_entry = self.json_model.create_empty_entry()
        
        # Abrir diálogo para preencher todos os campos de uma vez
        dialog = self.MultiFieldEditDialog(
            self.root,
            self.json_model,
            new_entry,
            self.theme
        )
        
        # Esperar pelo fechamento do diálogo
        self.root.wait_window(dialog)
        
        # Verificar se o usuário confirmou ou cancelou
        if dialog.result:
            # Usar os valores informados pelo usuário
            new_entry = dialog.result
            
            # Adicionar à lista de dados
            self.data.append(new_entry)
            
            # Adicionar ao histórico
            self.add_to_history()
            
            # Atualizar visualização
            self.update_tree()
            
            # Selecionar a nova entrada
            last_item = self.tree.get_children()[-1]
            self.tree.selection_set(last_item)
            self.tree.see(last_item)
    
    def edit_selected(self):
        """Edita a entrada selecionada."""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showinfo("Selecione uma entrada", "Por favor, selecione uma entrada para editar.")
            return
            
        if not self.json_model:
            messagebox.showerror("Erro", "Nenhum modelo carregado.")
            return
            
        # Obter índice da entrada selecionada
        item_id = selection[0]
        item_index = self.tree.index(item_id)
        
        if item_index >= len(self.data):
            messagebox.showerror("Erro", "Índice de entrada inválido.")
            return
            
        # Obter a entrada a ser editada
        entry = self.data[item_index]
        
        # Verificar se o usuário clicou em uma coluna específica
        column = self.tree.identify_column(self.tree.winfo_pointerx() - self.tree.winfo_rootx())
        
        # Se nenhuma coluna específica foi clicada ou foi um duplo clique sem foco em coluna,
        # abrir o diálogo para editar todos os campos de uma vez
        if not column or column == "#0":
            # Usar o novo diálogo multi-campo
            dialog = self.MultiFieldEditDialog(
                self.root,
                self.json_model,
                entry,
                self.theme
            )
            
            # Esperar pelo fechamento do diálogo
            self.root.wait_window(dialog)
            
            # Processar resultado
            if dialog.result:
                # Atualizar a entrada com todos os valores de uma vez
                for field, value in dialog.result.items():
                    entry[field] = value
                
                # Adicionar ao histórico
                self.add_to_history()
                
                # Atualizar visualização
                self.update_tree()
                
                # Manter seleção
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
            
            return
        
        # Se uma coluna específica foi clicada, editar apenas esse campo
        column_index = int(column.replace('#', '')) - 1
        if column_index < 0 or column_index >= len(self.tree["columns"]):
            return
        
        # Obter o nome do campo correspondente à coluna
        field = self.tree["columns"][column_index]
        field_type = self.json_model.get_field_type(field)
        is_required = self.json_model.is_field_required(field)
        current_value = entry.get(field)
        
        # Abrir diálogo para editar apenas este campo
        dialog = EditDialog(
            self.root,
            field,
            field_type,
            current_value,
            is_required,
            self.theme
        )
        
        # Esperar pelo fechamento do diálogo
        self.root.wait_window(dialog)
        
        # Processar resultado
        if dialog.result is not None:
            entry[field] = dialog.result
            
            # Adicionar ao histórico
            self.add_to_history()
            
            # Atualizar visualização
            self.update_tree()
            
            # Manter seleção
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
    
    def delete_selected(self):
        """Exclui a entrada selecionada."""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showinfo("Selecione uma entrada", "Por favor, selecione uma entrada para excluir.")
            return
            
        # Confirmar exclusão
        confirm = messagebox.askyesno(
            "Confirmar exclusão", 
            "Tem certeza que deseja excluir a entrada selecionada?"
        )
        
        if not confirm:
            return
            
        # Excluir todas as entradas selecionadas
        indices = []
        for item_id in selection:
            indices.append(self.tree.index(item_id))
        
        # Ordenar índices em ordem decrescente para não afetar os índices subsequentes
        indices.sort(reverse=True)
        
        # Remover entradas
        for index in indices:
            if 0 <= index < len(self.data):
                del self.data[index]
        
        # Adicionar ao histórico
        self.add_to_history()
        
        # Atualizar visualização
        self.update_tree()
    
    def _setup_autosave(self):
        """Configura o salvamento automático."""
        autosave_interval = get_config("files.auto_save_interval", 0)
        if autosave_interval > 0:
            # Converter segundos para milissegundos
            interval_ms = autosave_interval * 1000
            self._autosave_timer_id = self.root.after(interval_ms, self._autosave)
    
    def _autosave(self):
        """Função de salvamento automático."""
        if self.data and self.data_file_path:
            try:
                # Salvar silenciosamente sem mostrar mensagens
                self._save_data_to_file(self.data_file_path, show_messages=False)
            except Exception as e:
                # Registrar erro, mas não interromper o usuário
                print(f"Erro no salvamento automático: {str(e)}")
                
        # Agendar próximo salvamento
        autosave_interval = get_config("files.auto_save_interval", 0)
        if autosave_interval > 0:
            interval_ms = autosave_interval * 1000
            self._autosave_timer_id = self.root.after(interval_ms, self._autosave)
            
    def save_data(self):
        """Salva os dados no arquivo atual ou solicita um novo caminho."""
        if not self.data:
            messagebox.showinfo("Sem dados", "Não há dados para salvar.")
            return
            
        # Determinar caminho do arquivo
        file_path = self.data_file_path
        
        if not file_path:
            return self.save_data_as()
            
        return self._save_data_to_file(file_path)
            
    def save_data_as(self):
        """Salva os dados em um novo arquivo JSON."""
        if not self.data:
            messagebox.showinfo("Sem dados", "Não há dados para salvar.")
            return
            
        # Solicitar novo caminho de arquivo
        file_path = filedialog.asksaveasfilename(
            title="Salvar arquivo de dados como",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
            
        if not file_path:
            return False
            
        return self._save_data_to_file(file_path)
    
    def _save_data_to_file(self, file_path, show_messages=True):
        """Salva os dados em um arquivo JSON específico."""
        try:
            # Validar dados antes de salvar, se configurado
            if get_config("validation.validate_on_save", True) and self.json_model:
                all_errors = self.json_model.validate_data(self.data)
                if all_errors:
                    if show_messages:
                        error_msg = "Há erros de validação nos dados. Deseja salvar mesmo assim?"
                        for index, errors in all_errors.items():
                            error_msg += f"\n\nEntrada {index + 1}:\n"
                            for error in errors:
                                error_msg += f"  - {error}\n"
                        
                        confirm = messagebox.askyesno(
                            "Erros de validação",
                            error_msg
                        )
                        
                        if not confirm:
                            return False
            
            # Usar função de salvamento com backup, se configurado
            if get_config("files.create_backups", True):
                indent = get_config("export.default_json_indent", 2)
                save_json_with_backup(self.data, file_path, indent)
            else:
                # Salvar diretamente
                with open(file_path, 'w', encoding=get_config("files.default_encoding", "utf-8")) as f:
                    json.dump(self.data, f, indent=get_config("export.default_json_indent", 2), ensure_ascii=False)
            
            # Atualizar caminho do arquivo atual
            self.data_file_path = file_path
            
            # Atualizar status
            data_name = os.path.basename(file_path)
            current_status = self.status_var.get()
            if current_status.startswith("Modelo:"):
                self.status_var.set(f"{current_status.split(' | ')[0]} | Dados: {data_name}")
            else:
                self.status_var.set(f"Dados: {data_name}")
            
            # Adicionar ao histórico apenas se for um salvamento iniciado pelo usuário
            if show_messages:
                self.add_to_history()
                messagebox.showinfo("Dados salvos", f"Dados salvos com sucesso em {data_name}.")
            
            return True
            
        except Exception as e:
            if show_messages:
                messagebox.showerror(
                    "Erro ao salvar dados",
                    f"Não foi possível salvar os dados: {str(e)}"
                )
            traceback.print_exc()
            return False
    
    def search(self):
        """Pesquisa nos dados por termo específico."""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            return
            
        # Limpar resultados anteriores
        self.search_results = []
        self.current_search_index = -1
        
        # Buscar em todos os campos de todas as entradas
        for i, entry in enumerate(self.data):
            for field, value in entry.items():
                # Converter valor para string para pesquisa
                str_value = str(value).lower()
                
                if search_term in str_value:
                    self.search_results.append(i)
                    break
        
        # Exibir resultados
        if not self.search_results:
            messagebox.showinfo("Pesquisa", "Nenhum resultado encontrado.")
        else:
            self.find_next()
    
    def find_next(self):
        """Navega para o próximo resultado da pesquisa."""
        if not self.search_results:
            return
            
        # Incrementar índice de busca
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        
        # Obter índice do item
        item_index = self.search_results[self.current_search_index]
        
        # Selecionar o item
        if 0 <= item_index < len(self.tree.get_children()):
            item_id = self.tree.get_children()[item_index]
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
            
            # Atualizar status
            self.status_var.set(
                f"Resultado {self.current_search_index + 1} de {len(self.search_results)}"
            )
    
    def find_previous(self):
        """Navega para o resultado anterior da pesquisa."""
        if not self.search_results:
            return
            
        # Decrementar índice de busca
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        
        # Obter índice do item
        item_index = self.search_results[self.current_search_index]
        
        # Selecionar o item
        if 0 <= item_index < len(self.tree.get_children()):
            item_id = self.tree.get_children()[item_index]
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
            
            # Atualizar status
            self.status_var.set(
                f"Resultado {self.current_search_index + 1} de {len(self.search_results)}"
            )
    
    def add_to_history(self):
        """Adiciona o estado atual ao histórico."""
        # Criar cópia profunda dos dados para o histórico
        state = json.loads(json.dumps(self.data))
        self.history.add(state)
    
    def undo(self):
        """Desfaz a última operação."""
        if not self.history.can_undo():
            return
            
        previous_state = self.history.undo()
        if previous_state is not None:
            self.data = previous_state
            self.update_tree()
    
    def redo(self):
        """Refaz a última operação desfeita."""
        if not self.history.can_redo():
            return
            
        next_state = self.history.redo()
        if next_state is not None:
            self.data = next_state
            self.update_tree()
            
    def highlight_column(self, event):
        """Destaca a coluna clicada para melhor visualização."""
        if not self.json_model:
            return
            
        # Identificar a coluna clicada
        column = self.tree.identify_column(event.x)
        
        if not column or column == "#0":
            return
            
        # Obter o índice da coluna (0-based)
        column_index = int(column.replace('#', '')) - 1
        
        if column_index < 0 or column_index >= len(self.tree["columns"]):
            return
            
        # Obter o nome do campo correspondente à coluna
        field = self.tree["columns"][column_index]
        field_type = self.json_model.get_field_type(field)
        is_required = self.json_model.is_field_required(field)
        
        # Atualizar a barra de status com informação sobre o campo
        self.status_var.set(
            f"Campo: {field} | Tipo: {field_type} | Obrigatório: {'Sim' if is_required else 'Não'}"
        )