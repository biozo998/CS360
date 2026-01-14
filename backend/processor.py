import pandas as pd
import re
import os

def converter_horas_centesimais(valor):
    """
    Transforma '36:75' em 36.75 (float).
    Essencial para podermos fazer somas no Dashboard.
    """
    if pd.isna(valor) or valor == "":
        return 0.0
    
    # Limpa o valor (remove espaços e garante ponto como decimal)
    s_val = str(valor).replace(',', '.').strip()
    
    if ':' in s_val:
        partes = s_val.split(':')
        # h:m -> h + (m/100). Ex: 36:75 -> 36 + 0.75 = 36.75
        try:
            return float(partes[0]) + (float(partes[1]) / 100.0)
        except:
            return 0.0
    
    try:
        return float(s_val)
    except:
        return 0.0

def processar_projetos(caminho_arquivo):
    """
    Lê o CSV, renomeia colunas, trata horas e cria as colunas CS360.
    """
    print(f"[Processor] Lendo arquivo: {caminho_arquivo}")
    
    # O PSOffice costuma exportar em latin-1
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1')
    except:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')

    # 1. Limpeza de cabeçalhos
    df.columns = [c.strip() for c in df.columns]

    # 2. Mapa de Nomes (Garante que o banco entenda as colunas)
    mapa_nomes = {
        'gerente': 'gerente',
        'cliente': 'cliente',
        'id_proj': 'id_proj',
        'Projeto': 'projeto',
        'centro_resultado': 'centro_resultado',
        'TP_Proj': 'tp_proj',
        'id_tarefa': 'id_tarefa',
        'tarefa': 'tarefa',
        'responsavel': 'responsavel',
        'dt_inicio': 'dt_inicio',
        'dt_fim': 'dt_fim',
        'trab_prev': 'trab_prev',
        'trab_apontado': 'trab_apontado',
        'sld_hrs': 'sld_hrs'
    }
    df = df.rename(columns=mapa_nomes)

    # 3. Tratamento de Horas Decimais
    for col in ['trab_prev', 'trab_apontado', 'sld_hrs']:
        if col in df.columns:
            df[col] = df[col].apply(converter_horas_centesimais)

    # 4. Tratamento de Datas
    df['dt_inicio'] = pd.to_datetime(df['dt_inicio'], dayfirst=True).dt.date
    df['dt_fim'] = pd.to_datetime(df['dt_fim'], dayfirst=True).dt.date

    # 5. Regras de Negócio CS360 (gerente_tarefa e cod_resultado)
    def extrair_logica(row):
        cliente = str(row['cliente']).upper()
        tarefa = str(row['tarefa'])
        centro_res = str(row['centro_resultado'])
        
        g_tarefa, c_resultado = None, None

        # Regra para clientes CS-INTEGRA ou CSI SERVIÇOS
        if cliente in ["CS-INTEGRA", "CSI SERVIÇOS"]:
            match = re.match(r'^(\d{3})-(\d{3})', tarefa)
            if match:
                c_resultado = match.group(1) # 062
                g_tarefa = match.group(2)    # 033
        else:
            # Demais clientes
            match_t = re.match(r'^(\d{3})', tarefa)
            g_tarefa = match_t.group(1) if match_t else None
            
            match_cr = re.match(r'^(\d{3})', centro_res)
            c_resultado = match_cr.group(1) if match_cr else None
            
        return pd.Series([g_tarefa, c_resultado])

    df[['gerente_tarefa', 'cod_resultado']] = df.apply(extrair_logica, axis=1)

    print(f"[Processor] Limpeza concluída. {len(df)} linhas processadas.")
    return df