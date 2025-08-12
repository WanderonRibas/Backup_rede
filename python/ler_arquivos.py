import mysql.connector

def carregar_dispositivos():
    # Configuração do banco de dados
    conexao = mysql.connector.connect(
        host="localhost",        # IP ou host do banco
        user="root",             # Usuário do banco
        password="Master@308882#",  # Senha do banco
        database="net_backup"    # Nome do banco
    )

    cursor = conexao.cursor(dictionary=True)

    # Consulta dos dispositivos com as colunas corretas
    cursor.execute("SELECT ip, porta_ssh, usuario, senha, vendor FROM dispositivos")
    dispositivos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return dispositivos


if __name__ == "__main__":
    dispositivos = carregar_dispositivos()
    
    # Exemplo de uso
    for disp in dispositivos:
        print(f"IP: {disp['ip']} | Porta: {disp['porta_ssh']} | Usuário: {disp['usuario']} | Senha: {disp['senha']} | Vendor: {disp['vendor']}")
