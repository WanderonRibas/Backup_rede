<?php
session_start();
// Define o fuso horário para São Paulo
date_default_timezone_set('America/Sao_Paulo');

if (!isset($_SESSION['usuario'])) {
    header('Location: index.php');
    exit;
}

// Configuração do diretório de backups
$backupDir = __DIR__ . '/python/backups';

// Garantir que o diretório existe
if (!is_dir($backupDir)) {
    mkdir($backupDir, 0777, true);
}

// Função para listar arquivos
function listarArquivos($dir) {
    $arquivos = array_diff(scandir($dir), ['.', '..']);
    return array_filter($arquivos, function($arquivo) use ($dir) {
        return is_file($dir . '/' . $arquivo);
    });
}

// Ações: visualizar, download e excluir
if (isset($_GET['action']) && isset($_GET['file'])) {
    $arquivo = basename($_GET['file']); // evita path traversal
    $caminho = $backupDir . '/' . $arquivo;

    if (!file_exists($caminho)) {
        die("Arquivo não encontrado!");
    }

    switch ($_GET['action']) {
        case 'view':
            header('Content-Type: text/plain');
            readfile($caminho);
            exit;

        case 'download':
            header('Content-Description: File Transfer');
            header('Content-Type: application/octet-stream');
            header('Content-Disposition: attachment; filename="' . $arquivo . '"');
            header('Content-Length: ' . filesize($caminho));
            readfile($caminho);
            exit;

        case 'delete':
            unlink($caminho);
            header("Location: gerenciar_backups.php?msg=Arquivo%20excluido%20com%20sucesso");
            exit;
    }
}

// Listar arquivos do diretório
$arquivos = listarArquivos($backupDir);
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gerenciador de Backups</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: center; background: white; }
        th { background: #eee; }
        a { text-decoration: none; color: blue; margin: 0 5px; }
        .msg { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <a href="painel.php" class="btn btn-blue" style="margin: 10px 0; display: inline-block;">← Voltar</a>

    <h1>📂 Gerenciador de Backups</h1>

    <?php if (isset($_GET['msg'])): ?>
        <p class="msg"><?= htmlspecialchars($_GET['msg']) ?></p>
    <?php endif; ?>

    <?php if (empty($arquivos)): ?>
        <p>Nenhum arquivo de backup encontrado.</p>
    <?php else: ?>
        <table>
            <tr>
                <th>Arquivo</th>
                <th>Tamanho</th>
                <th>Modificado em</th>
                <th>Ações</th>
            </tr>
            <?php foreach ($arquivos as $arquivo): 
                $caminho = $backupDir . '/' . $arquivo; ?>
                <tr>
                    <td><?= htmlspecialchars($arquivo) ?></td>
                    <td><?= round(filesize($caminho) / 1024, 2) ?> KB</td>
                    <td><?= date('d/m/Y H:i:s', filemtime($caminho)) ?></td>
                    <td>
                        <a href="?action=view&file=<?= urlencode($arquivo) ?>" target="_blank">👁 Ver</a> |
                        <a href="?action=download&file=<?= urlencode($arquivo) ?>">⬇ Baixar</a> |
                        <a href="?action=delete&file=<?= urlencode($arquivo) ?>" onclick="return confirm('Deseja realmente excluir este arquivo?')">🗑 Excluir</a>
                    </td>
                </tr>
            <?php endforeach; ?>
        </table>
    <?php endif; ?>
</body>
</html>
