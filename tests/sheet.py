# -*- coding: utf-8 -*- 

from typing import Union
import os
import gspread
from gspread.worksheet import Worksheet
from gspread.spreadsheet import Spreadsheet
from google.oauth2.service_account import Credentials
import json
from time import sleep
from faker import Faker
import pandas as pd

SCOPES = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

def __get_id_by_name(gc, name:str):
    files = gc.list_spreadsheet_files()
    sheet_file_id = None
    for file in files:
        if file['name'] == name:
            sheet_file_id = file['id']
            break
    if sheet_file_id:
        return sheet_file_id
    else:
        return None

def get_sheet_file(gc, file_path):
    file = open('settings.json', 'r+', encoding='utf-8')
    settings = json.load(file)
    filename = f'{os.path.basename(file_path).replace(".xlsx","")}'
    try:
        # id_sheet = __get_id_by_name(gc, settings[filename])
        # spreadsheet = gc.open_by_key(id_sheet)
        spreadsheet = gc.open_by_key(settings[filename])
    except KeyError:
        spreadsheet = gc.create(filename)
        settings[filename] = spreadsheet.id
        file.truncate(0)
        file.seek(0)
        json.dump(settings, file, indent=4, ensure_ascii=False)
    return spreadsheet
    
def login():
    credentials = Credentials.from_service_account_file('', scopes=SCOPES)
    gc = gspread.auth.authorize(credentials)
    return gc

def remove_and_update_sheet(sheet_files:list[str]) -> None:
    
    def convert_excel_to_csv(file_path):
        def create_folder_csv():
            folder_path = f'planilhas/{os.path.basename(file_path).replace(".xlsx", "")}/'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return folder_path

        data_excel = pd.ExcelFile(file_path)

        for sheet_name in data_excel.sheet_names:
            data_sheet = pd.read_excel(data_excel, sheet_name=sheet_name)
            folder_path = create_folder_csv()
            csv_file_path = os.path.join(folder_path, f'{sheet_name}.csv')
            data_sheet.to_csv(csv_file_path, index=False)
        return f'planilhas/{os.path.basename(file_path).replace(".xlsx", "")}/'
    
    def push_worksheets(spreadsheet:Spreadsheet, folder_path):
        print('atualizando planilhas')
        def get_or_create_worksheet(spreadsheet, sheet_title, num_rows, num_cols):
            try:
                worksheet = spreadsheet.worksheet(sheet_title)
            except gspread.exceptions.WorksheetNotFound:
                print(sheet_title)
                worksheet = spreadsheet.add_worksheet(title=sheet_title[:100], rows=num_rows, cols=num_cols)
            return worksheet
        
        def update_worksheets():
            def check_duplicates(ws:Worksheet):
                novos_dados = ws.get_all_values()
                df_novos_dados = pd.DataFrame(novos_dados[1:], columns=novos_dados[0])
                duplicatas = df_novos_dados[df_novos_dados.duplicated(keep=False)]
                if not duplicatas.empty:
                    print("Duplicatas encontradas na planilha:")
                    print(duplicatas)
                else:
                    print("Não há duplicatas na planilha.")

            def remove_duplicates(ws:Worksheet):
                data = ws.get_all_values()
                unique_lines = []
                lines_already_seen = set()
                for linha in data:
                    chave = tuple(linha)
                    if chave not in lines_already_seen:
                        unique_lines.append(linha)
                        lines_already_seen.add(chave)
                ws.clear()
                ws.update(unique_lines)

            files = os.listdir(folder_path)
            for file in files:
                with open(f'{folder_path}/{file}', 'r') as file:
                    csv_contents = file.read().splitlines()
                    have_text = False
                    for line in csv_contents:
                        if not line.isspace() and have_text is False:
                            have_text = True
                            continue
                        else:
                            break
                    if have_text is False:
                        continue

                    with pd.ExcelFile(folder_path[:-1]+'.xlsx') as xls:
                        data_sheet = pd.read_excel(xls, os.path.basename(file.name).replace('.csv',''))
                        num_rows, num_cols = data_sheet.shape
                ws = get_or_create_worksheet(spreadsheet, os.path.basename(file.name).replace('.csv',''), num_rows, num_cols)
                ws:Worksheet
                # update de valores
                try:
                    ws.clear()
                    ws.update([line.split(',') for line in csv_contents])
                except Exception as e:
                    print(f'{e}: \n\n{csv_contents}\n\n')
                    continue
                # removendo qualquer row duplicata
                remove_duplicates(ws)
                # final check
                # check_duplicates(ws)
            try:
                sheet_origin = spreadsheet.get_worksheet(0)
                if sheet_origin.title == 'Sheet1' or sheet_origin.title == 'Página1':
                    spreadsheet.del_worksheet(sheet_origin)
            except Exception as e:
                print(f'remove sheet problem: {e}')

        def share_with_users():
            emails_to_share = ['']
            users_with_access = spreadsheet.list_permissions()
            users_to_share = []
            for email in emails_to_share:
                has_access = False
                for user in users_with_access:
                    if email == user['emailAddress']:
                        has_access = True
                        break
                if not has_access:
                    users_to_share.append(email)

            # for user in users_to_share:
                # spreadsheet.share(user, perm_type='user', role='writer')
        update_worksheets()
        share_with_users()
        print(f"Arquivo {spreadsheet.title} carregado com sucesso para o Google Planilhas!")

    gc = login()
    # sheet_files = os.listdir('planilhas')
    # sheet_files = [file for file in sheet_files if file.endswith('.xlsx')]
    for sheet_file in sheet_files:
        file_path = f'planilhas/{sheet_file}'
        spreadsheet = get_sheet_file(gc, file_path)
        folder_path = convert_excel_to_csv(file_path)
        push_worksheets(spreadsheet, folder_path)


