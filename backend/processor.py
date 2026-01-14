import pandas as pd
import re

def converter_horas(valor):
    if pd.isna(valor) or valor == "": return 0.0
    s_val = str(valor).replace(',', '.').strip()
    if ':' in s_val:
        h, m = s_val.split(':')
        return float(h) + (float(m) / 100.0)
    return float(s_val)

def processar_projetos(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1')
    df.columns = [c.strip() for c in df.columns]
    
    # Conversão de horas
    for col in ['trab_prev', 'trab_apontado', 'sld_hrs']:
        df[col] = df[col].apply(converter_horas)
    
    # Regra de negócio (Gerente e Cod Resultado)
    def extrair_logica(row):
        cliente = str(row['cliente']).upper()
        tarefa = str(row['tarefa'])
        if cliente in ["CS-INTEGRA", "CSI SERVIÇOS"]:
            match = re.match(r'^(\d{3})-(\d{3})', tarefa)
            if match: return pd.Series([match.group(2), match.group(1)])
        return pd.Series([None, None])

    df[['gerente_tarefa', 'cod_resultado']] = df.apply(extrair_logica, axis=1)
    return df