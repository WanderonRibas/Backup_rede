#!/usr/bin/env bash

# ==========================================
# Instalador do Sistema de Backup de Rede
# Autor: Wanderon Ribas
# Compatível com: Debian / Ubuntu
# ==========================================

set -euo pipefail

# --- Etapa 1: Permissões e pré-requisitos ---
echo "=== Verificando permissões de root ==="
if [[ $EUID -ne 0 ]]; then
   echo "Este script deve ser executado como root. Use 'sudo'."
   exit 1
fi

echo "=== Atualizando pacotes e instalando dependências ==="
apt-get update -y
apt-get install -y git apache2 php libapache2-mod-php php-curl php-mysqli \
                   python3 python3-pip mysql-server

# --- Etapa 2: Configuração do MySQL ---
echo "=== Configurando MySQL ==="
read -sp "Digite a senha do usuário root do MySQL: " MYSQL_PASS
echo
mysql -u root -p"$MYSQL_PASS" -e "CREATE DATABASE IF NOT EXISTS net_backup;"
mysql -u root -p"$MYSQL_PASS" -e "CREATE USER IF NOT EXISTS 'root_user'@'localhost' IDENTIFIED BY '$MYSQL_PASS';"
mysql -u root -p"$MYSQL_PASS" -e "GRANT ALL PRIVILEGES ON net_backup.* TO 'root_user'@'localhost';"
mysql -u root -p"$MYSQL_PASS" -e "FLUSH PRIVILEGES;"
echo "Banco de dados e usuário configurados."

# --- Etapa 3: Clonando e instalando a aplicação ---
echo "=== Clonando repositório ==="
TMP_DIR=$(mktemp -d)
git clone https://github.com/WanderonRibas/Backup_rede.git "$TMP_DIR"

echo "=== Copiando arquivos para o Apache ==="
rm -rf /var/www/html/*
cp -r "$TMP_DIR"/*.php /var/www/html/
cp -r "$TMP_DIR"/static /var/www/html/

# Criando pasta de backups e arquivo agendador.ini
mkdir -p /var/www/html/backups
touch /var/www/html/agendador.ini
chown -R www-data:www-data /var/www/html
chmod -R 775 /var/www/html/backups
chmod 664 /var/www/html/agendador.ini

# --- Etapa 4: Configuração da API Python ---
echo "=== Instalando dependências Python ==="
mkdir -p /opt/sistema-backup-python
cp -r "$TMP_DIR"/python/* /opt/sistema-backup-python/
pip3 install -r /opt/sistema-backup-python/requirements.txt

echo "=== Iniciando API Python ==="
nohup python3 /opt/sistema-backup-python/app.py > /var/log/backup-api.log 2>&1 &
echo "API Python iniciada. Log em /var/log/backup-api.log"

# --- Etapa 5: Finalização ---
rm -rf "$TMP_DIR"
systemctl restart apache2

echo "=========================================="
echo "Instalação concluída com sucesso!"
echo "Acesse: http://SEU-IP ou http://localhost"
echo "Usuário do MySQL: root_user / Senha: (a mesma informada)"
echo "=========================================="
