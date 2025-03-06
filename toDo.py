from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.theming import ThemeManager
from kivy.metrics import dp
from datetime import datetime

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15

    MDLabel:
        text: "✔ Lista de Tarefas"
        font_style: "H5"
        halign: "center"
        theme_text_color: "Primary"

    MDBoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [20, 15]
        size_hint_y: None
        height: "140dp"
        md_bg_color: app.theme_cls.bg_normal

        MDTextField:
            id: entrada_tarefa
            hint_text: "Digite uma tarefa"
            mode: "rectangle"

        MDBoxLayout:
            spacing: 10
            size_hint_y: None
            height: "50dp"

            MDRaisedButton:
                text: "Escolher Data"
                size_hint_x: 0.5
                md_bg_color: app.theme_cls.primary_color
                on_release: app.mostrar_seletor_data()

            MDRaisedButton:
                text: "Adicionar"
                size_hint_x: 0.5
                md_bg_color: app.theme_cls.primary_color
                on_release: app.adicionar_tarefa()

    ScrollView:
        MDList:
            id: lista_tarefas
'''

class ItemTarefa(OneLineAvatarIconListItem):
    def __init__(self, texto, data, **kwargs):
        super().__init__(text=f"{texto} ({data})", **kwargs)
        self.texto_tarefa = texto
        self.data_tarefa = data
        self.add_widget(CheckboxTarefa())
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
        return Builder.load_string(KV)

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
            tarefa = ItemTarefa(texto=texto_tarefa, data=data)
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

        self.dialogo.dismiss()

if __name__ == "__main__":
    ToDoApp().run()
