import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega a variável de ambiente (do seu arquivo .env)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

print("--- Verificando Modelos Disponíveis ---")

if not API_KEY:
    print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env!")
else:
    try:
        # Configura a API
        genai.configure(api_key=API_KEY)

        print("Chave de API encontrada. Listando modelos que suportam 'generateContent':\n")

        found_models = False
        # Loop para listar os modelos
        for model in genai.list_models():
            # Verifica se o modelo pode "falar" (gerar conteúdo)
            if 'generateContent' in model.supported_generation_methods:
                print(f"Modelo encontrado: {model.name}")
                found_models = True

        if not found_models:
            print("Nenhum modelo com 'generateContent' foi encontrado para esta chave.")

    except Exception as e:
        print(f"Ocorreu um erro ao tentar conectar ou listar modelos: {e}")

print("\n--- Verificação Concluída ---")