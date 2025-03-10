from flask import Flask, jsonify
import pyodbc
import requests
import threading
import time

app = Flask(__name__)

# Configuração da conexão com SQL Server
server = '192.168.30.16'
database = 'EXPERTOS'
username = 'sa'
password = 'L@gtech1100'

conn_string = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'

# ✅ Função para conectar ao banco de dados
def get_db_connection():
    try:
        conn = pyodbc.connect(conn_string, timeout=10)  # Timeout de 10s para evitar travamentos
        return conn
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
        return None

# ✅ Rota para buscar dados do SQL Server
@app.route('/dados', methods=['GET'])
def get_dados():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"erro": "Falha ao conectar ao banco de dados"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT TOP 10 * FROM usuario")  # Ajuste conforme sua tabela
        colunas = [column[0] for column in cursor.description]
        dados = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        conn.close()
        return jsonify(dados)
    
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return jsonify({"erro": str(e)}), 500


# ✅ Rota para consumir a API hospedada no Render
@app.route('/api-remota', methods=['GET'])
def get_api_remota():
    try:
        url = "https://api-expert-os.onrender.com/dados"  # Ajuste se necessário
        response = requests.get(url, timeout=15)  # Aumenta o tempo de espera

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"Erro ao conectar na API externa: {response.status_code}")
            return jsonify({"erro": "Falha ao conectar na API externa", "status_code": response.status_code}), 500
    
    except Exception as e:
        print(f"Erro ao acessar API externa: {e}")
        return jsonify({"erro": str(e)}), 500


# ✅ Função para pingar a API e evitar que hiberne no Render
def keep_awake():
    url = "https://api-expert-os.onrender.com/dados"  # Substitua pela URL da sua API
    while True:
        try:
            response = requests.get(url)
            print(f"Ping enviado! Status: {response.status_code}")
        except Exception as e:
            print(f"Erro ao pingar API: {e}")
        
        time.sleep(600)  # Pingar a cada 10 minutos


# ✅ Iniciar o ping automático em uma thread separada
threading.Thread(target=keep_awake, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
