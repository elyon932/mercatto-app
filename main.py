import threading
import mysql.connector
from datetime import datetime
from functools import partial
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.list import TwoLineAvatarListItem
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import OneLineAvatarIconListItem
from mysql.connector import Error
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.card import MDCard
from kivy.uix.label import Label

host = "132.255.212.43"
port = "3306"

internet = False


def conectar_data_contas():
    db = mysql.connector.connect(
        host=host,
        port=port,
        user="elyon",
        password="123654",
        database="contas"
    )
    return db

def conectar_data_email(email):
    db = mysql.connector.connect(
        host=host,
        port=port,
        user="elyon",
        password="123654",
        database=email
    )
    return db

def somente_db():
    db = mysql.connector.connect(
        host=host,
        port=port,
        user="elyon",
        password="123654",
    )
    return db

def error_produto():
    error_dialog = MDDialog(
        title="Erro",
        text="Nenhum produto adicionado",
        auto_dismiss=False,
        buttons=[
            MDFlatButton(
                text="Fechar", on_release=lambda *args: error_dialog.dismiss()
            )
        ],
    )
    error_dialog.open()


class MyLineListItem(MDCard):
    def __init__(self, text1, text2, text3, text4, text5, text6, text7, email, id_venda, **kwargs):
        super().__init__(**kwargs)
        self.error_dialog = None
        self.orientation = "vertical"
        self.padding = 7  # Adiciona espaçamento interno dentro do cartão
        self.size_hint_y = None
        self.height = "180dp"
        self.elevation = 2  # Dá um efeito de sombra
        self.radius = [10]  # Arredonda os cantos

        self.id_venda = id_venda
        self.email = email

        container = MDRelativeLayout()

        # Layout principal com textos
        layout = MDBoxLayout(orientation="vertical", spacing=10)
        layout.add_widget(Label(text=text1, font_size=dp(22), bold=True))
        layout.add_widget(Label(text=text2, font_size=dp(20)))
        layout.add_widget(Label(text=text3, font_size=dp(20)))
        layout.add_widget(Label(text=text4, font_size=dp(20)))
        layout.add_widget(Label(text=text5, font_size=dp(20)))
        layout.add_widget(Label(text=text6, font_size=dp(20)))
        layout.add_widget(Label(text=text7, font_size=dp(20)))

        # Ícone de lixeira no canto superior direito
        trash_icon = MDIconButton(
            icon="trash-can",
            pos_hint={"right": 1, "top": 1},
            on_release=self.on_trash_click
        )

        container.add_widget(layout)
        container.add_widget(trash_icon)
        self.add_widget(container)

    def on_trash_click(self, instance):
        self.error_dialog = MDDialog(
            title="Aviso",
            text="Tem certeza que deseja deletar essa venda?",
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="Fechar", on_release=lambda *args: self.error_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Continuar", on_release=lambda *args: self.deletar_vendas_sql()
                )
            ],
        )
        self.error_dialog.open()

    def deletar_vendas_sql(self):
        try:
            mydb = conectar_data_email(self.email)
            mycursor = mydb.cursor()

            query = "DELETE FROM vendas WHERE id = %s"

            mycursor.execute(query, (self.id_venda,))

            mydb.commit()
            mycursor.close()
            mydb.close()

            app = MDApp.get_running_app()

            tela5 = app.root.get_screen('five')
            tela5.atualizar_vendas()

            self.error_dialog.dismiss()

        except Error as e:
            self.error_dialog.dismiss()
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()


