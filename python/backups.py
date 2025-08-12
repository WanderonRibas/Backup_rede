import paramiko
from netmiko import ConnectHandler
import time
import re
import os

def backup_huawei(host, port, username, password, caminho_backup):
    """
    Realiza backup de um dispositivo Huawei via SSH com Netmiko,
    salvando a configuração atual (display current-configuration).
    """
    device = {
        'device_type': 'huawei',
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'secret': password,
    }

    try:
        # Garante que o diretório de backup exista
        os.makedirs(caminho_backup, exist_ok=True)

        # Conecta ao dispositivo
        with ConnectHandler(**device) as conn:
            conn.send_command('screen-length 0 temporary')  # Evita paginação
            output = conn.send_command('display current-configuration')  # Captura a config

        # Cria o nome do arquivo baseado no IP e data
        filename = os.path.join(caminho_backup, f"Huawei_{host.replace('.', '_')}.cfg")

        # Salva o arquivo
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"[{host}] ✅ Backup Huawei salvo em {filename}")
        return True

    except Exception as e:
        print(f"[{host}] ❌ Erro no backup Huawei: {e}")
        return False

def backup_mikrotik(host, port, username, password, caminho_backup):
    ssh = None
    sftp = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, password=password, timeout=10)

        # Obtem identidade
        stdin, stdout, stderr = ssh.exec_command("/system identity print")
        identidade_saida = stdout.read().decode()
        match = re.search(r'name:\s*(\S+)', identidade_saida)
        if not match:
            raise Exception("Não foi possível extrair o nome da identidade")
        nome_identidade = match.group(1)

        # Gera export
        ssh.exec_command(f"/export file={nome_identidade}")
        time.sleep(10)  # Aguarda exportação

        caminho_remoto = f"/{nome_identidade}.rsc"
        os.makedirs(caminho_backup, exist_ok=True)
        nome_arquivo_local = os.path.join(caminho_backup, f"{nome_identidade}.rsc")

        sftp = ssh.open_sftp()
        sftp.get(caminho_remoto, nome_arquivo_local)
        print(f"[{host}] ✅ Backup MikroTik salvo em {nome_arquivo_local}")
        return True
    except Exception as e:
        print(f"[{host}] ❌ Falha backup MikroTik: {e}")
        return False
    finally:
        if sftp: sftp.close()
        if ssh: ssh.close()

def backup_vsol(host, port, username, password, caminho_backup):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, timeout=10)

        shell = client.invoke_shell()
        time.sleep(2)

        shell.send(username + '\n')
        time.sleep(1)
        shell.send(password + '\n')
        time.sleep(2)

        shell.send("enable\n")
        time.sleep(1)
        shell.send(password + '\n')
        time.sleep(1)

        shell.send("terminal length 0\n")
        time.sleep(1)

        shell.send("show running-config\n")
        time.sleep(1)

        output = ""
        start_time = time.time()
        timeout = 40  # até 60 segundos para capturar toda a configuração

        while True:
            if shell.recv_ready():
                chunk = shell.recv(65535).decode('utf-8', errors='ignore')
                output += chunk
                # Para se encontrar o prompt e ter tempo suficiente de captura
                if "#" in chunk and (time.time() - start_time) > 3:
                    break
            if (time.time() - start_time) > timeout:
                break
            time.sleep(0.5)

        # Divide em linhas
        linhas = output.splitlines()

        # Encontra o índice da primeira linha que é apenas "!"
        inicio_idx = None
        for idx, linha in enumerate(linhas):
            if linha.strip() == "!":
                inicio_idx = idx
                break

        # Se achou, corta o output a partir dali
        if inicio_idx is not None:
            linhas_filtradas = linhas[inicio_idx:]
        else:
            linhas_filtradas = linhas

        # Remove linhas de prompt e vazias
        linhas_filtradas = [
            linha for linha in linhas_filtradas
            if not linha.strip().endswith("#") and linha.strip() != ""
        ]

        saida_final = "\n".join(linhas_filtradas)

        os.makedirs(caminho_backup, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_backup, f"VSOL_{host}.cfg")

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(saida_final.strip())

        print(f"[{host}] ✅ Backup V-SOL filtrado salvo em {caminho_arquivo}")
        return True

    except paramiko.AuthenticationException:
        print(f"[{host}] ❌ Erro de autenticação.")
        return False
    except paramiko.SSHException as e:
        print(f"[{host}] ❌ Erro SSH: {e}")
        return False
    except Exception as e:
        print(f"[{host}] ❌ Erro inesperado: {e}")
        return False
    finally:
        if 'client' in locals() and client:
            client.close()
            print(f"[{host}] 🔹 Conexão fechada.")

def backup_ubiquit(host, port, username, password, caminho_backup):
    ssh = None
    sftp = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, password=password, timeout=10)

        caminho_remoto = '/config/config.boot'
        os.makedirs(caminho_backup, exist_ok=True)
        nome_arquivo_local = os.path.join(caminho_backup, f"UBT_{host.replace('.', '_')}_config.boot")

        sftp = ssh.open_sftp()
        sftp.get(caminho_remoto, nome_arquivo_local)
        print(f"[{host}] ✅ Backup Ubiquiti salvo em {nome_arquivo_local}")
        return True
    except Exception as e:
        print(f"[{host}] ❌ Falha backup Ubiquiti: {e}")
        return False
    finally:
        if sftp: sftp.close()
        if ssh: ssh.close()
