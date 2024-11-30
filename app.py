# -*- coding: utf-8 -*-
from PySimpleGUI import PySimpleGUI as sg
import os
import json
import os

# Força o uso de UTF-8 no ambiente de execução
os.environ['PYTHONUTF8'] = '1'

def popup_text(text, title='Aviso'):
    """
    Exibe uma janela popup com texto selecionável.

    Args:
        title (str): Título da janela.
        text (str): Texto a ser exibido no popup.
    """
    layout = [
        [sg.Multiline(text, size=(500, 300), disabled=True, autoscroll=True, key='-TEXT-')],
        [sg.Button('Fechar', size=(100, 100))]
    ]

    window = sg.Window(title, layout, modal=True, finalize=True, size=(700, 450))
    
    while True:
        event, _ = window.read()
        if event == sg.WIN_CLOSED or event == 'Fechar':
            break

    window.close()

sg.theme('Reddit')
# Layout
layout = [
    [sg.Button('Baixar Python e Chrome 131')],
    [sg.Button('Baixar depêndencias do Python')],
    [sg.Button('Mostrar links das planilhas')],
    [sg.Button('Atualizar planilhas')],
    [sg.Button('Zerar planilhas e Baixar do zero (SEM ATUALIZAÇÕES)')],
    [sg.Button('Sair')]
]

# Janela
window = sg.Window('', layout=layout, icon='', font=("Arial", 12))

# Eventos
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Sair':
        break
    
    if event == 'Baixar Python e Chrome 131':
        os.system('python-3.13.0-amd64.exe')
        os.system('Chrome_131_WINDOWS.exe')
        popup_text('Python e Chrome 131 baixados!!!')
    
    if event == 'Baixar depêndencias do Python':
        os.system('pip install -r requirements.txt')
        popup_text('Depêndencias do Python baixadas!!!')

    if event == 'Mostrar links das planilhas':
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
            tables = ''
            for key, value in settings['excel_files'].items():
                tables += f'{key}: {value}\n\n'
            popup_text(tables, 'Links das planilhas:')

    if event == 'Atualizar planilhas':
        popup_text('Processo demorado!\nO script vai mostrar uma tela quando tiver acabado de atualizar...', 'Iniciando a atualização:')
        os.system('python main.py')
        popup_text('Tabelas atualizadas!!!')

    if event == 'Zerar planilhas e Baixar do zero (SEM ATUALIZAÇÕES)':
        # Exibe a mensagem de confirmação
        confirmation = sg.popup_yes_no(
            "ATENÇÃO: Essa ação irá excluir todas as tabelas e baixar novamente do zero.\n"
            "Esse processo pode demorar dias e não poderá ser desfeito.\n\n"
            "Deseja continuar?",
            title="Confirmação Necessária"
        )

        if confirmation == True:
            popup_text('Iniciando o processo...')
            popup_text('Processo demorado!\nO script vai mostrar uma tela quando tiver acabado de atualizar...', 'Iniciando o download do zero...')
            os.system('python modules/erase.py')
            with open('settings.json', 'w', encoding='utf-8') as file:
                settings = json.load(file)
                settings['last_date_updated'] = '01/01/2020'
                json.dump(settings, file, indent=4, ensure_ascii=False)
            os.system('python main.py')
            popup_text('Tabelas zeradas e baixadas do zero!!!')
        else:
            popup_text('Ação cancelada pelo usuário.')