class MyApp(MDApp):
    def build(self):
        screen = Builder.load_file("interface_main.kv")
        self.theme_cls.theme_style = "Dark"
        return screen  # Retornamos a tela, mas ainda não temos `self.root`

    def logar(self):
        thread = threading.Thread(target=self.executar_sql)
        thread.start()

        self.loading_dialog = MDDialog(
            title="Carregando",
            text="Por favor, aguarde...",
            auto_dismiss=False
        )
        self.loading_dialog.open()

    def executar_sql(self):
        try:
            self.email = self.root.get_screen('first').ids.user.text
            self.password = self.root.get_screen('first').ids.password.text

            mydb = conectar_data_contas()

            query = "SELECT * FROM contas WHERE usuario=%s AND senha=%s"

            usuario = self.email
            senha = self.password

            cursor = mydb.cursor()
            cursor.execute(query, (usuario, senha))
            result = cursor.fetchone()

            cursor.close()
            mydb.close()

            if result:
                db = somente_db()

                cursor = db.cursor()

                database_name = self.email
                cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(database_name))

                cursor.close()
                db.close()

                Clock.schedule_once(lambda dt: self.atualizar_interface(), 0)

            else:
                Clock.schedule_once(lambda dt: self.credenciais_invalidas(), 0)

        except Error as e:
            if e.errno == 2003:
                Clock.schedule_once(lambda dt: self.error_interface(), 0)

    def atualizar_interface(self):
        self.ativar_desativar_check()
        self.root.get_screen('second').produto_catalogo()
        self.root.get_screen('second').atualizar_valor_cobrar()
        self.root.get_screen('five').atualizar_vendas()

        self.loading_dialog.dismiss()

        self.root.get_screen('first').ids.welcome.text = 'Logado'
        Clock.schedule_once(lambda dt: (setattr(self.root.transition, 'direction', 'left'),
                                        setattr(self.root.current_screen.manager, 'current', 'second'), 1))

    def checar_net(self, *args):
        global internet
        if internet:
            try:
                # Conecta ao banco de dados
                db = somente_db()  # Substitua por sua função de conexão
                # Fecha a conexão imediatamente após abrir
                db.close()

            except mysql.connector.Error:
                # Agende a mudança de tela para a thread principal
                self.root.transition.direction = 'right'
                self.root.current = 'first'
                self.error_interface()
                self.clear()
                internet = False

        # Agenda a próxima execução da função após 3 segundos
        Clock.schedule_once(self.checar_net, 3)

    def ativar_desativar_check(self):
        global internet
        internet = not internet  # Alterna o valor de internet entre True e False
        self.checar_net()

    def credenciais_invalidas(self):
        self.loading_dialog.dismiss()
        self.root.get_screen('first').ids.welcome.text = 'Credenciais inválidas'

    def error_interface(self):
        self.loading_dialog.dismiss()
        error_dialog = MDDialog(
            title="Erro",
            text="Não foi possível se conectar ao servidor",
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                )
            ],
        )
        error_dialog.open()

    def clear(self):
        self.root.get_screen('first').ids.welcome.text = 'Bem-vindo'
        self.root.get_screen('first').ids.user.text = ''
        self.root.get_screen('first').ids.password.text = ''

    def ativar_desativar_senha_login(self, field, touch):
        """Função para alternar entre mostrar/ocultar a senha ao clicar no ícone."""
        # Calcula a largura aproximada do ícone (ajuste conforme necessário)
        icon_width = dp(48)  # Largura padrão do ícone no KivyMD

        # Obtém as coordenadas do campo de texto
        field_x, field_y = field.to_window(*field.pos)  # Posição absoluta na tela
        field_width, field_height = field.size

        # Define a área do ícone à direita
        icon_area_x = field_x + field_width - icon_width
        icon_area_y = field_y
        icon_area_width = icon_width
        icon_area_height = field_height

        # Verifica se o clique ocorreu na área do ícone
        if (icon_area_x <= touch.x <= icon_area_x + icon_area_width and
                icon_area_y <= touch.y <= icon_area_y + icon_area_height):
            if field.password:  # Se a senha estiver oculta
                field.password = False  # Mostra a senha
                field.icon_right = "eye"  # Altera o ícone para olho fechado
            else:
                field.password = True  # Oculta a senha
                field.icon_right = "eye-off"  # Altera o ícone para olho aberto

    def pagamento_item_selecionado(self, text):
        self.root.get_screen('second').dialog.dismiss()
        cobrar = self.root.get_screen('second').ids.valor_cobrar.text
        cobrar_formatado = cobrar.strip("Cobrar:\nR$")

        self.dialog = MDDialog(
            title=text,
            type="custom",
            auto_dismiss=False,
            content_cls=MDBoxLayout(
                MDTextField(
                    id='valor_recebido',
                    hint_text="Valor recebido:",
                    text=cobrar_formatado,
                    multiline=False,
                    max_text_length=6,
                    input_filter='float',
                ),
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="60dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda *args: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="VOLTAR",
                    on_release=lambda *args: (self.dialog.dismiss(), self.root.get_screen('second').dialog.open()),
                ),
                MDFlatButton(
                    text="AVANÇAR",
                    on_release=lambda *args: (self.dialog.dismiss(), self.second_dialog()),
                )
            ],
        )
        self.dialog.open()

    def second_dialog(self, *args):
        valor_recebido = self.dialog.content_cls.ids.valor_recebido.text
        data = datetime.now()
        data_formatada = data.strftime('%d/%m/%Y %H:%M')

        self.dialog2 = MDDialog(
            title='Pagamento concluído',
            type="custom",
            auto_dismiss=False,
            content_cls=MDBoxLayout(
                TwoLineListItem(
                    id='lista_grana',
                    text=self.dialog.title,
                    secondary_text="R${:.2f}".format(float(valor_recebido)),
                ),
                TwoLineListItem(
                    id='lista_data',
                    text='Data da venda:',
                    secondary_text=data_formatada,
                ),
                MDTextField(
                    id='observacoes',
                    hint_text="Observação da venda:",
                    multiline=True,
                ),
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="210dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda *args: self.dialog2.dismiss()
                ),
                MDFlatButton(
                    text="VOLTAR",
                    on_release=lambda *args: (self.dialog2.dismiss(), self.dialog.open()),
                ),
                MDFlatButton(
                    text="FINALIZAR",
                    on_release=lambda *args:
                    (self.root.get_screen('five').finalizar_venda(self.dialog.title,
                                                                  self.dialog2.content_cls.ids.lista_grana.secondary_text,
                                                                  self.dialog2.content_cls.ids.lista_data.secondary_text,
                                                                  self.dialog2.content_cls.ids.observacoes.text,
                                                                  self.root.get_screen("second").number_dict,
                                                                  self.root.get_screen("second").valor_dict,
                    self.root.get_screen("second").ids.dc.text, self.root.get_screen("second").ids.ac.text),
                    self.dialog2.dismiss(), self.root.get_screen("second").cancelar_compra())

                ),
            ],
        )

        self.dialog2.open()


