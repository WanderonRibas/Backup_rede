import time
import subprocess
import configparser
import schedule
from threading import Thread
from flask import Flask, jsonify, request
import os

# --- Configurações da Aplicação e Agendador ---
app = Flask(__name__)
schedule_instance = schedule

# --- PONTO CRÍTICO: Caminho do arquivo de configuração ---
caminho_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_arquivo_ini = os.path.join(caminho_do_script, 'agendador.ini')
print(f"DEBUG: O caminho do arquivo .ini será: {caminho_arquivo_ini}")


def executar_main_py():
    """Função para executar o script main.py."""
    print("Iniciando a execução do main.py...")
    try:
        caminho_main_py = os.path.join(caminho_do_script, 'main.py')
        subprocess.run(['python', caminho_main_py], check=True)
        print("Execução do main.py concluída com sucesso!")
        return True, "Execução do main.py concluída com sucesso!"
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o main.py: {e}")
        return False, f"Erro ao executar o main.py: {e}"
    except FileNotFoundError:
        print(f"Erro: O arquivo 'main.py' não foi encontrado em {caminho_main_py}.")
        return False, "Erro: O arquivo 'main.py' não foi encontrado."


def salvar_configuracao_ini(dias_semana, hora_agendada):
    """Salva a nova configuração do agendador no arquivo .ini."""
    config = configparser.ConfigParser()
    config['AGENDADOR'] = {
        'dias_semana': ','.join(dias_semana),
        'hora_execucao': hora_agendada
    }
    try:
        with open(caminho_arquivo_ini, 'w') as configfile:
            config.write(configfile)
        print(f"Nova configuração salva com sucesso em '{caminho_arquivo_ini}'.")
        return True, "Configuração salva com sucesso."
    except IOError as e:
        print(f"Erro CRÍTICO ao salvar o arquivo .ini: {e}")
        return False, f"Erro de I/O ao salvar a configuração: {e}"
    except Exception as e:
        print(f"Erro inesperado ao salvar o arquivo .ini: {e}")
        return False, f"Erro inesperado ao salvar a configuração: {e}"


def configurar_agendador(dias_semana, hora_agendada):
    """
    Configura o agendamento dinamicamente, limpando os agendamentos anteriores.
    Agora, lida corretamente com a opção 'todos'.
    """
    global schedule_instance
    schedule_instance.clear()

    dias_validos = {
        'segunda': schedule_instance.every().monday,
        'terca': schedule_instance.every().tuesday,
        'quarta': schedule_instance.every().wednesday,
        'quinta': schedule_instance.every().thursday,
        'sexta': schedule_instance.every().friday,
        'sabado': schedule_instance.every().saturday,
        'domingo': schedule_instance.every().sunday
    }
    
    msg = ""
    if not dias_semana or (len(dias_semana) == 1 and dias_semana[0].lower().strip() == ''):
        msg = "Agendamento desativado."
    elif 'todos' in dias_semana:
        schedule_instance.every().day.at(hora_agendada).do(executar_main_py)
        msg = f"Tarefa agendada para todos os dias às {hora_agendada}."
    else:
        dias_agendados = []
        for dia in dias_semana:
            dia = dia.strip().lower()
            if dia in dias_validos:
                dias_validos[dia].at(hora_agendada).do(executar_main_py)
                dias_agendados.append(dia)
            else:
                print(f"Aviso: Dia '{dia}' inválido. Ignorando.")
        msg = f"Tarefa agendada para os dias {', '.join(dias_agendados)} às {hora_agendada}."

    print(msg)
    
    salvou, msg_salvar = salvar_configuracao_ini(dias_semana, hora_agendada)
    if not salvou:
        print(f"Erro ao salvar a configuração: {msg_salvar}")
    
    return True, msg

# --- PONTO CRÍTICO: A função 'agendador_daemon' foi movida para cá. ---
def agendador_daemon():
    """Loop do agendador, rodando em uma thread separada."""
    while True:
        schedule_instance.run_pending()
        time.sleep(1)


# --- Rotas da API (Endpoints) ---
@app.route('/executar-tarefa', methods=['POST'])
def executar_tarefa_manual():
    """Endpoint para executar o main.py manualmente."""
    print("Comando recebido via API. Executando main.py...")
    sucesso, mensagem = executar_main_py()
    
    if sucesso:
        return jsonify({'status': 'sucesso', 'mensagem': mensagem}), 200
    else:
        return jsonify({'status': 'erro', 'mensagem': mensagem}), 500


@app.route('/agendar-tarefa', methods=['POST'])
def agendar_tarefa_api():
    """Novo endpoint para agendar a tarefa via API."""
    data = request.get_json()
    dias_semana = data.get('dias_semana', [])
    hora_execucao = data.get('hora_execucao', None)
    
    if not hora_execucao:
        return jsonify({'status': 'erro', 'mensagem': 'Hora de execução não fornecida.'}), 400

    sucesso, mensagem = configurar_agendador(dias_semana, hora_execucao)
    
    if sucesso:
        return jsonify({'status': 'sucesso', 'mensagem': mensagem}), 200
    else:
        return jsonify({'status': 'erro', 'mensagem': mensagem}), 500


# --- Lógica principal ---
if __name__ == '__main__':
    # Leitura inicial do INI para carregar a última configuração
    config = configparser.ConfigParser()
    if os.path.exists(caminho_arquivo_ini):
        config.read(caminho_arquivo_ini)
        try:
            dias_semana_ini = config['AGENDADOR'].get('dias_semana', '').split(',')
            hora_execucao_ini = config['AGENDADOR'].get('hora_execucao', '')
            if hora_execucao_ini:
                configurar_agendador(dias_semana_ini, hora_execucao_ini)
        except (configparser.Error, KeyError) as e:
            print(f"Aviso: Erro ao ler a configuração inicial do agendador.ini: {e}")
    else:
        print("Arquivo 'agendador.ini' não encontrado. Iniciando sem agendamento prévio.")

    agendador_thread = Thread(target=agendador_daemon, daemon=True)
    agendador_thread.start()
    
    app.run(host='0.0.0.0', port=5000)
