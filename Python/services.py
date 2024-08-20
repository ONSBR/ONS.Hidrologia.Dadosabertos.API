import csv
from flask import jsonify
import requests
from datetime import datetime, timedelta
from utils import cache, tipo_dado_map, tipo_grandeza_map, parse_data_Intervalo
from config import URLS

def baixar_csv(Intervalo, ano, mes, expiracao_minutos=10):
    """Baixa o arquivo CSV de uma URL, usando cache com expiração individual."""
    #url = URLS.get(Intervalo, URLS[Intervalo]).format(ano=ano, mes=mes)
    url = URLS.get(Intervalo, URLS['CADASTRO']).format(ano=ano, mes=mes)

    # Verifica se a URL está no cache e se a entrada ainda é válida
    if url in cache:
        cache_entry = cache[url]
        if datetime.now() < cache_entry['expiracao']:
            # Retorna o conteúdo do cache se ainda não expirou
            return cache_entry['conteudo']
    
    # Se o cache não for válido ou a URL não estiver no cache, baixa o arquivo
    response = requests.get(url)
    
    if response.status_code == 200:
        # Decodifica o conteúdo do CSV
        csv_data = response.content.decode('utf-8')
        
        # Converte o conteúdo CSV para uma lista de dicionários
        linhas = csv_data.splitlines()
        reader = csv.DictReader(linhas, delimiter=';')

        conteudo = [linha for linha in reader]
        
        # Armazena no cache com tempo de expiração individual
        cache[url] = {
            'conteudo': conteudo,
            'expiracao': datetime.now() + timedelta(minutes=expiracao_minutos)
        }
        
        return conteudo
    else:
        raise Exception(f"Erro ao baixar o arquivo dos Dados Abertod do ONS: {response.status_code}")

def carregar_dados_reservatorios():
    reservatorios = []
    dados_reservatorios = baixar_csv("CADASTRO", 0, 0)
    for row in dados_reservatorios:
        reservatorios.append({
            "Identificador": row["id_reservatorio"],
            "NomeCurto": row["nom_reservatorio"]
        })
    return reservatorios

def gerar_resposta_operacional(identificador, tipo_dado, inicio=None, fim=None, intervalo=None):
    reservatorios = carregar_dados_reservatorios()
    ano, mes = None, None

    # Encontrar o reservatório
    reservatorio_encontrado = None
    for reservatorio in reservatorios:
        if reservatorio["Identificador"] == identificador:
            reservatorio_encontrado = reservatorio
            break
    
    if not reservatorio_encontrado:
        return jsonify({"mensagem": "Reservatório não encontrado"}), 404

    # Validação dos parâmetros de data 'Inicio' e 'Fim'
    if inicio:
        try:
            inicio_data = datetime.strptime(inicio, '%Y-%m-%dT%H:%M:%S')
            ano = inicio_data.year
            mes = f"{inicio_data.month:02d}"  # Garantir que o mês esteja no formato MM
        except ValueError:
            return jsonify({"mensagem": "Formato de data inválido no parâmetro 'Inicio'. Use o formato '%Y-%m-%dT%H:%M:%S'."}), 400

    if fim:
        try:
            fim_data = datetime.strptime(fim, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({"mensagem": "Formato de data inválido no parâmetro 'Fim'. Use o formato '%Y-%m-%dT%H:%M:%S'."}), 400
        
    dados_operacionais = baixar_csv(intervalo, ano, mes)
    # Filtragem e processamento dos dados
    resultados = [
        {
            "Instante": parse_data_Intervalo(dado, intervalo).strftime('%d/%m/%Y %H:%M:%S'),
            "Valor": float(dado.get(tipo_dado_map.get(tipo_dado))) if dado.get(tipo_dado_map.get(tipo_dado)) is not None else 0
        }
        for dado in dados_operacionais
        if dado["id_reservatorio"] == identificador
        and (parse_data_Intervalo(dado, intervalo) >= inicio_data)
        and (parse_data_Intervalo(dado, intervalo) <= fim_data)
    ]

    resposta = {
        "PaginaCorrente": 1,
        "QuantidadeTotalItens": len(resultados),
        "Reservatorio": identificador,
        "Resultados": resultados
    }

    return jsonify(resposta)

def gerar_resposta_operacional_grandeza(identificadores, tipo_dado, inicio=None, fim=None):
    reservatorios = carregar_dados_reservatorios()
    ano, mes = None, None

    # Encontrar o reservatório
    reservatorios_encontrados = 0
    for reservatorio in reservatorios:
        if reservatorio["Identificador"] in identificadores:
            reservatorios_encontrados += 1
    
    if not reservatorios_encontrados == len(identificadores):
        return jsonify({"mensagem": "Reservatório não encontrado"}), 404

    # Validação dos parâmetros de data 'Inicio' e 'Fim'
    if inicio:
        try:
            data_obj = datetime.strptime(inicio, "%d/%m/%Y")
            data_formatada = data_obj.strftime("%Y-%m-%dT%H:%M:%S")
            inicio_data = datetime.strptime(data_formatada, '%Y-%m-%dT%H:%M:%S')
            ano = inicio_data.year
            mes = f"{inicio_data.month:02d}"  # Garantir que o mês esteja no formato MM
        except ValueError:
            return jsonify({"mensagem": "Formato de data inválido no parâmetro 'Inicio'. Use o formato '%Y-%m-%dT%H:%M:%S'."}), 400

    if fim:
        try:
            data_obj = datetime.strptime(fim, "%d/%m/%Y")
            data_formatada = data_obj.strftime("%Y-%m-%dT%H:%M:%S")
            fim_data = datetime.strptime(data_formatada, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({"mensagem": "Formato de data inválido no parâmetro 'Fim'. Use o formato '%Y-%m-%dT%H:%M:%S'."}), 400
        
    dados_operacionais = baixar_csv('DI', ano, mes)

    # Filtrando e processando os dados operacionais
    resultados = [
        {
            "Identificador": dado["id_reservatorio"],
            "DataHoraMedicao": datetime.strptime(dado["din_instante"], '%Y-%m-%d').strftime('%d/%m/%Y %H:%M:%S'),
            "ValorMedicao": float(dado[tipo_grandeza_map.get(tipo_dado)]) if dado.get(tipo_grandeza_map.get(tipo_dado)) else None,
            "StatusMedicao": "COO"
        }
        for dado in dados_operacionais
        if dado["id_reservatorio"] in identificadores
        and inicio_data <= datetime.strptime(dado["din_instante"], '%Y-%m-%d') <= fim_data
    ]
 
    resposta = {
        "Pagina": 1,
        "Quantidade": len(resultados),
        "Resultados": sorted(resultados, key=lambda x: (x["Identificador"]))
    }

    return jsonify(resposta)