class Tela1(Screen):
    pass


class Tela2(Screen):
    def __init__(self, **kwargs):
        super(Tela2, self).__init__(**kwargs)
        self.number_dict = {}
        self.valor_dict = {}

    def produto_catalogo(self):
        try:
            self.manager.get_screen('second').ids.container_produto_catalogo.clear_widgets()

            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("""
                        CREATE TABLE IF NOT EXISTS produtos (
                            id INT(11) AUTO_INCREMENT PRIMARY KEY,
                            categoria VARCHAR(255) NOT NULL,
                            descricao VARCHAR(255) UNIQUE NOT NULL,
                            v_custo DECIMAL(10, 2) NOT NULL,
                            v_venda DECIMAL(10, 2) NOT NULL,
                            e_minimo INT(11) NOT NULL,
                            e_atual INT(11) NOT NULL,
                            c_barras VARCHAR(255) NOT NULL,
                            observacoes VARCHAR(255),
                            botao_check BOOLEAN
                        )
                        """)

            mydb.commit()

            sql = "SELECT id FROM produtos WHERE botao_check=1"

            mycursor.execute(sql)
            produtos = mycursor.fetchall()
            num_produtos = len(produtos)

            mycursor.execute("SELECT descricao FROM produtos")
            descricao = mycursor.fetchall()

            mycursor.execute("SELECT v_venda FROM produtos")
            venda = mycursor.fetchall()

            mydb.commit()
            mycursor.close()
            mydb.close()

            for i in range(num_produtos):
                produto_id = str(produtos[i][0])
                produto_descricao = str(descricao[i][0])
                produto_venda = "R${:.2f}".format(float(venda[i][0]))
                list_item = TwoLineListItem(text=produto_descricao, secondary_text=produto_venda, id=produto_id)
                list_item.bind(on_touch_down=partial(self.item_click, produto_id, produto_descricao, produto_venda))
                self.manager.get_screen('second').ids.container_produto_catalogo.add_widget(list_item)

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def item_click(self, produto_id, produto_descricao, produto_venda, instance, touch):
        if instance.collide_point(*touch.pos):
            container = self.manager.get_screen('second').ids.container_venda_catalogo

            if produto_id in self.number_dict:
                self.number_dict[produto_id] += 1
            else:
                self.number_dict[produto_id] = 1

            number = self.number_dict[produto_id]

            valor_produto = float(produto_venda.strip("R$"))
            valor_total = number * valor_produto
            self.valor_dict[produto_id] = valor_total

            self.manager.get_screen('five').item = self.number_dict

            for item in container.children:
                if item.id == produto_id:
                    if number > 9:
                        item.children[0].icon = "numeric-9-plus-box-multiple-outline"
                    else:
                        item.children[0].icon = "numeric-{}-box-multiple-outline".format(number)
                    new_item = TwoLineAvatarListItem(
                        IconLeftWidget(
                            icon=item.children[0].icon
                        ),
                        text=item.text,
                        secondary_text=item.secondary_text,
                        id=item.id
                    )
                    new_item.bind(on_touch_down=partial(self.item_click2, new_item))
                    container.remove_widget(item)
                    container.add_widget(new_item)
                    break
            else:
                list_item = TwoLineAvatarListItem(
                    IconLeftWidget(
                        icon="numeric-1-box-multiple-outline"
                    ),
                    text=produto_descricao,
                    secondary_text=produto_venda,
                    id=produto_id
                )
                list_item.bind(on_touch_down=partial(self.item_click2, list_item))
                container.add_widget(list_item)

            self.atualizar_valor_cobrar()

    def item_click2(self, item, instance, touch):
        if instance.collide_point(*touch.pos):
            self.item = item
            container = self.manager.get_screen('second').ids.container_venda_catalogo
            container.remove_widget(item)
            self.number_dict[item.id] = 0
            self.valor_dict[item.id] = 0

            self.atualizar_valor_cobrar()

    def cancelar_compra(self):
        container = self.manager.get_screen('second').ids.container_venda_catalogo
        container.clear_widgets()
        self.number_dict = {}
        self.valor_dict = {}
        self.manager.get_screen("second").ids.dc.text = "Descontos:\nR$0.00"
        self.manager.get_screen("second").ids.ac.text = "Acréscimos:\nR$0.00"

        self.atualizar_valor_cobrar()

    def atualizar_valor_cobrar(self):
        self.total = 0
        for value in self.valor_dict.values():
            self.total += value

        total_formatado = "{:.2f}".format(self.total)
        self.manager.get_screen('second').ids.valor_cobrar.text = f'Cobrar:\nR${total_formatado}'

    def verificar_total_cobrar(self):
        if self.total == 0:
            error_produto()

    def verificar_tirar_decrescentar(self):
        if self.total == 0:
            error_produto()
        else:
            dc = self.manager.get_screen("second").ids.dc
            if dc.text != "Descontos:\nR$0.00":
                partes = dc.text.split("R$")
                valor = partes[1].strip()
                dc.text = "Descontos:\nR$" + "{:.2f}".format(float(valor)-1)

                cobrar = self.manager.get_screen("second").ids.valor_cobrar
                partes2 = cobrar.text.split("R$")
                valor2 = partes2[1].strip()
                cobrar.text = "Cobrar:\nR$" + "{:.2f}".format(float(valor2)+1)

    def verificar_colocar_decrescentar(self):
        if self.total == 0:
            error_produto()
        else:
            dc = self.manager.get_screen("second").ids.dc
            partes = dc.text.split("R$")
            valor = partes[1].strip()
            dc.text = "Descontos:\nR$" + "{:.2f}".format((float(valor) if valor != "0.00" else 0) +1.00)

            cobrar = self.manager.get_screen("second").ids.valor_cobrar
            partes2 = cobrar.text.split("R$")
            valor2 = partes2[1].strip()
            cobrar.text = "Cobrar:\nR$" + "{:.2f}".format(float(valor2) - 1)

    def verificar_tirar_acrescentar(self):
        if self.total == 0:
            error_produto()
        else:
            ac = self.manager.get_screen("second").ids.ac
            if ac.text != "Acréscimos:\nR$0.00":
                partes = ac.text.split("R$")
                valor = partes[1].strip()
                ac.text = "Acréscimos:\nR$" + "{:.2f}".format(float(valor)-1)

                cobrar = self.manager.get_screen("second").ids.valor_cobrar
                partes2 = cobrar.text.split("R$")
                valor2 = partes2[1].strip()
                cobrar.text = "Cobrar:\nR$" + "{:.2f}".format(float(valor2)-1)

    def verificar_colocar_acrescentar(self):
        if self.total == 0:
            error_produto()
        else:
            ac = self.manager.get_screen("second").ids.ac
            partes = ac.text.split("R$")
            valor = partes[1].strip()
            ac.text = "Acréscimos:\nR$" + "{:.2f}".format((float(valor) if valor != "0.00" else 0) +1.00)

            cobrar = self.manager.get_screen("second").ids.valor_cobrar
            partes2 = cobrar.text.split("R$")
            valor2 = partes2[1].strip()
            cobrar.text = "Cobrar:\nR$" + "{:.2f}".format(float(valor2) + 1)

    def verificar_valor_cobrar(self):
        cobrar = self.manager.get_screen('second').ids.valor_cobrar.text
        cobrar_formatado = cobrar.strip("Cobrar:\n")
        if cobrar != "Cobrar:\nR$0.00":
            self.dialog = MDDialog(
                title=f'Escolha a forma de pagamento\n'
                      f'Restante: {cobrar_formatado}',
                type="confirmation",
                auto_dismiss=False,
                items=[
                    ItemConfirm(text="Dinheiro"),
                    ItemConfirm(text="Débito"),
                    ItemConfirm(text="Crédito"),
                    ItemConfirm(text="Boleto"),
                    ItemConfirm(text="Cheque"),
                ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda *args: self.dialog.dismiss()
                    ),
                ],
            )
            self.dialog.open()


