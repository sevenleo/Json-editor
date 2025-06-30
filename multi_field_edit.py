import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Any, Dict, List, Optional, Union

class MultiFieldEditDialog(tk.Toplevel):
    """Diálogo para edição de múltiplos campos de uma entrada JSON."""
    
    def __init__(self, parent, json_model, current_values=None, theme=None):
        super().__init__(parent)
        self.parent = parent
        self.json_model = json_model
        self.current_values = current_values or {}
        self.theme = theme or {}
        self.result = None
        self.field_widgets = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        self.title("Editar Campos")
        self.configure(bg=self.theme.get("bg", "#F0F0F0"))
        
        # Tamanho da janela
        window_width = 600
        window_height = 500
        
        # Posicionar no centro da janela pai
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(True, True)
        
        # Frame principal com scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame, bg=self.theme.get("bg", "#F0F0F0"))
        canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame para conteúdo
        content_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Título
        title_label = ttk.Label(
            content_frame, 
            text="Editar Campos", 
            font=("", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")
        
        # Cabeçalhos
        ttk.Label(
            content_frame, 
            text="Campo", 
            font=("", 10, "bold")
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        ttk.Label(
            content_frame, 
            text="Tipo", 
            font=("", 10, "bold")
        ).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(
            content_frame, 
            text="Valor", 
            font=("", 10, "bold")
        ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Separador
        separator = ttk.Separator(content_frame, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Criar widgets para cada campo
        row = 3
        fields = self.json_model.get_field_names()
        
        for field in fields:
            field_type = self.json_model.get_field_type(field)
            is_required = self.json_model.is_field_required(field)
            current_value = self.current_values.get(field)
            
            # Nome do campo (com indicador se é obrigatório)
            field_label = ttk.Label(
                content_frame,
                text=f"{field} {'*' if is_required else ''}"
            )
            field_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            # Tipo do campo
            type_label = ttk.Label(content_frame, text=field_type)
            type_label.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            
            # Widget para o valor
            value_widget = self.create_field_widget(content_frame, field_type, current_value)
            value_widget.grid(row=row, column=2, padx=5, pady=5, sticky="ew")
            
            # Armazenar referência ao widget
            self.field_widgets[field] = {
                "widget": value_widget,
                "type": field_type,
                "required": is_required
            }
            
            row += 1
        
        # Configurar expansão da coluna de valor
        content_frame.grid_columnconfigure(2, weight=1)
        
        # Botões
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.cancel
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Salvar", 
            command=self.save
        ).pack(side="right")
        
        # Configurar redimensionamento do canvas
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        content_frame.bind("<Configure>", configure_canvas)
        
        # Configurar scroll com o mouse
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        
        # Tornar modal
        self.transient(self.parent)
        self.grab_set()
        self.focus_set()
    
    def create_field_widget(self, parent, field_type, current_value):
        """Cria o widget apropriado para o tipo do campo."""
        if field_type == "str":
            widget = ttk.Entry(parent)
            widget.insert(0, str(current_value) if current_value is not None else "")
            return widget
            
        elif field_type == "int":
            vcmd = (self.register(self.validate_int), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            widget.insert(0, str(current_value) if current_value is not None else "0")
            return widget
            
        elif field_type == "float":
            vcmd = (self.register(self.validate_float), '%P')
            widget = ttk.Entry(parent, validate="key", validatecommand=vcmd)
            widget.insert(0, str(current_value) if current_value is not None else "0.0")
            return widget
            
        elif field_type == "bool":
            var = tk.BooleanVar(value=bool(current_value) if current_value is not None else False)
            widget = ttk.Checkbutton(parent, variable=var)
            widget.var = var  # Armazenar referência à variável
            return widget
            
        elif field_type == "list" or field_type.startswith("list["):
            # Criar um frame para a lista com scrollbar
            list_container = ttk.Frame(parent)
            canvas = tk.Canvas(list_container, height=100)
            scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
            list_frame = ttk.Frame(canvas)
            
            # Configurar o canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Criar janela no canvas para o frame
            canvas_window = canvas.create_window((0, 0), window=list_frame, anchor="nw")
            
            # Configurar o redimensionamento
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(canvas_window, width=event.width)
            
            list_frame.bind("<Configure>", configure_scroll_region)
            
            # Criar widget composto
            widget = ttk.Frame(parent)
            widget.list_frame = list_frame
            widget.entries = []
            widget.canvas = canvas
            
            # Botões para adicionar/remover itens
            btn_frame = ttk.Frame(widget)
            btn_frame.pack(fill="x", side="bottom", pady=2)
            
            ttk.Button(btn_frame, text="Adicionar Item",
                      command=lambda w=widget, lf=list_frame: self.add_list_item(w, lf)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Remover Último",
                      command=lambda w=widget: self.remove_list_item(w)).pack(side="left")
            
            # Adicionar o container ao widget principal
            list_container.pack(fill="both", expand=True)
            
            # Adicionar itens da lista atual
            if current_value and isinstance(current_value, list):
                for item in current_value:
                    self.add_list_item(widget, list_frame, item)
            
            # Se a lista estiver vazia, adicionar um item em branco
            if not widget.entries:
                self.add_list_item(widget, list_frame)
                
            return widget
                
        elif field_type == "dict" or field_type == "object":
            # Criar um frame para o dicionário com scrollbar
            dict_container = ttk.Frame(parent)
            canvas = tk.Canvas(dict_container, height=100)
            scrollbar = ttk.Scrollbar(dict_container, orient="vertical", command=canvas.yview)
            dict_frame = ttk.Frame(canvas)
            
            # Configurar o canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Criar janela no canvas para o frame
            canvas_window = canvas.create_window((0, 0), window=dict_frame, anchor="nw")
            
            # Configurar o redimensionamento
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig(canvas_window, width=event.width)
            
            dict_frame.bind("<Configure>", configure_scroll_region)
            
            # Criar widget composto
            widget = ttk.Frame(parent)
            widget.dict_frame = dict_frame
            widget.entries = []
            widget.canvas = canvas
            
            # Botões para adicionar/remover pares
            btn_frame = ttk.Frame(widget)
            btn_frame.pack(fill="x", side="bottom", pady=2)
            
            ttk.Button(btn_frame, text="Adicionar Par",
                      command=lambda w=widget, df=dict_frame: self.add_dict_pair(w, df)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Remover Último",
                      command=lambda w=widget: self.remove_dict_pair(w)).pack(side="left")
            
            # Adicionar o container ao widget principal
            dict_container.pack(fill="both", expand=True)
            
            # Adicionar pares do dicionário atual
            if current_value and isinstance(current_value, dict):
                for key, value in current_value.items():
                    self.add_dict_pair(widget, dict_frame, key, value)
            
            # Se o dicionário estiver vazio, adicionar um par em branco
            if not widget.entries:
                self.add_dict_pair(widget, dict_frame)
                
            return widget
        
        # Caso padrão
        widget = ttk.Entry(parent)
        widget.insert(0, str(current_value) if current_value is not None else "")
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
    
    def get_field_value(self, field_name):
        """Obtém o valor de um campo específico."""
        if field_name not in self.field_widgets:
            return None
            
        field_info = self.field_widgets[field_name]
        widget = field_info["widget"]
        field_type = field_info["type"]
        
        try:
            if field_type == "str":
                return widget.get()
                
            elif field_type == "int":
                value = widget.get()
                # Se o valor estiver vazio e não for um campo obrigatório, permitir null
                if not value:
                    is_required = field_info.get("required", False)
                    return None if not is_required else 0
                return int(value)
                
            elif field_type == "float":
                value = widget.get()
                # Se o valor estiver vazio e não for um campo obrigatório, permitir null
                if not value:
                    is_required = field_info.get("required", False)
                    return None if not is_required else 0.0
                return float(value)
                
            elif field_type == "bool":
                return widget.var.get()
                
            elif field_type == "list" or field_type.startswith("list["):
                # Coletar valores dos campos de entrada
                list_values = []
                inner_type = field_type[5:-1] if field_type.startswith("list[") else None
                
                for entry_widget in widget.entries:
                    value = entry_widget.get().strip()
                    if value:  # Ignorar entradas vazias
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
                
                return list_values
                
            elif field_type == "dict" or field_type == "object":
                # Coletar pares chave-valor dos campos de entrada
                dict_values = {}
                
                for key_widget, value_widget in widget.entries:
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
                
                return dict_values
                
            return None
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao obter valor", 
                f"Erro ao obter valor do campo {field_name}: {str(e)}"
            )
            return None
    
    def save(self):
        """Salva os valores editados."""
        result = {}
        errors = []
        
        # Coletar valores de todos os campos
        for field_name, field_info in self.field_widgets.items():
            try:
                value = self.get_field_value(field_name)
                
                # Validar campos obrigatórios
                if field_info["required"] and (value is None or (isinstance(value, str) and value.strip() == "")):
                    errors.append(f"O campo '{field_name}' é obrigatório")
                    continue
                
                # Validar tipo para listas tipadas
                field_type = field_info["type"]
                if field_type.startswith("list[") and value:
                    inner_type = field_type[5:-1]
                    
                    for i, item in enumerate(value):
                        if inner_type == "str" and not isinstance(item, str):
                            errors.append(f"Item {i} em '{field_name}' deve ser do tipo string")
                        elif inner_type == "int" and not isinstance(item, int):
                            errors.append(f"Item {i} em '{field_name}' deve ser do tipo inteiro")
                        elif inner_type == "float" and not isinstance(item, (int, float)):
                            errors.append(f"Item {i} em '{field_name}' deve ser do tipo número")
                        elif inner_type == "bool" and not isinstance(item, bool):
                            errors.append(f"Item {i} em '{field_name}' deve ser do tipo booleano")
                
                # Adicionar ao resultado
                result[field_name] = value
                
            except Exception as e:
                errors.append(f"Erro no campo '{field_name}': {str(e)}")
        
        # Exibir erros, se houver
        if errors:
            error_msg = "\n".join(errors)
            messagebox.showerror("Erros de validação", error_msg)
            return
        
        # Armazenar resultado
        self.result = result
        self.destroy()
    
    def cancel(self):
        """Cancela a edição."""
        self.result = None
        self.destroy()
        
    def add_list_item(self, widget, list_frame, value=None):
        """Adiciona um novo item à lista."""
        # Frame para o item
        item_frame = ttk.Frame(list_frame)
        item_frame.pack(fill="x", pady=2, padx=2)
        
        # Entrada para o valor do item
        entry = ttk.Entry(item_frame)
        entry.pack(side="left", fill="x", expand=True)
        
        # Preencher com o valor, se fornecido
        if value is not None:
            entry.insert(0, str(value))
            
        # Adicionar à lista de entradas
        widget.entries.append(entry)
        
        # Atualizar a região de rolagem
        widget.canvas.update_idletasks()
        widget.canvas.configure(scrollregion=widget.canvas.bbox("all"))
        
        return entry
        
    def remove_list_item(self, widget):
        """Remove o último item da lista."""
        if widget.entries:
            # Remover o último widget de entrada
            entry = widget.entries.pop()
            entry.master.destroy()  # Destruir o frame pai
            
            # Atualizar a região de rolagem
            widget.canvas.update_idletasks()
            widget.canvas.configure(scrollregion=widget.canvas.bbox("all"))
            
    def add_dict_pair(self, widget, dict_frame, key=None, value=None):
        """Adiciona um novo par chave-valor ao dicionário."""
        # Frame para o par
        pair_frame = ttk.Frame(dict_frame)
        pair_frame.pack(fill="x", pady=2, padx=2)
        
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
        
        # Atualizar a região de rolagem
        widget.canvas.update_idletasks()
        widget.canvas.configure(scrollregion=widget.canvas.bbox("all"))
        
        return key_entry, value_entry
        
    def remove_dict_pair(self, widget):
        """Remove o último par do dicionário."""
        if widget.entries:
            # Remover o último par de widgets
            pair = widget.entries.pop()
            pair[0].master.destroy()  # Destruir o frame pai
            
            # Atualizar a região de rolagem
            widget.canvas.update_idletasks()
            widget.canvas.configure(scrollregion=widget.canvas.bbox("all"))