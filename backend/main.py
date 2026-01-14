import scraper
import processor
import database
import os

def iniciar_fluxo_projetos():
    print("\n=== INICIANDO PROCESSO CS360: PROJETOS ===")
    
    # Passo 1: Garantir que o banco de dados tem a tabela pronta
    database.inicializar_banco()

    # Passo 2: Mandar o robô buscar o arquivo
    caminho_arquivo = scraper.extrair_relatorio("projetos")
    
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        print(f"[Main] Arquivo obtido: {caminho_arquivo}")
        
        # Passo 3: Limpar os dados e aplicar as regras (Gerente Tarefa / Horas)
        df_limpo = processor.processar_projetos(caminho_arquivo)
        
        # Passo 4: Salvar no Banco de Dados (Upsert)
        database.upsert_dados(df_limpo)
        
        print("=== PROCESSO CONCLUÍDO COM SUCESSO! ===")
    else:
        print("[Main] Falha: O robô não conseguiu baixar o relatório.")

if __name__ == "__main__":
    iniciar_fluxo_projetos()