class Tela3(Screen):
    pass


class Tela4(Screen):
    pass


class Tela5(Screen):
    def finalizar_venda(self, title, grana, data, text, number, valor, descontos, acrescimos):
        def is_valid_text(text):
            if bool(text.strip()): return bool(text.strip())
            else: return "Nenhuma descrição"

        email = self.manager.get_screen('first').ids.user.text
        mydb = conectar_data_email(email)

        query = "SELECT descricao FROM produtos WHERE id = %s"

        produtos_id = [int(chave) for chave in number.keys()]
        produtos = []

        cursor = mydb.cursor()

        for i in produtos_id:
            cursor.execute(query, (i,))
            resultado = cursor.fetchone()
            if resultado:
                produtos.append(resultado[0])

        cursor.close()
        mydb.close()

        valores = list(number.values())
        precos = list(valor.values())
        final = "Produtos: "

        for i in produtos:
            if len(produtos) == 1:
                final += i + " " + "(" + str((precos[produtos.index(i)]) / valores[produtos.index(i)]) + "x" + str(
                    valores[produtos.index(i)]) + ")" + " " + "R$" + str(
                    "{:.2f}".format(precos[produtos.index(i)]))
            else:
                if i == produtos[-1]:
                    final += i + " " + "(" + str((precos[produtos.index(i)]) / valores[produtos.index(i)]) + "x" + str(
                        valores[produtos.index(i)]) + ")" + " " + "R$" + str(
                        "{:.2f}".format(precos[produtos.index(i)])) + " "
                else:
                    final += i + " " + "(" + str((precos[produtos.index(i)]) / valores[produtos.index(i)]) + "x" + str(
                        valores[produtos.index(i)]) + ")" + " " + "R$" + str(
                        "{:.2f}".format(precos[produtos.index(i)])) + "," + " "

        partes = descontos.split("R$")
        valor = partes[1].strip()

        partes2 = acrescimos.split("R$")
        valor2 = partes2[1].strip()

        id_venda = self.adicionar_vendas_sql(title, grana, data, is_valid_text(text), final, descontos, acrescimos)
        print(id_venda)
        item = MyLineListItem(
            title, grana, data, final, "Descontos R$" + "{:.2f}".format(float(valor)),
            "Acréscimos R$" + "{:.2f}".format(float(valor2)),
            is_valid_text(text), email, id_venda
        )

        container = self.manager.get_screen("five").ids.container_vendas

        # Adiciona o item e inverte a lista manualmente
        widgets = container.children[:]  # Copia a lista de widgets
        widgets.insert(0, item)  # Adiciona o novo item no topo
        container.clear_widgets()  # Remove todos os widgets do container
        for w in widgets:
            container.add_widget(w)  # Reinsere os widgets na ordem desejada

        container.height = container.minimum_height  # Ajusta a altura dinamicamente
        container.canvas.ask_update()  # Força a atualização do layout

    def adicionar_vendas_sql(self, titulo, grana, data, texto, final, descontos, acrescimos):
        self.create_table()
        email = self.manager.get_screen('first').ids.user.text
        mydb = conectar_data_email(email)
        mycursor = mydb.cursor()

        # Inserir os valores na tabela
        sql = """
            INSERT INTO vendas (tipo, grana, data, descricao, detalhes, descontos, acrescimos) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (titulo, grana, data, texto, final, descontos, acrescimos)

        mycursor.execute(sql, valores)  # Executar a inserção
        mydb.commit()  # Confirmar a transação

        inserted_id = mycursor.lastrowid  # Obter o ID do registro inserido

        mycursor.close()
        mydb.close()

        return inserted_id

    def atualizar_vendas(self):
        self.create_table()
        email = self.manager.get_screen('first').ids.user.text
        mydb = conectar_data_email(email)
        cursor = mydb.cursor()

        query = "SELECT id, tipo, grana, data, descricao, detalhes, descontos, acrescimos FROM vendas ORDER BY id DESC"
        cursor.execute(query)
        vendas = cursor.fetchall()

        cursor.close()
        mydb.close()

        container = self.manager.get_screen("five").ids.container_vendas
        container.clear_widgets()

        # Criando a lista de widgets e adicionando no container invertendo a ordem
        widgets = []
        for venda in vendas:
            id_venda, titulo, grana, data, texto, final, descontos, acrescimos = venda
            item = MyLineListItem(
                titulo, grana, data, final, "Descontos R$" + "{:.2f}".format(float(descontos.split("R$")[1])),
                                            "Acréscimos R$" + "{:.2f}".format(float(acrescimos.split("R$")[1])),
                texto, email, id_venda
            )
            widgets.insert(0, item)  # Insere o mais recente no topo

        # Adiciona os itens de forma invertida para garantir o LIFO
        for w in widgets:
            container.add_widget(w)

        container.height = container.minimum_height  # Ajusta a altura dinamicamente
        container.canvas.ask_update()  # Força a atualização do layout

    def create_table(self):
        self.manager.get_screen('nine').ids.container.clear_widgets()

        email = self.manager.get_screen('first').ids.user.text

        mydb = conectar_data_email(email)  # Conectar ao banco de dados do usuário

        mycursor = mydb.cursor()

        # Criar a tabela se não existir
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INT(30) AUTO_INCREMENT PRIMARY KEY,
                tipo VARCHAR(30) NOT NULL,
                grana VARCHAR(30) NOT NULL,
                data VARCHAR(30) NOT NULL,
                descricao VARCHAR(255) NOT NULL,
                detalhes VARCHAR(255) NOT NULL,
                descontos VARCHAR(255) NOT NULL,
                acrescimos VARCHAR(255) NOT NULL
            )
        """)

        mydb.commit()
        mycursor.close()
        mydb.close()


