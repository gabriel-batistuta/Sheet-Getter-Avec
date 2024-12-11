# avec_relatorio

Esse código serve pra pegar o fluxo de dados de relatórios em excel (cerca de 500) da plataforma AVEC e junta-los em poucos arquivos (menos de 10) e salva-los no google planilhas usando a api do google planilhas e google drive

- código não funciona por si só, precisa de credenciais de usuário
- esse código era privado e pra deixar público tirei tudo de sensível tornando não executavel
- serve somente pra estudo 

lista de códigos usados na versão final do software:
- main.py
- erase.py
- google_sheet.py

tutorial: [tutorial.mp4](https://github.com/gabriel-batistuta/Sheet-Getter-Avec/raw/refs/heads/master/tutorial.mp4)

Pra fazer o arquivo .EXE 
```bash
pyinstaller --onefile --noconsole --icon=assets/.ico --name SOFTWARE_NAME app.py
```
