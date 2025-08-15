#!/bin/bash

# Este script automatiza a instalação do Sistema de Backup em ambientes Linux (Debian/Ubuntu).
# Ele instala as dependências, clona o projeto e configura os serviços.

# --- Etapa 1: Pré-requisitos e Verificações ---
echo "--- Verificando permissões de root ---"
if [[ $EUID -ne 0 ]]; then
   echo "Este script deve ser executado como root. Use 'sudo'." 
   exit 1
fi

echo "--- Atualizando o sistema e instalando dependências essenciais ---"
apt-get update -y
apt-get install -y git apache2 php libapache2-mod-php php-curl php-mysqli python3 python3-pip mysql-server

# Verifica se os pacotes foram instalados corretamente
if [ $? -ne 0 ]; then
    echo "Erro: A instalação de pacotes falhou. Verifique sua conexão e tente novamente."
    exit 1
fi

# --- Etapa 2: Configuração do Servidor MySQL ---
echo "--- Configurando o MySQL (você precisará definir uma senha) ---"
mysql_secure_installation

# Cria o banco de dados e o usuário para a aplicação
echo "--- Criando o banco de dados 'net_backup' e o usuário 'root_user' ---"
# NOTA: O script abaixo usa a senha padrão 'root_password'.
# Certifique-se de que sua aplicação PHP e Python usam essa mesma senha.
# A melhor prática é usar uma variável de ambiente para a senha, mas por simplicidade, estamos usando a senha 'root_password'
mysql -u root -proot_password -e "CREATE DATABASE IF NOT EXISTS net_backup;"
mysql -u root -proot_password -e "CREATE USER 'root_user'@'localhost' IDENTIFIED BY 'root_password';"
mysql -u root -proot_password -e "GRANT ALL PRIVILEGES ON net_backup.* TO 'root_user'@'localhost';"
mysql -u root -proot_password -e "FLUSH PRIVILEGES;"
echo "Banco de dados e usuário criados com sucesso."

# --- Etapa 3: Instalação da Aplicação ---
echo "--- Clonando o repositório do GitHub ---"
# Substitua a URL abaixo pela URL do seu repositório!
git clone https://github.com/WanderonRibas/Backup_rede.git /tmp/sistema-backup

echo "--- Copiando arquivos para o diretório do servidor web ---"
# Apaga o diretório padrão e copia o novo conteúdo
rm -rf /var/www/html/*
cp -r /tmp/sistema-backup/php/* /var/www/html/

# Configura as permissões de escrita para a pasta de backups e agendador.ini
echo "--- Configurando permissões de arquivos ---"
mkdir -p /var/www/html/backups
chmod 777 /var/www/html/backups
touch /var/www/html/agendador.ini
chmod 777 /var/www/html/agendador.ini

# --- Etapa 4: Configuração da Aplicação Python ---
echo "--- Instalando bibliotecas Python (Flask, schedule) ---"
pip3 install flask schedule

echo "--- Iniciando a API Python em segundo plano ---"
# CORRIGIDO: O script agora inicia o app.py em vez de agendador.py
nohup python3 /tmp/sistema-backup/python/app.py > /var/log/backup-api.log 2>&1 &
echo "API Python iniciada. Verifique o log em /var/log/backup-api.log"

# --- Etapa 5: Finalização e Mensagem de Sucesso ---
echo "--- Limpando arquivos temporários ---"
rm -rf /tmp/sistema-backup

echo "--- Reiniciando o Apache ---"
systemctl restart apache2
echo "Apache reiniciado."

echo "==================================================="
echo "Instalação concluída com sucesso!"
echo "Acesse a aplicação em http://localhost ou seu IP do servidor."
echo "==================================================="
