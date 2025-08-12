import requests

def validar_chave(chave: str, servidor_url: str = "http://localhost:5000/validate") -> bool:
    try:
        response = requests.post(servidor_url, json={"key": chave}, timeout=5)
        if response.status_code == 200 and response.json().get("status") == "valid":
            print("✅ Chave válida. Acesso permitido.")
            return True
        else:
            print("❌ Chave inválida. Acesso negado.")
            return False
    except Exception as e:
        print(f"Erro na validação: {e}")
        return False
