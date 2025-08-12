<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');

if (!isset($_GET['ip_range'], $_GET['usuario'], $_GET['senha'], $_GET['porta'])) {
    echo "data: Parâmetros inválidos\n\n";
    flush();
    exit;
}

$ip_range = escapeshellarg($_GET['ip_range']);
$usuario = escapeshellarg($_GET['usuario']);
$senha = escapeshellarg($_GET['senha']);
$porta = intval($_GET['porta']);

$comando = "python3 cadastro_massa.py $ip_range $usuario $senha $porta";

$process = popen($comando, 'r');

if (!$process) {
    echo "data: Erro ao iniciar processo Python\n\n";
    flush();
    exit;
}

while (!feof($process)) {
    $linha = fgets($process);
    if ($linha !== false) {
        echo "data: " . trim($linha) . "\n\n";
        ob_flush();
        flush();
    }
}

pclose($process);
echo "data: --- FIM DO PROCESSO ---\n\n";
flush();
