<?php
session_start();

// Detalhes da conexão com o MySQL
// ATENÇÃO: Substitua 'localhost', 'nome_do_seu_banco', 'seu_usuario_mysql' e 'sua_senha_mysql'
// com as suas informações de banco de dados reais.
$host = 'localhost';          // Geralmente 'localhost' se o banco estiver no mesmo servidor
$dbname = 'net_backup';      // O nome do seu banco de dados MySQL
$username = 'root';          // O nome de usuário para acessar o MySQL
$password = 'Master@308882#'; // A senha do seu usuário MySQL

try {
    // Conexão PDO para MySQL
    $db = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    
    // Define o modo de erro do PDO para lançar exceções em caso de problemas
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Define o modo de busca padrão para associativo (nomes das colunas como chaves)
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

} catch (PDOException $e) {
    // Em caso de erro na conexão, exibe uma mensagem e encerra o script
    die("Erro de conexão com o banco de dados: " . $e->getMessage());
}

if (isset($_POST['login'])) {
    $logon = $_POST['logon'];
    $senha_digitada = $_POST['senha']; // A senha digitada pelo usuário (ainda em texto puro)

    // Busca o usuário no banco de dados
    $stmt = $db->prepare("SELECT * FROM usuarios WHERE login = ?");
    $stmt->execute([$logon]);
    $usuario = $stmt->fetch();

    if ($usuario) {
        // --- Lógica para "primeiro login sem senha" com 'senha_pendente' ---
        // Se a coluna 'senha_pendente' existe e está definida como TRUE,
        // significa que o usuário precisa definir uma senha.
        // Neste caso, não verificamos a senha com password_verify() ainda,
        // apenas confirmamos o login e redirecionamos para a tela de alteração.
        if (isset($usuario['senha_pendente']) && $usuario['senha_pendente'] === 1) { // MySQL armazena BOOLEAN como 0 ou 1
            $_SESSION['usuario'] = $usuario['login'];
            header('Location: alterar_senha.php'); // Redireciona para a página de alteração de senha
            exit;
        } 
        // --- Lógica de login normal para usuários com senha já definida ---
        // Usa password_verify() para comparar a senha digitada com o hash armazenado.
        // ESSA É A PARTE MAIS IMPORTANTE PARA A SEGURANÇA.
        elseif (password_verify($senha_digitada, $usuario['senha'])) {
            $_SESSION['usuario'] = $usuario['login'];
            header('Location: painel.php'); // Redireciona para o painel principal
            exit;
        } else {
            // Senha incorreta
            $erro = "Usuário ou senha inválidos!";
        }
    } else {
        // Usuário não encontrado
        $erro = "Usuário ou senha inválidos!";
    }
}
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="static/style.css">
</head>
<body>

<div class="container">
    <h2>Login</h2>

    <?php if (isset($erro)) { echo "<div class='alert'>$erro</div>"; } ?>

    <form action="" method="POST">
        <div class="mb-3">
            <label for="logon">Usuário:</label>
            <input type="text" id="logon" name="logon" class="form-control" required>
        </div>
        <div class="mb-3">
            <label for="senha">Senha:</label>
            <input type="password" id="senha" name="senha" class="form-control">
        </div>
        <button type="submit" name="login" class="btn">Entrar</button>
    </form>
</div>

</body>
</html>