from datetime import datetime

cache = {}

tipo_grandeza_map = {
    "NIV": "val_nivelmontante",
    "NIJ": "val_niveljusante",
    "VUT": "val_volumeutilcon",
    "AFL": "val_vazaoafluente",
    "TUR": "val_vazaoturbinada",
    "VER": "val_vazaovertida",
    "VOE": "val_vazaooutrasestruturas",
    "DFL": "val_vazaodefluente",
    "VTR": "val_vazaotransferida",
    "VNA": "val_vazaonatural",
    "VAR": "val_vazaoartificial",
    "VNM": "val_vazaoincremental",
    "VEL": "val_vazaoevaporacaoliquida",
    "VUC": "val_vazaousoconsuntivo"
}

tipo_dado_map = {
    "afluencia": "val_vazaoafluente",
    "defluencia": "val_vazaodefluente",
    "energiaTurbinavel": "val_vazaoturbinada",
    "nivelJusante": "val_niveljusante",
    "nivelMontante": "val_nivelmontante",
    "vazaoOutrasEstruturas": "val_vazaooutrasestruturas",
    "vazaoTurbinada": "val_vazaoturbinada",
    "vazaoVertida": "val_vazaovertida",
    "volumeUtil": "val_volumeutil"
}

def parse_data_Intervalo(dado, intervalo):
    formato = '%Y-%m-%d %H:%M:%S' if intervalo == 'HO' else '%Y-%m-%d'
    return datetime.strptime(dado["din_instante"], formato)
