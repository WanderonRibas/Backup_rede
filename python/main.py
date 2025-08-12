# -*- coding: utf-8 -*-
import threading
import time
import os
import mysql.connector
from datetime import datetime
import sys

from ler_arquivos import carregar_dispositivos
from chave_client import validar_chave
from backups import backup_huawei, backup_mikrotik, backup_vsol, backup_ubiquit

# Pega o diretório do script Python em execução
script_dir = os.path.dirname(os.path.abspath(__file__))

# Garante que a saída do console seja UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# === Configurações ===
CHAVE_ATIVACAO = "teste"

# Constrói o caminho completo para a pasta de backups.
# O os.path.join() junta o diretório do script com o nome da pasta,
# resultando em um caminho absoluto (ex: C:\laragon\www\SistemaBackup\python\backups).
CAMINHO_BACKUP = os.path.join(script_dir, "backups")

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Master@308882#',
    'database': 'net_backup'
}

# === Valida chave ===
if not validar_chave(CHAVE_ATIVACAO, "http://172.16.11.2:5000/validate"):
    sys.exit("Encerrando execução devido à chave inválida.")

# === Cria pasta de backup se necessário ===
os.makedirs(CAMINHO_BACKUP, exist_ok=True)

# === Função para salvar status no banco ===
def salvar_status(host, status):
    """
    Atualiza o campo status_backup (0 ou 1) na tabela dispositivos
    para o dispositivo com o IP informado.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dispositivos
            SET status_backup = %s
            WHERE ip = %s
        """, (int(status), host))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{host}] 🔹 Status {int(status)} atualizado na tabela dispositivos.")

    except Exception as e:
        print(f"[{host}] ❌ Erro ao atualizar status no banco: {e}")


# === Função para processar cada host ===
def processar_host(disp):
    ip = disp['ip']
    usuario = disp['usuario']
    senha = disp['senha']
    porta = disp.get('porta_ssh', 22)
    vendor = disp['vendor']

    print(f"\n[{ip}] Iniciando backup do vendor {vendor}...")

    status = False

    try:
        if vendor == "Huawei":
            status = backup_huawei(ip, porta, usuario, senha, CAMINHO_BACKUP)
        elif vendor == "Mikrotik":
            status = backup_mikrotik(ip, porta, usuario, senha, CAMINHO_BACKUP)
        elif vendor == "VSOL":
            status = backup_vsol(ip, porta, usuario, senha, CAMINHO_BACKUP)
        elif vendor == "Ubiquit":
            status = backup_ubiquit(ip, porta, usuario, senha, CAMINHO_BACKUP)
        else:
            print(f"[{ip}] ❌ Vendor não suportado ou não identificado.")

    except Exception as e:
        print(f"[{ip}] ❌ Erro geral: {e}")
        status = False

    # Salva status no banco
    salvar_status(ip, status)

    if status:
        print(f"[{ip}] ✅ Backup bem-sucedido e registrado no banco")
    else:
        print(f"[{ip}] ❌ Backup falhou e registrado no banco")

# === Execução paralela para todos os dispositivos do banco ===
threads = []
for disp in carregar_dispositivos():
    t = threading.Thread(target=processar_host, args=(disp,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n✅ Processo de backup finalizado para todos os hosts.")