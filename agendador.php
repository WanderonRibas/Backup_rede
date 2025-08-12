<?php
session_start();

if (!isset($_SESSION['usuario'])) {
    header('Location: index.php');
    exit;
}

// Configuração MySQL (se ainda for utilizada)
// ... seu código de conexão de banco de dados ...

// URL do novo endpoint da sua API Python
$url_api_agendador = 'http://localhost:5000/agendar-tarefa';
$msg_retorno = '';

// --- Lógica para processar o formulário ---
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $dias_semana_enviados = $_POST['dias_semana'] ?? [];
    $hora_execucao_enviada = $_POST['hora_execucao'] ?? '';

    // Prepara os dados para enviar à API no formato JSON
    $dados_para_api = [
        'dias_semana' => $dias_semana_enviados,
        'hora_execucao' => $hora_execucao_enviada
    ];
    
    // Inicia a requisição cURL para a API Python
    $ch = curl_init($url_api_agendador);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($dados_para_api));

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    // Verifica por erros no cURL e na resposta da API
    if (curl_errno($ch)) {
        $msg_retorno = 'Erro cURL: ' . curl_error($ch);
    } else {
        $dados_api = json_decode($response, true);
        if ($http_code == 200 && isset($dados_api['status']) && $dados_api['status'] === 'sucesso') {
            $msg_retorno = "Agendamento atualizado com sucesso! Mensagem: " . htmlspecialchars($dados_api['mensagem']);
        } else {
            $msg_retorno = "Erro ao agendar via API. HTTP Code: {$http_code}. Mensagem: " . htmlspecialchars($dados_api['mensagem'] ?? 'Resposta inesperada.');
        }
    }
    curl_close($ch);
}

// --- Lógica para ler o arquivo .ini e exibir na página ---
// Esta parte lê a configuração que a API Python salvou por último.
$arquivo_ini = 'python/agendador.ini';
$dias_semana_salvos = [];
$hora_execucao_salva = '';

if (file_exists($arquivo_ini)) {
    $config = parse_ini_file($arquivo_ini, true);
    if (isset($config['AGENDADOR'])) {
        $dias_semana_salvos = explode(',', $config['AGENDADOR']['dias_semana']);
        $hora_execucao_salva = $config['AGENDADOR']['hora_execucao'];
    }
}
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configurar Agendador</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
        h1 { text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="time"] { width: 100%; padding: 8px; box-sizing: border-box; border-radius: 4px; border: 1px solid #ccc; }
        .checkbox-group label { font-weight: normal; }
        .checkbox-group input { margin-right: 5px; }
        button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .agendamento-atual { background-color: #f0f0f0; padding: 10px; border-radius: 4px; margin-top: 20px; }
        .mensagem-retorno { padding: 10px; border-radius: 4px; margin-top: 10px; }
        .sucesso { background-color: #d4edda; color: #155724; }
        .erro { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Configurar Agendador de Tarefas</h1>

    <?php if (!empty($msg_retorno)): ?>
        <div class="mensagem-retorno <?php echo (strpos($msg_retorno, 'sucesso') !== false) ? 'sucesso' : 'erro'; ?>">
            <?php echo htmlspecialchars($msg_retorno); ?>
        </div>
    <?php endif; ?>

    <div class="agendamento-atual">
        <h2>Agendamento Atual</h2>
        <p><strong>Dias da Semana:</strong> <?php echo empty($dias_semana_salvos) ? 'Nenhum dia selecionado' : htmlspecialchars(implode(', ', $dias_semana_salvos)); ?></p>
        <p><strong>Hora de Execução:</strong> <?php echo empty($hora_execucao_salva) ? 'Nenhuma hora definida' : htmlspecialchars($hora_execucao_salva); ?></p>
    </div>

    <form action="agendador.php" method="POST">
        <h3>Definir Novo Agendamento</h3>
        <div class="form-group">
            <label for="dias_semana">Dias da Semana:</label>
            <div class="checkbox-group">
                <input type="checkbox" id="segunda" name="dias_semana[]" value="segunda" <?php echo in_array('segunda', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="segunda">Segunda-feira</label>
                <input type="checkbox" id="terca" name="dias_semana[]" value="terca" <?php echo in_array('terca', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="terca">Terça-feira</label>
                <input type="checkbox" id="quarta" name="dias_semana[]" value="quarta" <?php echo in_array('quarta', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="quarta">Quarta-feira</label>
                <input type="checkbox" id="quinta" name="dias_semana[]" value="quinta" <?php echo in_array('quinta', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="quinta">Quinta-feira</label>
                <input type="checkbox" id="sexta" name="dias_semana[]" value="sexta" <?php echo in_array('sexta', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="sexta">Sexta-feira</label>
                <input type="checkbox" id="sabado" name="dias_semana[]" value="sabado" <?php echo in_array('sabado', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="sabado">Sábado</label>
                <input type="checkbox" id="domingo" name="dias_semana[]" value="domingo" <?php echo in_array('domingo', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="domingo">Domingo</label>
                <input type="checkbox" id="todos" name="dias_semana[]" value="todos" <?php echo in_array('todos', $dias_semana_salvos) ? 'checked' : ''; ?>><label for="todos">Todos os dias</label>
            </div>
        </div>
        
        <div class="form-group">
            <label for="hora_execucao">Hora de Execução:</label>
            <input type="time" id="hora_execucao" name="hora_execucao" value="<?php echo htmlspecialchars($hora_execucao_salva); ?>" required>
        </div>
        
        <button type="submit">Salvar Configurações</button>
    </form>
    
    <div style="text-align: center; margin-top: 20px;">
        <a href="painel.php">
            <button>Voltar para o Painel</button>
        </a>
    </div>
</body>
</html>