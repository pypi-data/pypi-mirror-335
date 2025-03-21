import requests
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class MessageClient:
    def enviar_mensagem(self, numero, mensagem):
        raise NotImplementedError("Este método deve ser sobrescrito pelas subclasses")

class WhatsAppClient(MessageClient):
    def __init__(self, torre=False):
        if torre:
            self.url = os.getenv("ZAPI_MESSAGE_TORRE_URL")
        else:
            self.url = os.getenv("ZAPI_MESSAGE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": os.getenv("ZAPI_AUTHORIZATION"),
            "Client-Token": os.getenv("ZAPI_CLIENT_TOKEN")
        }

    def enviar_mensagem(self, numeros, mensagem, anexo=None, tipo_anexo=None):
        if not isinstance(numeros, list):
            numeros = [numeros]
        
        for numero in numeros:
            if anexo:
                payload = {
                    "phone": numero,
                    "caption": mensagem,
                    "viewOnce": False
                }
                if tipo_anexo == "imagem":
                    payload["image"] = anexo
                    url = f"{os.getenv('ZAPI_BASE_URL')}/send-image"
                elif tipo_anexo == "video":
                    payload["video"] = anexo
                    url = f"{os.getenv('ZAPI_BASE_URL')}/send-video"
                else:
                    raise ValueError("Tipo de anexo não suportado. Use 'imagem' ou 'video'.")
            else:
                payload = {
                    "phone": numero,
                    "message": mensagem
                }
                url = self.url
            
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                print("Mensagem enviada com sucesso para", numero)
            else:
                print("Ocorreu um erro ao enviar a mensagem para", numero)

    def criar_grupo(self, nome_grupo, telefones, imagem_perfil):
        url = os.getenv("ZAPI_CREATE_GROUP_URL")
        payload = {
            "groupName": nome_grupo,
            "phones": telefones,
            "profileImage": imagem_perfil
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
        else:
            print(response.json())

    def obter_metadata_convite_grupo(self, url_convite):
        url = os.getenv("ZAPI_REQUEST_GROUP_URL")
        querystring = {"URL": url_convite}
        response = requests.get(url, headers=self.headers, params=querystring)
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            return None
        else:
            return (response.json())

# Exemplo de uso da classe WhatsAppClient
if __name__ == "__main__":
    cliente_whatsapp = WhatsAppClient()
    # numeros = ["5548996547434", "5548988437126"]  # Lista de números de telefone dos destinatários
    # mensagem = "Teste de envio de mensagem via WhatsApp"
    # cliente_whatsapp.enviar_mensagem(numeros, mensagem)

    # Exemplo de uso do método criar_grupo
    # nome_grupo = "Meu grupo Z-API"
    # telefones = ["5548988437126", "5548996547434"]
    # imagem_perfil = ""
    # cliente_whatsapp.criar_grupo(nome_grupo, telefones, imagem_perfil)

    # # Exemplo de uso do método obter_metadata_convite_grupo
    # url_convite = "https://chat.whatsapp.com/GuC9aDSNTXt60TEufDBkg2"
    # id = cliente_whatsapp.obter_metadata_convite_grupo(url_convite)
    # print(id['phone'])