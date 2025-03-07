import sqlite3
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.theming import ThemeManager
from kivy.metrics import dp
from datetime import datetime

class ItemTarefa(OneLineAvatarIconListItem):
    def __init__(self, texto, data, tarefa_id, **kwargs):
        super().__init__(text=f"{texto} ({data})", **kwargs)
        self.texto_tarefa = texto
        self.data_tarefa = data
        self.tarefa_id = tarefa_id
        self.orientation = "horizontal"

        self.checkbox = CheckboxTarefa()
        self.add_widget(self.checkbox)

        self.bind(on_release=self.editar_tarefa)

    def editar_tarefa(self, *args):
        app = MDApp.get_running_app()
        app.mostrar_dialogo_edicao(self)

    def atualizar_texto(self):
        self.text = f"{self.texto_tarefa} ({self.data_tarefa})"

class CheckboxTarefa(IRightBodyTouch, MDCheckbox):
    pass

class ToDoApp(MDApp):
    data_selecionada = None
    tarefa_em_edicao = None
    theme_cls = ThemeManager()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.criar_banco_de_dados()
        return Builder.load_file("toDo.kv")

    def on_start(self):
        self.carregar_tarefas()

    def criar_banco_de_dados(self):
        self.conn = sqlite3.connect("tarefas.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    def carregar_tarefas(self):
        self.cursor.execute("SELECT * FROM tarefas")
        tarefas = self.cursor.fetchall()

        for tarefa in tarefas:
            tarefa_item = ItemTarefa(
                texto=tarefa[1], 
                data=tarefa[2], 
                tarefa_id=tarefa[0]
            )
            self.root.ids.lista_tarefas.add_widget(tarefa_item)

    def mostrar_seletor_data(self):
        seletor_data = MDDatePicker()
        seletor_data.bind(on_save=self.salvar_data)
        seletor_data.open()

    def salvar_data(self, instance, valor, intervalo_datas):
        self.data_selecionada = valor.strftime("%d/%m/%Y")

    def adicionar_tarefa(self):
        texto_tarefa = self.root.ids.entrada_tarefa.text.strip()
        if texto_tarefa:
            data = self.data_selecionada if self.data_selecionada else "Sem data"
            self.cursor.execute("INSERT INTO tarefas (texto, data) VALUES (?, ?)", (texto_tarefa, data))
            self.conn.commit()
            tarefa_id = self.cursor.lastrowid
            tarefa = ItemTarefa(
                texto=texto_tarefa, 
                data=data, 
                tarefa_id=tarefa_id
            )
            self.root.ids.lista_tarefas.add_widget(tarefa)
            self.root.ids.entrada_tarefa.text = ""
            self.data_selecionada = None  

    def mostrar_dialogo_edicao(self, item_tarefa):
        self.tarefa_em_edicao = item_tarefa

        conteudo = MDBoxLayout(orientation="vertical", spacing=20, padding=[10, 10, 10, 10], size_hint_y=None)
        conteudo.height = dp(150)

        self.campo_texto_edicao = MDTextField(text=item_tarefa.texto_tarefa, hint_text="Editar tarefa", size_hint_y=None, height=dp(50))
        self.botao_data_edicao = MDRaisedButton(text=f"Data: {item_tarefa.data_tarefa}", on_release=self.mostrar_seletor_data_edicao)

        conteudo.add_widget(self.campo_texto_edicao)
        conteudo.add_widget(self.botao_data_edicao)

        self.dialogo = MDDialog(
            title="Editar Tarefa",
            type="custom",
            content_cls=conteudo,
            buttons=[
                MDRaisedButton(text="Salvar", on_release=lambda x: self.salvar_edicao(item_tarefa)),
                MDRaisedButton(text="Cancelar", on_release=lambda x: self.dialogo.dismiss())
            ],
            size_hint=(0.8, None),
            height=dp(250)
        )
        self.dialogo.open()

    def mostrar_seletor_data_edicao(self, instance):
        seletor_data = MDDatePicker()
        seletor_data.bind(on_save=self.salvar_data_edicao)
        seletor_data.open()

    def salvar_data_edicao(self, instance, valor, intervalo_datas):
        self.botao_data_edicao.text = f"Data: {valor.strftime('%d/%m/%Y')}"

    def salvar_edicao(self, item_tarefa):
        novo_texto = self.campo_texto_edicao.text.strip()
        nova_data = self.botao_data_edicao.text.replace("Data: ", "")

        if novo_texto:
            item_tarefa.texto_tarefa = novo_texto
            item_tarefa.data_tarefa = nova_data
            item_tarefa.atualizar_texto()

            self.cursor.execute("UPDATE tarefas SET texto = ?, data = ? WHERE id = ?", (novo_texto, nova_data, item_tarefa.tarefa_id))
            self.conn.commit()

        self.dialogo.dismiss()

    def on_stop(self):
        self.conn.close()

if __name__ == "__main__":
    ToDoApp().run()
