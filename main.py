import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import sys
from json_editor import JsonEditorApp
from json_model import JsonModel, JsonModelError
from config import config, get_config

class ConfigDialog(tk.Toplevel):
    """Diálogo para edição de configurações do sistema."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Configurações")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Tornar modal
        self.transient(parent)
        self.grab_set()
        
        # Configurar tema
        self.is_dark_mode = get_config("ui.dark_mode_default", False)
        
        # Configurar interface
        self.setup_ui()
        
        # Centralizar
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_width()) // 2
        y = (screen_height - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Configura a interface do diálogo de configurações."""
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Notebook para separar categorias
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Abas para cada categoria
        ui_frame = ttk.Frame(notebook, padding=10)
        files_frame = ttk.Frame(notebook, padding=10)
        validation_frame = ttk.Frame(notebook, padding=10)
        export_frame = ttk.Frame(notebook, padding=10)
        directories_frame = ttk.Frame(notebook, padding=10)
        
        notebook.add(ui_frame, text="Interface")
        notebook.add(files_frame, text="Arquivos")
        notebook.add(validation_frame, text="Validação")
        notebook.add(export_frame, text="Exportação")
        notebook.add(directories_frame, text="Diretórios")
        
        # Configurações de Interface
        self.setup_ui_tab(ui_frame)
        
        # Configurações de Arquivos
        self.setup_files_tab(files_frame)
        
        # Configurações de Validação
        self.setup_validation_tab(validation_frame)
        
        # Configurações de Exportação
        self.setup_export_tab(export_frame)
        
        # Configurações de Diretórios
        self.setup_directories_tab(directories_frame)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Restaurar Padrões", 
            command=self.reset_defaults
        ).pack(side="left", padx=5)
        
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
    
    def setup_ui_tab(self, parent):
        """Configura a aba de Interface."""
        # Tamanho da janela
        size_frame = ttk.LabelFrame(parent, text="Tamanho da Janela", padding=10)
        size_frame.pack(fill="x", pady=5)
        
        ttk.Label(size_frame, text="Largura:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.width_var = tk.IntVar(value=get_config("ui.window_width", 1000))
        ttk.Spinbox(
            size_frame, 
            from_=800, 
            to=1920, 
            increment=50, 
            textvariable=self.width_var
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(size_frame, text="Altura:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.height_var = tk.IntVar(value=get_config("ui.window_height", 700))
        ttk.Spinbox(
            size_frame, 
            from_=600, 
            to=1080, 
            increment=50, 
            textvariable=self.height_var
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        size_frame.grid_columnconfigure(1, weight=1)
        
        # Tema e aparência
        theme_frame = ttk.LabelFrame(parent, text="Tema e Aparência", padding=10)
        theme_frame.pack(fill="x", pady=5)
        
        self.dark_mode_var = tk.BooleanVar(value=get_config("ui.dark_mode_default", False))
        ttk.Checkbutton(
            theme_frame, 
            text="Usar tema escuro por padrão", 
            variable=self.dark_mode_var
        ).pack(anchor="w", pady=2)
        
        self.show_tooltips_var = tk.BooleanVar(value=get_config("ui.show_tooltips", True))
        ttk.Checkbutton(
            theme_frame, 
            text="Mostrar dicas de ferramentas", 
            variable=self.show_tooltips_var
        ).pack(anchor="w", pady=2)
        
        self.show_types_var = tk.BooleanVar(value=get_config("ui.show_field_types_in_headers", True))
        ttk.Checkbutton(
            theme_frame, 
            text="Mostrar tipos nos cabeçalhos", 
            variable=self.show_types_var
        ).pack(anchor="w", pady=2)
        
        # Fonte
        font_frame = ttk.LabelFrame(parent, text="Fonte", padding=10)
        font_frame.pack(fill="x", pady=5)
        
        ttk.Label(font_frame, text="Tamanho da fonte:").pack(side="left", padx=5)
        
        self.font_size_var = tk.IntVar(value=get_config("ui.font_size", 10))
        ttk.Spinbox(
            font_frame, 
            from_=8, 
            to=16, 
            increment=1, 
            textvariable=self.font_size_var,
            width=5
        ).pack(side="left", padx=5)
        
        # Comportamento
        behavior_frame = ttk.LabelFrame(parent, text="Comportamento", padding=10)
        behavior_frame.pack(fill="x", pady=5)
        
        self.drag_drop_var = tk.BooleanVar(value=get_config("ui.enable_drag_drop", True))
        ttk.Checkbutton(
            behavior_frame, 
            text="Habilitar arrastar e soltar arquivos", 
            variable=self.drag_drop_var
        ).pack(anchor="w", pady=2)
        
        self.confirm_delete_var = tk.BooleanVar(value=get_config("ui.confirm_before_delete", True))
        ttk.Checkbutton(
            behavior_frame, 
            text="Confirmar antes de excluir", 
            variable=self.confirm_delete_var
        ).pack(anchor="w", pady=2)
        
        ttk.Label(behavior_frame, text="Tamanho máximo do histórico:").pack(anchor="w", pady=2)
        
        self.history_size_var = tk.IntVar(value=get_config("ui.max_history_size", 50))
        ttk.Spinbox(
            behavior_frame, 
            from_=10, 
            to=200, 
            increment=10, 
            textvariable=self.history_size_var,
            width=5
        ).pack(anchor="w", padx=20, pady=2)
    
    def setup_files_tab(self, parent):
        """Configura a aba de Arquivos."""
        # Backup e Salvamento
        backup_frame = ttk.LabelFrame(parent, text="Backup e Salvamento", padding=10)
        backup_frame.pack(fill="x", pady=5)
        
        self.create_backups_var = tk.BooleanVar(value=get_config("files.create_backups", True))
        ttk.Checkbutton(
            backup_frame, 
            text="Criar backups antes de salvar", 
            variable=self.create_backups_var
        ).pack(anchor="w", pady=2)
        
        ttk.Label(backup_frame, text="Intervalo de salvamento automático (segundos):").pack(anchor="w", pady=2)
        ttk.Label(backup_frame, text="0 = desativado").pack(anchor="w", padx=20, pady=0)
        
        self.auto_save_var = tk.IntVar(value=get_config("files.auto_save_interval", 300))
        ttk.Spinbox(
            backup_frame, 
            from_=0, 
            to=3600, 
            increment=60, 
            textvariable=self.auto_save_var,
            width=5
        ).pack(anchor="w", padx=20, pady=2)
        
        # Arquivos grandes
        large_files_frame = ttk.LabelFrame(parent, text="Arquivos Grandes", padding=10)
        large_files_frame.pack(fill="x", pady=5)
        
        ttk.Label(large_files_frame, text="Limite para considerar arquivo grande (MB):").pack(anchor="w", pady=2)
        
        self.large_file_var = tk.DoubleVar(value=get_config("files.large_file_threshold_mb", 10.0))
        ttk.Spinbox(
            large_files_frame, 
            from_=1, 
            to=100, 
            increment=1, 
            textvariable=self.large_file_var,
            width=5
        ).pack(anchor="w", padx=20, pady=2)
        
        # Codificação
        encoding_frame = ttk.LabelFrame(parent, text="Codificação", padding=10)
        encoding_frame.pack(fill="x", pady=5)
        
        ttk.Label(encoding_frame, text="Codificação padrão:").pack(side="left", padx=5)
        
        self.encoding_var = tk.StringVar(value=get_config("files.default_encoding", "utf-8"))
        encodings = ["utf-8", "utf-16", "latin-1", "ascii", "cp1252"]
        ttk.Combobox(
            encoding_frame, 
            textvariable=self.encoding_var,
            values=encodings,
            state="readonly",
            width=10
        ).pack(side="left", padx=5)
        
        # Arquivos recentes
        recent_frame = ttk.LabelFrame(parent, text="Arquivos Recentes", padding=10)
        recent_frame.pack(fill="x", pady=5)
        
        ttk.Label(recent_frame, text="Número de arquivos recentes para lembrar:").pack(anchor="w", pady=2)
        
        self.recent_files_var = tk.IntVar(value=get_config("files.recent_files_count", 10))
        ttk.Spinbox(
            recent_frame, 
            from_=0, 
            to=30, 
            increment=1, 
            textvariable=self.recent_files_var,
            width=5
        ).pack(anchor="w", padx=20, pady=2)
    
    def setup_validation_tab(self, parent):
        """Configura a aba de Validação."""
        # Quando validar
        when_frame = ttk.LabelFrame(parent, text="Quando Validar", padding=10)
        when_frame.pack(fill="x", pady=5)
        
        self.validate_load_var = tk.BooleanVar(value=get_config("validation.validate_on_load", True))
        ttk.Checkbutton(
            when_frame, 
            text="Validar ao carregar arquivo", 
            variable=self.validate_load_var
        ).pack(anchor="w", pady=2)
        
        self.validate_save_var = tk.BooleanVar(value=get_config("validation.validate_on_save", True))
        ttk.Checkbutton(
            when_frame, 
            text="Validar antes de salvar", 
            variable=self.validate_save_var
        ).pack(anchor="w", pady=2)
        
        self.validate_edit_var = tk.BooleanVar(value=get_config("validation.validate_on_edit", True))
        ttk.Checkbutton(
            when_frame, 
            text="Validar ao editar campos", 
            variable=self.validate_edit_var
        ).pack(anchor="w", pady=2)
        
        # Comportamento da validação
        behavior_frame = ttk.LabelFrame(parent, text="Comportamento da Validação", padding=10)
        behavior_frame.pack(fill="x", pady=5)
        
        self.strict_type_var = tk.BooleanVar(value=get_config("validation.strict_type_checking", True))
        ttk.Checkbutton(
            behavior_frame, 
            text="Verificação estrita de tipos", 
            variable=self.strict_type_var
        ).pack(anchor="w", pady=2)
        
        self.allow_extra_var = tk.BooleanVar(value=get_config("validation.allow_extra_fields", False))
        ttk.Checkbutton(
            behavior_frame, 
            text="Permitir campos extras não definidos no modelo", 
            variable=self.allow_extra_var
        ).pack(anchor="w", pady=2)
    
    def setup_export_tab(self, parent):
        """Configura a aba de Exportação."""
        # JSON
        json_frame = ttk.LabelFrame(parent, text="JSON", padding=10)
        json_frame.pack(fill="x", pady=5)
        
        ttk.Label(json_frame, text="Indentação padrão (espaços):").pack(anchor="w", pady=2)
        
        self.json_indent_var = tk.IntVar(value=get_config("export.default_json_indent", 2))
        ttk.Spinbox(
            json_frame, 
            from_=0, 
            to=8, 
            increment=1, 
            textvariable=self.json_indent_var,
            width=5
        ).pack(anchor="w", padx=20, pady=2)
        
        # CSV
        csv_frame = ttk.LabelFrame(parent, text="CSV", padding=10)
        csv_frame.pack(fill="x", pady=5)
        
        ttk.Label(csv_frame, text="Delimitador:").pack(side="left", padx=5)
        
        self.csv_delimiter_var = tk.StringVar(value=get_config("export.csv_delimiter", ","))
        delimiters = [",", ";", "\t", "|", " "]
        ttk.Combobox(
            csv_frame, 
            textvariable=self.csv_delimiter_var,
            values=delimiters,
            width=5
        ).pack(side="left", padx=5)
        
        self.csv_header_var = tk.BooleanVar(value=get_config("export.csv_include_header", True))
        ttk.Checkbutton(
            csv_frame, 
            text="Incluir cabeçalho", 
            variable=self.csv_header_var
        ).pack(side="left", padx=20)
        
        # Excel
        excel_frame = ttk.LabelFrame(parent, text="Excel", padding=10)
        excel_frame.pack(fill="x", pady=5)
        
        ttk.Label(excel_frame, text="Nome da planilha padrão:").pack(side="left", padx=5)
        
        self.excel_sheet_var = tk.StringVar(value=get_config("export.excel_sheet_name", "JSON Data"))
        ttk.Entry(
            excel_frame, 
            textvariable=self.excel_sheet_var,
            width=20
        ).pack(side="left", padx=5)
    
    def setup_directories_tab(self, parent):
        """Configura a aba de Diretórios."""
        dirs = get_config("directories", {})
        
        # Frame para diretórios
        dirs_frame = ttk.Frame(parent, padding=10)
        dirs_frame.pack(fill="both", expand=True)
        
        # Variáveis para cada diretório
        self.dir_vars = {}
        
        # Adicionar campos para cada diretório
        row = 0
        for dir_name, dir_path in dirs.items():
            ttk.Label(dirs_frame, text=f"{dir_name.capitalize()}:").grid(
                row=row, column=0, sticky="w", padx=5, pady=5
            )
            
            self.dir_vars[dir_name] = tk.StringVar(value=dir_path)
            entry = ttk.Entry(dirs_frame, textvariable=self.dir_vars[dir_name], width=40)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            
            ttk.Button(
                dirs_frame, 
                text="Selecionar", 
                command=lambda name=dir_name: self.select_directory(name)
            ).grid(row=row, column=2, padx=5, pady=5)
            
            row += 1
        
        dirs_frame.grid_columnconfigure(1, weight=1)
        
        # Explicação
        ttk.Label(
            parent, 
            text="Nota: Alterações nos diretórios terão efeito após reiniciar o aplicativo.",
            foreground="gray"
        ).pack(anchor="w", padx=10, pady=10)
    
    def select_directory(self, dir_name):
        """Abre diálogo para selecionar diretório."""
        current_path = self.dir_vars[dir_name].get()
        new_path = filedialog.askdirectory(initialdir=current_path)
        
        if new_path:
            self.dir_vars[dir_name].set(new_path)
    
    def save(self):
        """Salva as configurações e fecha o diálogo."""
        # Interface
        config.set("ui.window_width", self.width_var.get())
        config.set("ui.window_height", self.height_var.get())
        config.set("ui.dark_mode_default", self.dark_mode_var.get())
        config.set("ui.show_tooltips", self.show_tooltips_var.get())
        config.set("ui.show_field_types_in_headers", self.show_types_var.get())
        config.set("ui.font_size", self.font_size_var.get())
        config.set("ui.enable_drag_drop", self.drag_drop_var.get())
        config.set("ui.confirm_before_delete", self.confirm_delete_var.get())
        config.set("ui.max_history_size", self.history_size_var.get())
        
        # Arquivos
        config.set("files.create_backups", self.create_backups_var.get())
        config.set("files.auto_save_interval", self.auto_save_var.get())
        config.set("files.large_file_threshold_mb", self.large_file_var.get())
        config.set("files.default_encoding", self.encoding_var.get())
        config.set("files.recent_files_count", self.recent_files_var.get())
        
        # Validação
        config.set("validation.validate_on_load", self.validate_load_var.get())
        config.set("validation.validate_on_save", self.validate_save_var.get())
        config.set("validation.validate_on_edit", self.validate_edit_var.get())
        config.set("validation.strict_type_checking", self.strict_type_var.get())
        config.set("validation.allow_extra_fields", self.allow_extra_var.get())
        
        # Exportação
        config.set("export.default_json_indent", self.json_indent_var.get())
        config.set("export.csv_delimiter", self.csv_delimiter_var.get())
        config.set("export.csv_include_header", self.csv_header_var.get())
        config.set("export.excel_sheet_name", self.excel_sheet_var.get())
        
        # Diretórios
        for dir_name, var in self.dir_vars.items():
            config.set(f"directories.{dir_name}", var.get())
        
        # Salvar configurações
        config.save()
        
        # Fechar diálogo
        self.destroy()
    
    def cancel(self):
        """Cancela as alterações e fecha o diálogo."""
        self.destroy()
    
    def reset_defaults(self):
        """Redefine as configurações para os valores padrão."""
        confirm = messagebox.askyesno(
            "Confirmar Redefinição",
            "Tem certeza que deseja redefinir todas as configurações para os valores padrão?",
            parent=self
        )
        
        if confirm:
            config.reset()
            self.destroy()
            messagebox.showinfo(
                "Configurações Redefinidas",
                "As configurações foram redefinidas para os valores padrão.\n"
                "As alterações terão efeito após reiniciar o aplicativo."
            )

def main():
    """Função principal para iniciar a aplicação."""
    root = tk.Tk()
    root.title("Editor de Banco de Dados JSON")
    
    # Verificar e criar diretórios necessários
    create_required_directories()
    
    # Verificar e criar arquivos de exemplo se não existirem
    check_example_files()
    
    # Obter dimensões da janela a partir das configurações
    window_width = get_config("ui.window_width", 1000)
    window_height = get_config("ui.window_height", 700)
    
    # Centralizar janela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Criar menu
    create_menu(root)
    
    # Iniciar a aplicação
    app = JsonEditorApp(root)
    
    # Guardar referência global
    root.app = app
    
    # Iniciar loop principal
    root.mainloop()

def create_required_directories():
    """Cria os diretórios necessários para a aplicação."""
    for dir_name, dir_path in get_config("directories", {}).items():
        os.makedirs(dir_path, exist_ok=True)

def check_example_files():
    """Verifica e cria arquivos de exemplo se necessário."""
    # Obter diretório de exemplos
    examples_dir = get_config("directories.examples", "examples")
    os.makedirs(examples_dir, exist_ok=True)
    
    # Criar arquivo de modelo de exemplo
    example_model_path = os.path.join(examples_dir, "example_model.json")
    if not os.path.exists(example_model_path):
        example_model = {
            "__meta__": {
                "name": {"type": "str", "required": True},
                "email": {"type": "str", "required": False},
                "age": {"type": "int", "required": False},
                "active": {"type": "bool", "required": True},
                "tags": {"type": "list[str]", "required": False},
                "address": {"type": "dict", "required": False}
            }
        }
        
        with open(example_model_path, 'w', encoding='utf-8') as f:
            json.dump(example_model, f, indent=2, ensure_ascii=False)
    
    # Criar arquivo de dados de exemplo
    example_data_path = os.path.join(examples_dir, "example_data.json")
    if not os.path.exists(example_data_path):
        example_data = [
            {
                "name": "João Silva",
                "email": "joao@exemplo.com",
                "age": 30,
                "active": True,
                "tags": ["cliente", "premium"],
                "address": {
                    "street": "Rua Exemplo",
                    "number": 123,
                    "city": "São Paulo"
                }
            },
            {
                "name": "Maria Oliveira",
                "email": "maria@exemplo.com",
                "age": 25,
                "active": True,
                "tags": ["cliente", "normal"],
                "address": {
                    "street": "Avenida Teste",
                    "number": 456,
                    "city": "Rio de Janeiro"
                }
            },
            {
                "name": "Pedro Santos",
                "active": False
            }
        ]
        
        with open(example_data_path, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, indent=2, ensure_ascii=False)

def create_menu(root):
    """Cria o menu principal."""
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    # Menu Arquivo
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Arquivo", menu=file_menu)
    
    file_menu.add_command(label="Carregar Modelo", command=lambda: root.app.load_model_file())
    file_menu.add_command(label="Carregar Dados", command=lambda: root.app.load_data_file())
    file_menu.add_separator()
    file_menu.add_command(label="Salvar", command=lambda: root.app.save_data())
    file_menu.add_command(label="Salvar Como...", command=lambda: root.app.save_data_as())
    file_menu.add_separator()
    file_menu.add_command(label="Sair", command=root.quit)
    
    # Menu Editar
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Editar", menu=edit_menu)
    
    edit_menu.add_command(label="Desfazer", command=lambda: root.app.undo())
    edit_menu.add_command(label="Refazer", command=lambda: root.app.redo())
    edit_menu.add_separator()
    edit_menu.add_command(label="Adicionar Entrada", command=lambda: root.app.add_entry())
    edit_menu.add_command(label="Editar Selecionada", command=lambda: root.app.edit_selected())
    edit_menu.add_command(label="Excluir Selecionada", command=lambda: root.app.delete_selected())
    edit_menu.add_separator()
    edit_menu.add_command(label="Pesquisar", command=lambda: root.app.search_entry.focus_set())
    
    # Menu Ferramentas
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Ferramentas", menu=tools_menu)
    
    tools_menu.add_command(label="Validar Dados", command=lambda: root.app.validate_data())
    tools_menu.add_separator()
    tools_menu.add_command(label="Exportar para CSV", command=lambda: export_to_csv(root.app))
    tools_menu.add_command(label="Importar de CSV", command=lambda: import_from_csv(root.app))
    
    # Menu Visualizar
    view_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Visualizar", menu=view_menu)
    
    view_menu.add_command(label="Alternar Tema", command=lambda: root.app.toggle_theme())
    
    # Menu Configurações
    settings_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Configurações", menu=settings_menu)
    
    settings_menu.add_command(label="Preferências", command=lambda: open_config_dialog(root))
    
    # Menu Ajuda
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Ajuda", menu=help_menu)
    
    help_menu.add_command(label="Sobre", command=lambda: show_about_dialog(root))
    help_menu.add_command(label="Ajuda", command=lambda: show_help(root))

def open_config_dialog(root):
    """Abre o diálogo de configurações."""
    ConfigDialog(root)

def export_to_csv(app):
    """Exporta dados para CSV."""
    if not app.data:
        messagebox.showinfo("Exportar para CSV", "Não há dados para exportar.")
        return
        
    # Obter caminho para salvar
    file_path = filedialog.asksaveasfilename(
        title="Exportar para CSV",
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    
    if not file_path:
        return
        
    try:
        from json_utils import convert_json_to_csv
        
        # Obter configurações
        delimiter = get_config("export.csv_delimiter", ",")
        include_header = get_config("export.csv_include_header", True)
        
        # Criar arquivo temporário com os dados
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w+")
        json.dump(app.data, temp_file, ensure_ascii=False)
        temp_file.close()
        
        # Converter para CSV
        convert_json_to_csv(temp_file.name, file_path, delimiter, include_header)
        
        # Remover arquivo temporário
        os.unlink(temp_file.name)
        
        messagebox.showinfo(
            "Exportação Concluída", 
            f"Dados exportados com sucesso para {file_path}."
        )
        
    except Exception as e:
        messagebox.showerror(
            "Erro na Exportação", 
            f"Não foi possível exportar para CSV: {str(e)}"
        )

def import_from_csv(app):
    """Importa dados de CSV."""
    # Verificar se há modelo carregado
    if not app.json_model:
        messagebox.showerror(
            "Erro", 
            "Nenhum modelo carregado. Carregue um modelo primeiro."
        )
        return
        
    # Obter caminho do arquivo CSV
    file_path = filedialog.askopenfilename(
        title="Importar de CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    
    if not file_path:
        return
        
    try:
        from json_utils import convert_csv_to_json
        
        # Obter configurações
        delimiter = get_config("export.csv_delimiter", ",")
        
        # Criar arquivo temporário para receber dados JSON
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        temp_file.close()
        
        # Converter CSV para JSON
        convert_csv_to_json(file_path, temp_file.name, delimiter, True)
        
        # Carregar dados
        app.load_data_file(temp_file.name)
        
        # Remover arquivo temporário
        os.unlink(temp_file.name)
        
    except Exception as e:
        messagebox.showerror(
            "Erro na Importação", 
            f"Não foi possível importar do CSV: {str(e)}"
        )

def show_about_dialog(root):
    """Mostra o diálogo 'Sobre'."""
    about_window = tk.Toplevel(root)
    about_window.title("Sobre")
    about_window.geometry("400x300")
    about_window.resizable(False, False)
    
    # Tornar modal
    about_window.transient(root)
    about_window.grab_set()
    
    # Título
    title_label = ttk.Label(
        about_window, 
        text="Editor de Banco de Dados JSON",
        font=("", 16, "bold")
    )
    title_label.pack(pady=(20, 10))
    
    # Versão
    version_label = ttk.Label(about_window, text="Versão 1.0.0")
    version_label.pack(pady=5)
    
    # Descrição
    desc_text = (
        "Um sistema para gerenciar arquivos JSON através de uma interface gráfica "
        "amigável, com validação de esquema e recursos avançados de edição."
    )
    
    desc_label = ttk.Label(about_window, text=desc_text, wraplength=350, justify="center")
    desc_label.pack(pady=10, padx=20)
    
    # Créditos
    credits_label = ttk.Label(
        about_window, 
        text="© 2025 JSON Database Editor",
        foreground="gray"
    )
    credits_label.pack(pady=10)
    
    # Botão de fechar
    close_button = ttk.Button(about_window, text="Fechar", command=about_window.destroy)
    close_button.pack(pady=20)
    
    # Centralizar
    about_window.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - about_window.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - about_window.winfo_height()) // 2
    about_window.geometry(f"+{x}+{y}")

def show_help(root):
    """Mostra a ajuda."""
    help_window = tk.Toplevel(root)
    help_window.title("Ajuda")
    help_window.geometry("600x500")
    
    # Tornar modal
    help_window.transient(root)
    help_window.grab_set()
    
    # Frame principal
    main_frame = ttk.Frame(help_window, padding=10)
    main_frame.pack(fill="both", expand=True)
    
    # Título
    title_label = ttk.Label(
        main_frame, 
        text="Ajuda do Editor de Banco de Dados JSON",
        font=("", 14, "bold")
    )
    title_label.pack(pady=(0, 10))
    
    # Conteúdo em um widget de texto com scroll
    help_text = tk.Text(main_frame, wrap="word", height=20)
    help_text.pack(fill="both", expand=True)
    
    # Barra de rolagem
    scrollbar = ttk.Scrollbar(help_text, command=help_text.yview)
    scrollbar.pack(side="right", fill="y")
    help_text.configure(yscrollcommand=scrollbar.set)
    
    # Conteúdo da ajuda
    help_content = """
# Como Usar o Editor de Banco de Dados JSON

## Conceitos Básicos

Este aplicativo permite editar arquivos JSON estruturados, seguindo um modelo definido em um arquivo separado.

### Arquivo de Modelo

O arquivo de modelo contém um objeto JSON com uma propriedade __meta__ que define a estrutura esperada dos dados:

```json
{
  "__meta__": {
    "name": { "type": "str", "required": true },
    "email": { "type": "str", "required": false },
    "age": { "type": "int", "required": false },
    "active": { "type": "bool", "required": true },
    "tags": { "type": "list[str]", "required": false }
  }
}
```

### Arquivo de Dados

O arquivo de dados contém uma lista de objetos JSON que seguem a estrutura definida no modelo:

```json
[
  {
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "age": 30,
    "active": true,
    "tags": ["cliente", "premium"]
  },
  {
    "name": "Maria Oliveira",
    "email": "maria@exemplo.com",
    "active": true
  }
]
```

## Operações Básicas

1. **Carregar Modelo**: Use o menu Arquivo > Carregar Modelo ou arraste um arquivo de modelo para a janela.
2. **Carregar Dados**: Use o menu Arquivo > Carregar Dados ou arraste um arquivo de dados para a janela.
3. **Adicionar Entrada**: Clique no botão "Adicionar" ou use o menu Editar > Adicionar Entrada.
4. **Editar Entrada**: Selecione uma entrada e clique em "Editar" ou dê um duplo clique na entrada.
5. **Excluir Entrada**: Selecione uma entrada e clique em "Excluir" ou pressione a tecla Delete.
6. **Salvar Dados**: Use o menu Arquivo > Salvar ou pressione Ctrl+S.

## Atalhos de Teclado

- Ctrl+O: Carregar modelo
- Ctrl+D: Carregar dados
- Ctrl+S: Salvar dados
- Ctrl+N: Adicionar entrada
- Delete: Excluir entrada selecionada
- Ctrl+Z: Desfazer
- Ctrl+Y: Refazer
- Ctrl+F: Pesquisar
- F3: Próximo resultado de pesquisa
- Shift+F3: Resultado anterior de pesquisa

## Recursos Adicionais

- **Validação**: Os dados são validados automaticamente contra o modelo.
- **Tema**: Alterne entre os temas claro e escuro no menu Visualizar.
- **Exportação/Importação**: Exporte ou importe dados em formato CSV.
- **Configurações**: Personalize o comportamento do aplicativo no menu Configurações.

## Resolução de Problemas

Se encontrar algum problema:
1. Verifique se o arquivo de modelo está corretamente formatado.
2. Verifique se o arquivo de dados segue a estrutura definida no modelo.
3. Consulte o console para mensagens de erro detalhadas.
"""
    
    help_text.insert("1.0", help_content)
    help_text.configure(state="disabled")  # Tornar somente leitura
    
    # Botão de fechar
    close_button = ttk.Button(main_frame, text="Fechar", command=help_window.destroy)
    close_button.pack(pady=10)
    
    # Centralizar
    help_window.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - help_window.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - help_window.winfo_height()) // 2
    help_window.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    main()