def change_values_in_all_sheets(sheet:Union[str, list]):
    def login():
        credentials = Credentials.from_service_account_file('', scopes=SCOPES)
        gc = gspread.authorize(credentials)
        return gc

    def get_sheet_files(sheet):
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        
        sheet_files = []
        if type(sheet) == list:
            with open('settings.json', 'r') as f:
                js = json.load(f)
            sheet_files = []
            for key, value in js.items():
                if key != 'last_date_updated':
                    sheet_files.append(value)
            print(sheet_files)
            return sheet_files
        elif type(sheet) == str:
            sheet_files.append(settings[sheet])
        # no_priority_list = ['last_date_updated', 'Campanhas', 'Profissionais', 'Agenda', 'Auditoria', 'Clientes']
        
        # # Adding priority sheets first
        # for key, value in settings.items():
        #     if key not in no_priority_list:
        #         sheet_files.append(value)
        
        # # Adding non-priority sheets
        # for key, value in settings.items():
        #     if key in no_priority_list and key != 'last_date_updated':
        #         sheet_files.append(value)
        print(sheet_files)
        return sheet_files

    def col_idx_to_str(col_idx):
        """Converts a column index to a column letter (e.g., 1 -> 'A', 27 -> 'AA')."""
        col_str = ''
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            col_str = chr(65 + remainder) + col_str
        return col_str

    def alter_values(sheet_files):

        def is_digit(value: str) -> bool:
            value = value.replace(',', '.')
            
            try:
                float_value = float(value)
                return True
            except ValueError:
                return False

        def convert_value(value: str) -> int:
            values = value.split(',')
            if len(values) > 1:
                value1 = values[0].replace('.', '')  # Remove o ponto
                value2 = values[1]
                return int(value1) + int('0.'+value2)  # Converte e soma os valores
            else:
                value = value.replace('.', '')  # Remove o ponto
                return int(value)  # Converte o valor para inteiro
        
        for sheet_file in sheet_files:
            gc = login()
            spreadsheet = gc.open_by_key(sheet_file)
            worksheets = spreadsheet.worksheets()
            
            for worksheet in worksheets:
                all_cells = worksheet.get_all_values()
                modified_rows = []

                for row in all_cells:
                    new_row = []
                    for cell in row:
                        new_value = cell
                        if isinstance(new_value, str) and new_value.count('"') == 1:
                            new_value = new_value.replace('"', '')
                        
                        if isinstance(new_value, str) and new_value.count("'") == 1:
                            new_value = new_value.replace("'", "")
                        
                        if isinstance(new_value, str) and is_digit(new_value.replace('.0', '')) and new_value.count('.0') == 1:
                            new_value = convert_value(new_value.replace('.0', ''))
                        
                        elif isinstance(new_value, str) and is_digit(new_value):
                            new_value = convert_value(new_value)

                        new_row.append(new_value)
                    modified_rows.append(new_row)

                # Determine the full range for update
                num_rows = len(modified_rows)
                num_cols = len(modified_rows[0]) if num_rows > 0 else 0
                last_col_letter = col_idx_to_str(num_cols)
                range_name = f'A1:{last_col_letter}{num_rows}'

                try:
                    worksheet.clear()  # Clear the worksheet before updating
                    worksheet.update(values=modified_rows, range_name=range_name)
                    print(f"Worksheet {worksheet.title} updated successfully.")
                    sleep(2)
                except Exception as e:
                    print(f"Failed to update worksheet {worksheet.title}: {e}")
                    sleep(10)
                    try:
                        worksheet.clear()
                        worksheet.update(values=modified_rows, range_name=range_name)
                        print(f"Retrying: Worksheet {worksheet.title} updated successfully.")
                        sleep(2)
                    except Exception as e:
                        print(f"Failed to update worksheet {worksheet.title} on retry: {e}")
                        sleep(10)

    sheet_files = get_sheet_files(sheet)
    alter_values(sheet_files)

