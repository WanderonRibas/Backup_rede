import pymysql
import ipaddress
import sys
from detectar_vendor import detectar_vendor

# === RECEBENDO ARGUMENTOS DO PHP ===
if len(sys.argv) < 5:
    print("Uso: python cadastro_massa.py <ip_range> <usuario> <senha> <porta>")
    sys.exit(1)

IP_RANGE = sys.argv[1]
SSH_USER = sys.argv[2]
SSH_PASSWORD = sys.argv[3]
SSH_PORT = int(sys.argv[4])

# === CONFIGURAÇÕES DO BANCO ===
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Master@308882#"
DB_NAME = "net_backup"

# Função para gerar lista de IPs do range
def gerar_ips(range_str):
    inicio, fim = range_str.split('-')
    ip_inicio = ipaddress.IPv4Address(inicio)
    ip_fim = ipaddress.IPv4Address(fim)
    return [str(ip) for ip in range(int(ip_inicio), int(ip_fim) + 1)]

# Função para cadastrar no banco
def cadastrar_dispositivo(ip, vendor):
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor()

    sql = """
    INSERT INTO dispositivos (ip, porta_ss, usuario, senha, vendor)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (ip, SSH_PORT, SSH_USER, SSH_PASSWORD, vendor))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[OK] {ip} ({vendor}) cadastrado no banco.")

# === EXECUÇÃO ===
ips = gerar_ips(IP_RANGE)
print(f"Testando {len(ips)} IPs...\n")

for ip in ips:
    vendor = detectar_vendor(ip, SSH_PORT, SSH_USER, SSH_PASSWORD)

    if vendor not in ["desconhecido", "erro"]:
        cadastrar_dispositivo(ip, vendor)
    elif vendor == "desconhecido":
        print(f"[IGNORADO] {ip} respondeu SSH mas não foi possível identificar vendor.")
    else:
        print(f"[X] {ip} não respondeu ao SSH ou ocorreu erro.")
