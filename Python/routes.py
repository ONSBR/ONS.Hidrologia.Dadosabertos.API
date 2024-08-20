from flask import Blueprint, jsonify, request
from services import gerar_resposta_operacional, gerar_resposta_operacional_grandeza, carregar_dados_reservatorios
from utils import tipo_dado_map, tipo_grandeza_map

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/hidrologia/reservatorios', methods=['GET'])
def listar_reservatorios():
    reservatorios = carregar_dados_reservatorios()
    return jsonify({
        "PaginaCorrente": 1,
        "QuantidadeTotalItens": len(reservatorios),
        "Resultados": reservatorios
    })


@api_blueprint.route('/hidrologia/reservatorios/<string:identificador>', methods=['GET'])
def obter_reservatorio(identificador):
    reservatorios = carregar_dados_reservatorios()

    for reservatorio in reservatorios:
        if reservatorio["Identificador"] == identificador:
            resposta = {
                "PaginaCorrente": 1,
                "QuantidadeTotalItens": 1,
                "Resultados": [reservatorio]
            }
            return jsonify(resposta)

    return jsonify({"mensagem": "Reservatório não encontrado"}), 404

@api_blueprint.route('/hidrologia/GrandezasHidrologicas', methods=['GET'])
def obter_dados_operacionais_grandezas():
    DataInicialMedicao = request.args.get('DataInicialMedicao')
    DataFinalMedicao = request.args.get('DataFinalMedicao')
    IDPostoReservatorio = request.args.getlist('IDPostoReservatorio')
    Grandeza = request.args.get('Grandeza')

    if Grandeza not in tipo_grandeza_map:
        return jsonify({"mensagem": "Grandeza inválida"}), 400

    return gerar_resposta_operacional_grandeza(IDPostoReservatorio, Grandeza, DataInicialMedicao, DataFinalMedicao)

@api_blueprint.route('/hidrologia/reservatorios/<string:identificador>/<string:tipo_dado>', methods=['GET'])
def obter_dados_operacionais(identificador, tipo_dado):
    if tipo_dado not in tipo_dado_map:
        return jsonify({"mensagem": "Grandeza inválida"}), 400

    inicio = request.args.get('Inicio')
    fim = request.args.get('Fim')
    intervalo = request.args.get('Intervalo')

    return gerar_resposta_operacional(identificador, tipo_dado, inicio, fim, intervalo)