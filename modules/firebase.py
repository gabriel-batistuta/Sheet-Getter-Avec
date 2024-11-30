from time import time
from firebase_admin import credentials, initialize_app, storage, firestore
import json
import re

def replace_to_postgres_name(name):
    # Remove ou substitui caracteres indesejados
    name = (name.replace('"', '')
                .replace("'", '')
                .replace('?', '')
                .replace('/', ' ')
                .replace('\\', '')
                .replace('(', '')
                .replace(')', '')
                .replace('[', '')
                .replace(']', '')
                .replace('{', '')
                .replace('}', '')
                .replace('+', '_')
                .replace('*', '_')
                .replace('&', '_')
                .replace('^', '_')
                .replace('%', '')
                .replace('$', '')
                .replace('#', '')
                .replace('@', '')
                .replace('!', '')
                .replace('~', '')
                .replace('`', '')
                .replace('|', '_')
                .replace('<', '')
                .replace('>', '')
                .replace('=', '_')
                .replace(':', '')
                .replace(';', '')
                .replace('  ', ' ')
                .replace(',', ' ')
                .replace(' ', '_')
                .replace('-', '_')
                .replace('.', '')
                .replace('ç', 'c')
                .lower())

    if name == 'id':
        return 'id_avec'
    
    if name[-1] in ['.', '%', '_', '-']:
        name = name[:-1]
    
    if name[0] in ['.', '%', '_', '-']:
        name = name[1:]
    
    # Verifica se a string contém apenas caracteres válidos (letras, números e underscores)
    name = re.sub(r'[^a-z0-9_]', '', name)
    
    return name

def initialize():
    projectId = ''
    apiKey = ''
    service_account = ''

    config = {
        "apiKey": f"{apiKey}",
        "authDomain": f"{projectId}.firebaseapp.com",
        "databaseURL": f"https://{projectId}.firebaseio.com",
        "storageBucket": f"{projectId}.appspot.com",
        "serviceAccount": f"{service_account}"
    }

    cred = credentials.Certificate(config['serviceAccount'])
    initialize_app(cred, {'storageBucket': f'{config["storageBucket"]}'})

initialize()
collection = ''
db = firestore.client()

def not_exists_in_firebase_by_id(id:str, collection:str) -> bool:
    doc = db.collection(collection).document(id).get()

    if doc.exists:
        return False
    else:
        return True

def upload_report(data:dict, report_name:str, collection):
    # faz uma referencia a um objeto que ira ser criado na coleção
    doc_ref = db.collection(u'{0}'.format(collection))

    if not_exists_in_firebase_by_id(report_name, collection):
        # cria o objeto
        json_ref = doc_ref.document(replace_to_postgres_name(report_name))
        # envia os dados ao objeto
        json_ref.set(data)
        print(f'Added document with id {json_ref.id} to Firestore Database')
    else:
        print(f'Documento já existe no banco de dados')

def update_report(report, report_name, collection):
    doc_ref = db.collection(collection).document(replace_to_postgres_name(report_name))
    doc_ref.update(report)
    print("Documento atualizado com sucesso.")

def push_reports(JSON):

    report = json.loads(JSON)['reports']
    for reports in report:
        for report_categorie, report_categorie_value in reports.items():
            print(f'Categoria: {report_categorie}')
            for especific_report in report_categorie_value:
                for table_name, table_values in especific_report.items():
                    table_name = replace_to_postgres_name(table_name)
                    print(f'Tabela: {table_name}')
                    upload_report({table_name:table_values}, table_name, report_categorie)
                    update_report({table_name:table_values}, table_name, report_categorie)

if __name__ == '__main__':
    with open('./reports.json', 'r') as f:
        push_reports(f.read())