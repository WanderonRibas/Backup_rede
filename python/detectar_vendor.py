# detectar_vendor.py
import paramiko
import time

def detectar_vendor(host, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, timeout=10)

        shell = client.invoke_shell()
        time.sleep(1)

        # Captura inicial
        if shell.recv_ready():
            shell.recv(4096)

        def enviar_comando(comando, delay=1.5):
            shell.send(comando + '\n')
            time.sleep(delay)
            output = ""
            while shell.recv_ready():
                output += shell.recv(4096).decode('utf-8', errors='ignore').lower()
            return output

        # Mikrotik
        output = enviar_comando("/system resource print")
        if "mikrotik" in output:
            client.close()
            return "mikrotik"

        # Huawei
        output = enviar_comando("display version")
        if "huawei" in output or "vrp" in output:
            client.close()
            return "huawei"

        # Cisco IOS
        output = enviar_comando("show version")
        if "cisco ios" in output or "cisco" in output:
            client.close()
            return "cisco_ios"

        # Ubiquiti
        output = enviar_comando("cat /proc/cpuinfo")
        if "ases implemented" in output or "tlb_entries" in output:
            client.close()
            return "ubiquit"

        # V-SOL tentativa
        shell.send("enable\n")
        time.sleep(2)
        shell.send(password + '\n')
        time.sleep(2)
        shell.send("configure terminal\n")
        time.sleep(2)
        shell.send("show version\n")
        time.sleep(2)

        output = ""
        while shell.recv_ready():
            output += shell.recv(4096).decode('utf-8', errors='ignore').lower()

        shell.close()
        client.close()

        if "gpon" in output or "epon" in output:
            return "vsol"

        return "desconhecido"

    except Exception:
        return "erro"