faker = Faker('pt_BR')

# Função para gerar dados de pessoas
def generate_person_data(num_rows):
    """
    Gera uma lista de dados simulados para pessoas com consistência garantida.

    Args:
        num_rows (int): Número de linhas (pessoas) a gerar.

    Returns:
        list: Lista de listas contendo os dados das pessoas.
    """
    data = [["Nome", "Email", "Telefone", "Cidade", "Estado"]]  # Cabeçalhos
    unique_set = set()  # Conjunto para garantir unicidade de e-mails, por exemplo

    for _ in range(num_rows):
        while True:
            name = faker.name()
            email = faker.email()
            phone = faker.phone_number()
            city = faker.city()
            state = faker.state_abbr()

            # Garantir que o e-mail seja único
            if email not in unique_set:
                unique_set.add(email)
                break

        # Adiciona os dados consistentes para a pessoa
        data.append([name, email, phone, city, state])
        print([name, email, phone, city, state])
    return data

# Preenche a planilha com dados simulados
def fill_spreadsheet_with_fake_data(spreadsheet_id, num_rows):
    """
    Preenche a primeira aba do Google Sheets com dados simulados.

    Args:
        spreadsheet_id (str): ID do Google Sheets.
        num_rows (int): Número de linhas de dados a preencher.
    """
    try:
        # Login e obtenção do spreadsheet
        gc = login()
        spreadsheet = gc.open_by_key(spreadsheet_id)

        # Seleciona a primeira aba
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.clear()
        # Gera os dados simulados
        fake_data = generate_person_data(num_rows)

        # Envia os dados para o Google Sheets
        worksheet.update(fake_data, 'A1')
        print(f"Dados simulados enviados com sucesso para {worksheet.title}.")
    except Exception as e:
        print(f"Erro ao preencher a planilha: {e}")

if __name__ == '__main__':
    gc = login()
    sp = gc.open_by_key(id)
    fill_spreadsheet_with_fake_data(sp.id, 50000)