class Tela6(Screen):
    pass


class Tela7(Screen):
    pass


class Tela8(Screen):
    def atualizar_widgets_categorias(self):
        self.manager.get_screen('ten').ids.categoria.text = ''


class Tela9(Screen):
    def atualizar_widgets_produtos(self):
        self.manager.get_screen('eleven').ids.label_categorias.text = 'Nenhum'
        self.manager.get_screen('eleven').ids.codigo.text = ''
        self.manager.get_screen('eleven').ids.descricao.text = ''
        self.manager.get_screen('eleven').ids.valor_custo.text = ''
        self.manager.get_screen('eleven').ids.valor_venda.text = ''
        self.manager.get_screen('eleven').ids.estoque_minimo.text = ''
        self.manager.get_screen('eleven').ids.estoque_atual.text = ''
        self.manager.get_screen('eleven').ids.codigo_de_barras.text = ''
        self.manager.get_screen('eleven').ids.observacoes.text = ''
        self.manager.get_screen('eleven').ids.check.active = False


class Tela10(Screen):
    def adicionar_categoria(self):
        thread = threading.Thread(target=self.execute_query)
        thread.start()

        self.loading_dialog = MDDialog(
            title="Carregando",
            text="Por favor, aguarde...",
            auto_dismiss=False
        )
        self.loading_dialog.open()

    def execute_query(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("CREATE TABLE IF NOT EXISTS categorias (categoria VARCHAR(100) NOT NULL UNIQUE CHECK (TRIM(categoria) <> ''))")
            mycursor.execute("SELECT categoria FROM categorias")

            categorias = mycursor.fetchall()
            num_categorias = len(categorias)

            try:
                if num_categorias < 5:
                    sql = "INSERT INTO categorias (categoria) VALUES (%s)"
                    val = [self.manager.get_screen('ten').ids.categoria.text]
                    mycursor.execute(sql, val)

                    mydb.commit()
                    mycursor.close()
                    mydb.close()

                    Clock.schedule_once(lambda dt: self.atualizar_categoria(), 0)

                    Clock.schedule_once(lambda dt: self.update_interface(), 0)

                else:
                    Clock.schedule_once(lambda dt: self.limite_atingido(), 0)

            except Error as e:
                if e.errno:
                    Clock.schedule_once(lambda dt, error=e: self.error_interface(error), 0)

        except Error as e:
            Clock.schedule_once(lambda dt, error=e: self.error_interface(error), 0)

    def limite_atingido(self):
        self.loading_dialog.dismiss()

        self.dialog_categorias = MDDialog(
            title="Erro",
            text="O número máximo de categorias foi atingido.",
            buttons=[MDFlatButton(text="OK", on_release=lambda *args: self.dialog_categorias.dismiss())]
        )
        self.dialog_categorias.open()

    def error_interface(self, error):
        self.loading_dialog.dismiss()
        error_dialog = MDDialog(
            title="Erro",
            text="Houve um erro ao adicionar a categoria: " + str(error),
            buttons=[
                MDFlatButton(
                    text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                )
            ],
        )
        error_dialog.open()

    def update_interface(self):
        self.loading_dialog.dismiss()

        setattr(self.manager.transition, 'direction', 'right')
        setattr(self.manager, 'current', 'eight')

    def atualizar_categoria(self):
        try:
            self.manager.get_screen('eight').ids.container_categoria.clear_widgets()

            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("CREATE TABLE IF NOT EXISTS categorias (categoria VARCHAR(100) NOT NULL UNIQUE CHECK (TRIM(categoria) <> ''))")

            mycursor.execute("SELECT categoria FROM categorias")

            categoria = mycursor.fetchall()
            num_categoria = len(categoria)

            mydb.commit()
            mycursor.close()
            mydb.close()

            for i in range(num_categoria):
                categoria_id = str(categoria[i][0])
                list_item = OneLineListItem(text=categoria_id, id=categoria_id)
                list_item.bind(on_touch_down=partial(self.item_click, categoria_id))
                self.manager.get_screen('eight').ids.container_categoria.add_widget(list_item)

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def item_click(self, categoria_id, instance, touch):
        if instance.collide_point(*touch.pos):
            try:
                self.manager.get_screen('thirteen').categoria_id = categoria_id

                email = self.manager.get_screen('first').ids.user.text

                mydb = conectar_data_email(email)

                mycursor = mydb.cursor()

                query = "SELECT * FROM categorias WHERE categoria=%s"

                mycursor.execute(query, (categoria_id,))
                result = mycursor.fetchone()

                mydb.commit()
                mycursor.close()
                mydb.close()

                if result:
                    self.manager.get_screen('thirteen').ids.categoria2.text = str(result[0])

                self.manager.transition.direction = 'left'
                self.manager.current = 'thirteen'

            except Error as e:
                error_dialog = MDDialog(
                    title="Erro",
                    text=str(e),
                    buttons=[
                        MDFlatButton(
                            text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                        )
                    ],
                )
                error_dialog.open()


class Tela11(Screen):
    def acionar_menu(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("CREATE TABLE IF NOT EXISTS categorias (categoria VARCHAR(100) NOT NULL UNIQUE CHECK (TRIM(categoria) <> ''))")

            mycursor.execute("SELECT categoria FROM categorias")

            categorias = mycursor.fetchall()
            num_categorias = len(categorias)

            menu_items = [
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i[0]}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i[0]}": self.set_item(x),
                 } for i in categorias
            ]
            self.menu = MDDropdownMenu(
                caller=self.manager.get_screen('eleven').ids.menu_categorias,
                items=menu_items,
                width_mult=num_categorias,
            )

            mycursor.close()
            mydb.close()

            self.menu.open()

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def set_item(self, text__item):
        self.manager.get_screen('eleven').ids.label_categorias.text = text__item
        self.menu.dismiss()

    def adicionar_produto(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            id = self.manager.get_screen('eleven').ids.codigo.text or None
            categoria = self.manager.get_screen('eleven').ids.label_categorias.text
            descricao = self.manager.get_screen('eleven').ids.descricao.text
            v_custo = self.manager.get_screen('eleven').ids.valor_custo.text
            v_venda = self.manager.get_screen('eleven').ids.valor_venda.text
            e_minimo = self.manager.get_screen('eleven').ids.estoque_minimo.text
            e_atual = self.manager.get_screen('eleven').ids.estoque_atual.text
            c_barras = self.manager.get_screen('eleven').ids.codigo_de_barras.text
            observacoes = self.manager.get_screen('eleven').ids.observacoes.text
            botao_check = self.manager.get_screen('eleven').ids.check.active

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INT(11) AUTO_INCREMENT PRIMARY KEY,
                categoria VARCHAR(255) NOT NULL,
                descricao VARCHAR(255) UNIQUE NOT NULL,
                v_custo DECIMAL(10, 2) NOT NULL,
                v_venda DECIMAL(10, 2) NOT NULL,
                e_minimo INT(11) NOT NULL,
                e_atual INT(11) NOT NULL,
                c_barras VARCHAR(255) NOT NULL,
                observacoes VARCHAR(255),
                botao_check BOOLEAN
            )
            """)

            mydb.commit()

            sql = "INSERT INTO produtos (id, categoria, descricao, v_custo, v_venda, e_minimo, e_atual, c_barras, observacoes, botao_check) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = [id, categoria, descricao, v_custo, v_venda, e_minimo, e_atual, c_barras, observacoes, botao_check]

            if categoria == 'Nenhum':
                error_dialog = MDDialog(
                    title="Erro",
                    text='Selecione uma categoria',
                    buttons=[
                        MDFlatButton(
                            text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                        )
                    ],
                )
                error_dialog.open()
            else:
                try:
                    mycursor.execute(sql, val)
                    setattr(self.manager.transition, 'direction', 'right')
                    setattr(self.manager, 'current', 'nine')
                    mydb.commit()

                except Error as e:
                    if e.errno:
                        error_dialog = MDDialog(
                            title="Erro",
                            text="Houve um erro ao adicionar o produto: " + str(e),
                            buttons=[
                                MDFlatButton(
                                    text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                                )
                            ],
                        )
                        error_dialog.open()

            mydb.commit()
            mycursor.close()
            mydb.close()

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def adicionar_lista(self):
        try:
            self.manager.get_screen('nine').ids.container.clear_widgets()

            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INT(11) AUTO_INCREMENT PRIMARY KEY,
                categoria VARCHAR(255) NOT NULL,
                descricao VARCHAR(255) UNIQUE NOT NULL,
                v_custo DECIMAL(10, 2) NOT NULL,
                v_venda DECIMAL(10, 2) NOT NULL,
                e_minimo INT(11) NOT NULL,
                e_atual INT(11) NOT NULL,
                c_barras VARCHAR(255) NOT NULL,
                observacoes VARCHAR(255),
                botao_check BOOLEAN
            )
            """)

            mydb.commit()

            mycursor.execute("SELECT id FROM produtos")

            produtos = mycursor.fetchall()
            num_produtos = len(produtos)

            mycursor.execute("SELECT descricao FROM produtos")
            descricao = mycursor.fetchall()

            mycursor.execute("SELECT v_venda FROM produtos")
            venda = mycursor.fetchall()

            mydb.commit()
            mycursor.close()
            mydb.close()

            for i in range(num_produtos):
                produto_id = str(produtos[i][0])
                produto_descricao = str(descricao[i][0])
                produto_venda = "R${:.2f}".format(float(venda[i][0]))
                list_item = TwoLineListItem(text=produto_descricao, secondary_text=produto_venda, id=produto_id)
                list_item.bind(on_touch_down=partial(self.item_click, produto_id))
                self.manager.get_screen('nine').ids.container.add_widget(list_item)

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def item_click(self, produto_id, instance, touch):
        if instance.collide_point(*touch.pos):
            try:
                self.manager.get_screen('twelve').produto_id = produto_id

                email = self.manager.get_screen('first').ids.user.text

                mydb = conectar_data_email(email)

                mycursor = mydb.cursor()

                query = "SELECT * FROM produtos WHERE id=%s"

                mycursor.execute(query, (produto_id,))
                result = mycursor.fetchone()

                mydb.commit()
                mycursor.close()
                mydb.close()

                if result:
                    self.manager.get_screen('twelve').ids.codigo2.text = str(result[0])
                    self.manager.get_screen('twelve').ids.label_categorias2.text = str(result[1])
                    self.manager.get_screen('twelve').ids.descricao2.text = str(result[2])
                    self.manager.get_screen('twelve').ids.valor_custo2.text = str(result[3])
                    self.manager.get_screen('twelve').ids.valor_venda2.text = str(result[4])
                    self.manager.get_screen('twelve').ids.estoque_minimo2.text = str(result[5])
                    self.manager.get_screen('twelve').ids.estoque_atual2.text = str(result[6])
                    self.manager.get_screen('twelve').ids.codigo_de_barras2.text = str(result[7])
                    self.manager.get_screen('twelve').ids.observacoes2.text = str(result[8])
                    self.manager.get_screen('twelve').ids.check2.active = result[9]

                self.manager.transition.direction = 'left'
                self.manager.current = 'twelve'

            except Error as e:
                error_dialog = MDDialog(
                    title="Erro",
                    text=str(e),
                    buttons=[
                        MDFlatButton(
                            text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                        )
                    ],
                )
                error_dialog.open()


