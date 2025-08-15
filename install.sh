#!/bin/bash

set -euo pipefail

echo "=== Verificando permissões de root ==="
if [ "$EUID" -ne 0 ]; then
    echo "Por favor, execute como root"
    exit 1
fi

echo "=== Atualizando pacotes e instalando dependências ==="
apt-get update -y
apt-get install -y git apache2 php libapache2-mod-php php-curl php-mysql                    python3 python3-pip default-mysql-server

echo "=== Instalando dependências Python ==="
pip3 install flask flask-cors paramiko schedule

echo "=== Clonando repositório (se necessário) ==="
if [ ! -d "/opt/Backup_rede" ]; then
    git clone https://github.com/WanderonRibas/Backup_rede.git /opt/Backup_rede
else
    echo "Repositório já existe em /opt/Backup_rede"
fi

echo "=== Configurando permissões ==="
chmod -R 755 /opt/Backup_rede

echo "=== Instalação concluída ==="
