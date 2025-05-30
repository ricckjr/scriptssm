import requests
import re
import json
import sys
from connect_database import execute_mysql_query_with_params, write_data_to_mysql


def sanitize_numbers_only(value):
    return re.sub(r'\D', '', value)


def obter_token():
    url = "https://auth.somultas.com/realms/organ-query-realm/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "username": "flow_automacao",
        "password": "fvsiou490",
        "client_id": "apisissm",
        "client_secret": "JGoNtJZamflh8CbiCvc24P7dkxRcUHXE"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")


def obter_dados_cliente(cpf, token):
    url = f"https://api.somultas.com/clientes/{cpf}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    dados = response.json()
    if isinstance(dados, list) and len(dados) > 0:
        return dados[0]
    elif isinstance(dados, dict):
        return dados
    return None


def format_phone_number(phone_number):
    numbers_only = sanitize_numbers_only(phone_number)
    if len(numbers_only) == 11:
        return f"({numbers_only[:2]}) {numbers_only[2:6]}-{numbers_only[6:]}"
    elif len(numbers_only) == 10:
        return f"({numbers_only[:2]}) {numbers_only[2:6]}-{numbers_only[6:]}"
    return phone_number


def get_cliente_info(telefone):
    telefone_formatado = format_phone_number(telefone)
    telefone_limpio = sanitize_numbers_only(telefone)

    query = f"""
    SELECT cm.contador, cm.contador_wpp, cm.contador_twillo, c.data_cadastro 
    FROM tb_contador_mensagens cm 
    INNER JOIN tb_clientes c ON cm.telefone1 = c.telefone1 
    WHERE cm.telefone1 = '{telefone_formatado}' OR cm.telefone1 = '{telefone_limpio}'
    """
    db = 'sissm'
    cliente = execute_mysql_query_with_params(query, db)
    if cliente:
        return cliente[0][0], cliente[0][1], cliente[0][2], cliente[0][3].year
    return None, None, None, None


def check_sms_status(sms_enviadas, whats_app, twillo, data_cadastro):
    pass

def verifica_identificador(telefone):
    pass

def ultima_mensagem(identificador):
    pass


def validar_cliente(telefone):
    sms_enviadas, whats_app, twillo, data_cadastro = get_cliente_info(telefone)
    
    if sms_enviadas is None:
        return f"Cliente com telefone {telefone} não encontrado."
    
    if sms_enviadas > 1 and whats_app > 0 and twillo > 1:
        execute_mysql_query_with_params(
            f"UPDATE tb_clientes SET validado = 1 WHERE telefone1 = '{telefone}'", 'sissm'
        )
        return "Todas tentativas esgotadas. O número será validado!"
    elif sms_enviadas > 1 and whats_app > 0 and twillo < 2:
        return "Limite de tentativas de validação no site ainda não foi atingido. Enviar SMS.."
    elif sms_enviadas > 1 and whats_app == 0:
        return "Limite de tentativas de validação no site ainda não foi atingido. Enviar WhatsApp."
    elif sms_enviadas < 2 and data_cadastro >= 2025:
        return "Tentativas de validação no SisSM não esgotadas."
    elif sms_enviadas is not None and whats_app is not None:
        check_sms_status(sms_enviadas, whats_app, twillo, data_cadastro)
        if sms_enviadas >= 3 and whats_app == 1 or data_cadastro < 2025:
            status = verifica_identificador(telefone)
            if status and 'resource' in status and 'identity' in status['resource']:
                identificador = status['resource']['identity']
                mensagem = ultima_mensagem(identificador)
                if mensagem and len(mensagem['resource']['items']) == 0:
                    execute_mysql_query_with_params(
                        f"UPDATE tb_clientes SET validado = 1 WHERE telefone1 = '{telefone}'", 'sissm'
                    )
                    return "Mensagem não recebida, número será validado."
                else:
                    status_mensagem = mensagem['resource']['items'][0]['status']
                    if status_mensagem == 'received':
                        return "Mensagem recebida, mas sem confirmação de leitura."
                    elif status_mensagem == 'consumed':
                        return "Mensagem recebida e lida pelo cliente."
                    elif status_mensagem == 'failed':
                        execute_mysql_query_with_params(
                            f"UPDATE tb_clientes SET validado = 1 WHERE telefone1 = '{telefone}'", 'sissm'
                        )
                        return "Erro no envio, número será validado."
            else:
                return "Falha ao verificar o identificador."
    
    return "Validação não definida."


def main():
    if len(sys.argv) < 2:
        print("❌ CPF não fornecido.")
        return

    cpf_cliente = sys.argv[1]
    cpf_clean = sanitize_numbers_only(cpf_cliente)
    if len(cpf_clean) < 11:
        print("❌ CPF inválido.")
        return

    token = obter_token()
    cliente = obter_dados_cliente(cpf_clean, token)
    if not cliente:
        print("❌ Cliente não encontrado.")
        return

    print("✅ Cliente encontrado")

    telefone = cliente.get('telefone1')
    nome = cliente.get('nome')
    if not telefone or not nome:
        print("❌ Dados incompletos.")
        return

    telefone_formatado = format_phone_number(telefone)
    validacao_resultado = validar_cliente(telefone_formatado)

    print(f"👤 Cliente: {nome}")
    print(f"📞 Telefone: {telefone_formatado}")
    print(f"📄 Status Validação: {validacao_resultado}")


if __name__ == "__main__":
    main()
