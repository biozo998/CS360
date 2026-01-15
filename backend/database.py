from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Conecta ao banco usando a URL do .env
engine = create_engine(os.getenv("DATABASE_URL"))

def inicializar_banco():
    print("[Database] Verificando e criando tabelas...")
    try:
        with engine.begin() as conn:
            # 1. Tabela de Projetos
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS lancamentos_projeto (
                    id_tarefa INTEGER PRIMARY KEY,
                    gerente VARCHAR(255),
                    cliente VARCHAR(255),
                    id_proj INTEGER,
                    projeto VARCHAR(255),
                    centro_resultado VARCHAR(255),
                    tp_proj VARCHAR(50),
                    tarefa TEXT,
                    responsavel VARCHAR(255),
                    dt_inicio DATE,
                    dt_fim DATE,
                    trab_prev DECIMAL(10,2),
                    trab_apontado DECIMAL(10,2),
                    sld_hrs DECIMAL(10,2),
                    gerente_tarefa VARCHAR(50),
                    cod_resultado VARCHAR(50),
                    ativo BOOLEAN DEFAULT TRUE,
                    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # 2. Tabela de Cadastro de Gerentes
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cad_gerentes (
                    codigo VARCHAR(3) PRIMARY KEY,
                    nome VARCHAR(255),
                    area VARCHAR(100)
                );
            """))

            # 3. Tabela de Cadastro de Atividades
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cad_atividades (
                    codigo VARCHAR(3) PRIMARY KEY,
                    tipo_hora VARCHAR(20),
                    descricao TEXT,
                    estrategia VARCHAR(50)
                );
            """))
        print("[Database] Todas as tabelas foram inicializadas com sucesso.")
    except Exception as e:
        print(f"[Database] Erro ao inicializar banco: {e}")
        
def upsert_dados(df):
    """Executa a lógica de Inserir ou Atualizar (Upsert)."""
    with engine.begin() as conn:
        # Marca todos como inativos antes de processar o novo arquivo
        conn.execute(text("UPDATE lancamentos_projeto SET ativo = FALSE"))

        for _, row in df.iterrows():
            query = text("""
                INSERT INTO lancamentos_projeto (
                    id_tarefa, gerente, cliente, id_proj, projeto, centro_resultado, 
                    tp_proj, tarefa, responsavel, dt_inicio, dt_fim, 
                    trab_prev, trab_apontado, sld_hrs, gerente_tarefa, cod_resultado, ativo
                ) VALUES (
                    :id_tarefa, :gerente, :cliente, :id_proj, :projeto, :centro_resultado, 
                    :tp_proj, :tarefa, :responsavel, :dt_inicio, :dt_fim, 
                    :trab_prev, :trab_apontado, :sld_hrs, :gerente_tarefa, :cod_resultado, TRUE
                )
                ON CONFLICT (id_tarefa) DO UPDATE SET
                    trab_apontado = EXCLUDED.trab_apontado,
                    sld_hrs = EXCLUDED.sld_hrs,
                    ativo = TRUE,
                    ultima_atualizacao = CURRENT_TIMESTAMP;
            """)
            conn.execute(query, row.to_dict())
    print(f"[Database] Upsert de {len(df)} registros concluído.")