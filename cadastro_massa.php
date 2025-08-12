<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Cadastro em Massa de Dispositivos</title>
    <style>
        body { font-family: Arial, sans-serif; }
        #output { 
            background: #111; color: #0f0; padding: 10px; 
            height: 400px; overflow-y: scroll; white-space: pre-wrap;
            border-radius: 5px; margin-top: 20px;
        }
    </style>
</head>
<body>
<h2>Cadastro em Massa de Dispositivos</h2>
<a href="painel.php" class="btn btn-blue" style="margin: 10px 0; display: inline-block;">← Voltar</a>

<form id="cadastroForm">
    <label>Range de IPs (ex: 192.168.1.1-192.168.1.50):</label><br>
    <input type="text" name="ip_range" required><br><br>

    <label>Usuário SSH:</label><br>
    <input type="text" name="usuario" required><br><br>

    <label>Senha SSH:</label><br>
    <input type="password" name="senha" required><br><br>

    <label>Porta SSH:</label><br>
    <input type="number" name="porta" value="22" required><br><br>

    <button type="submit">Executar Cadastro</button>
</form>

<div id="output"></div>

<script>
document.getElementById('cadastroForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const params = new URLSearchParams(formData);

    const output = document.getElementById('output');
    output.textContent = "Iniciando cadastro em massa...\n";

    const eventSource = new EventSource('executar_cadastro.php?' + params.toString());

    eventSource.onmessage = function(event) {
        output.textContent += event.data + "\n";
        output.scrollTop = output.scrollHeight;
    };

    eventSource.onerror = function() {
        output.textContent += "\nProcesso finalizado ou ocorreu um erro.\n";
        eventSource.close();
    };
});
</script>
</body>
</html>
