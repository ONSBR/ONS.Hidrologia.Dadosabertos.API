CACHE_EXPIRATION = 10  # Minutos
BASE_URL = "https://ons-aws-prod-opendata.s3.amazonaws.com/dataset"
URLS = {
    'HO': f"{BASE_URL}/dados_hidrologicos_ho/DADOS_HIDROLOGICOS_HO_{{ano}}_{{mes}}.csv",
    'DI': f"{BASE_URL}/dados_hidrologicos_di/DADOS_HIDROLOGICOS_RES_{{ano}}.csv",
    'CADASTRO': f"{BASE_URL}/reservatorio/RESERVATORIOS.csv"
}