class Tela12(Screen):
    produto_id = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.produto_id = self.manager.get_screen('twelve').produto_id

    def acionar_menu2(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            mycursor.execute("CREATE TABLE IF NOT EXISTS categorias (categoria VARCHAR(100) NOT NULL UNIQUE CHECK (TRIM(categoria) <> ''))")

            mycursor.execute("SELECT categoria FROM categorias")

            categorias = mycursor.fetchall()
            num_categorias = len(categorias)

            menu_items = [
                {
                    "viewclass": "OneLineListItem",
                    "text": f"{i[0]}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i[0]}": self.set_item(x),
                 } for i in categorias
            ]
            self.menu = MDDropdownMenu(
                caller=self.manager.get_screen('twelve').ids.menu_categorias2,
                items=menu_items,
                width_mult=num_categorias,
            )

            mycursor.close()
            mydb.close()

            self.menu.open()

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def set_item(self, text__item):
        self.manager.get_screen('twelve').ids.label_categorias2.text = text__item
        self.menu.dismiss()

    def deletar_produto(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            query = "DELETE FROM produtos WHERE id = %s"

            mycursor.execute(query, (self.produto_id,))

            mydb.commit()
            mycursor.close()
            mydb.close()

            self.manager.get_screen('eleven').adicionar_lista()
            self.manager.current = 'nine'
            self.manager.transition.direction = 'right'

            self.manager.get_screen('second').produto_catalogo()

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def substituir_produto(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            sql = "UPDATE produtos SET id=%s, categoria=%s, descricao=%s, v_custo=%s, v_venda=%s, e_minimo=%s, e_atual=%s, c_barras=%s, observacoes=%s, botao_check=%s WHERE id=%s"

            id = self.manager.get_screen('twelve').ids.codigo2.text
            categoria = self.manager.get_screen('twelve').ids.label_categorias2.text
            descricao = self.manager.get_screen('twelve').ids.descricao2.text
            v_custo = self.manager.get_screen('twelve').ids.valor_custo2.text
            v_venda = self.manager.get_screen('twelve').ids.valor_venda2.text
            e_minimo = self.manager.get_screen('twelve').ids.estoque_minimo2.text
            e_atual = self.manager.get_screen('twelve').ids.estoque_atual2.text
            c_barras = self.manager.get_screen('twelve').ids.codigo_de_barras2.text
            observacoes = self.manager.get_screen('twelve').ids.observacoes2.text
            check = self.manager.get_screen('twelve').ids.check2.active

            mycursor.execute(sql, (id, categoria, descricao, v_custo, v_venda, e_minimo, e_atual, c_barras, observacoes, check, self.produto_id))

            mydb.commit()
            mycursor.close()
            mydb.close()

            self.manager.get_screen('eleven').adicionar_lista()
            self.manager.current = 'nine'
            self.manager.transition.direction = 'right'

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()


class Tela13(Screen):
    categoria_id = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.categoria_id = self.manager.get_screen('thirteen').categoria_id

    def deletar_categoria(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            query = "SELECT * FROM produtos WHERE categoria = %s"

            mycursor.execute(query, (self.categoria_id,))

            resultado = mycursor.fetchall()
            existe_valor_banho = bool(resultado)

            if existe_valor_banho:
                error5_dialog = MDDialog(
                    title="Erro: Não foi possível efetuar a ação",
                    text="Existem produtos que usam essa categoria.",
                    buttons=[
                        MDFlatButton(
                            text="Fechar", on_release=lambda *args: error5_dialog.dismiss()
                        )
                    ],
                )
                error5_dialog.open()

            else:
                query = "DELETE FROM categorias WHERE categoria = %s"

                mycursor.execute(query, (self.categoria_id,))

                mydb.commit()
                mycursor.close()
                mydb.close()

                self.manager.get_screen('ten').atualizar_categoria()
                self.manager.current = 'eight'
                self.manager.transition.direction = 'right'

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text=str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()

    def substituir_categoria(self):
        try:
            email = self.manager.get_screen('first').ids.user.text

            mydb = conectar_data_email(email)

            mycursor = mydb.cursor()

            sql = "UPDATE categorias SET categoria=%s WHERE categoria=%s"

            nova_categoria = self.manager.get_screen('thirteen').ids.categoria2.text

            mycursor.execute(sql, (nova_categoria, self.categoria_id))

            mydb.commit()
            mycursor.close()
            mydb.close()

            self.manager.get_screen('ten').atualizar_categoria()
            self.manager.current = 'eight'
            self.manager.transition.direction = 'right'

        except Error as e:
            error_dialog = MDDialog(
                title="Erro",
                text="Não foi possível atualizar a categoria: " + str(e),
                buttons=[
                    MDFlatButton(
                        text="Fechar", on_release=lambda *args: error_dialog.dismiss()
                    )
                ],
            )
            error_dialog.open()


class Tela14(Screen):
    pass


class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

        app = MDApp.get_running_app()
        app.pagamento_item_selecionado(self.text)

    def on_touch_down(self, touch):
        if self.ids.check.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            app.pagamento_item_selecionado(self.text)

        return super().on_touch_down(touch)


class Gerenciador(ScreenManager):
    pass


sm = Gerenciador()
sm.add_widget(Tela1(name='first'))
sm.add_widget(Tela2(name='second'))
sm.add_widget(Tela3(name='third'))
sm.add_widget(Tela4(name='four'))
sm.add_widget(Tela5(name='five'))
sm.add_widget(Tela6(name='six'))
sm.add_widget(Tela7(name='seven'))
sm.add_widget(Tela8(name='eight'))
sm.add_widget(Tela9(name='nine'))
sm.add_widget(Tela10(name='ten'))
sm.add_widget(Tela11(name='eleven'))
sm.add_widget(Tela12(name='twelve'))
sm.add_widget(Tela13(name='thirteen'))
sm.add_widget(Tela14(name='fourteen'))

if __name__ == '__main__':
    MyApp().run()
