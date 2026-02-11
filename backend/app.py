from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import processor
import scraper
from sqlalchemy import text
import main

app = Flask(__name__)
# O CORS(app) resolve o erro que você viu na imagem
CORS(app) 

# Garante que as tabelas (inclusive as novas de cadastro) sejam criadas ao iniciar
database.inicializar_banco()

# --- NOVOS ENDPOINTS DO DASHBOARD ---

@app.route('/api/dashboard/kpis', methods=['GET'])
def get_dashboard_kpis():
    """Retorna os principais KPIs para os cards do dashboard."""
    with database.engine.connect() as conn:
        # Contagem de projetos ativos (DISTINCT)
        q_proj_ativos = text("SELECT COUNT(DISTINCT id_proj) FROM lancamentos_projeto WHERE ativo = TRUE")
        projetos_ativos = conn.execute(q_proj_ativos).scalar()

        # Contagem de projetos com data fim atrasada (DISTINCT)
        q_proj_atrasados = text("SELECT COUNT(DISTINCT id_proj) FROM lancamentos_projeto WHERE ativo = TRUE AND dt_fim < CURRENT_DATE")
        projetos_atrasados = conn.execute(q_proj_atrasados).scalar()

        # Contagem de projetos com data fim em dia (DISTINCT)
        q_proj_em_dia = text("SELECT COUNT(DISTINCT id_proj) FROM lancamentos_projeto WHERE ativo = TRUE AND dt_fim >= CURRENT_DATE")
        projetos_em_dia = conn.execute(q_proj_em_dia).scalar()
        
        return jsonify({
            "projetos_ativos": projetos_ativos,
            "projetos_atrasados": projetos_atrasados,
            "projetos_em_dia": projetos_em_dia
        })

@app.route('/api/dashboard/horas-por-area', methods=['GET'])
def get_horas_por_area():
    """Retorna a soma de horas apontadas agrupadas por área do gerente."""
    query = text("""
        SELECT 
            COALESCE(g.area, 'Sem Área') as area, 
            SUM(l.trab_apontado) as horas
        FROM lancamentos_projeto l
        LEFT JOIN cad_gerentes g ON l.gerente_tarefa = g.codigo
        WHERE l.ativo = TRUE AND l.trab_apontado > 0
        GROUP BY g.area
        ORDER BY horas DESC
    """)
    with database.engine.connect() as conn:
        result = conn.execute(query)
        data = [{"area": r[0], "horas": float(r[1])} for r in result]
    return jsonify(data)

# --- ENDPOINTS DE EXPORTAÇÃO PARA EXCEL ---

@app.route('/api/export/projetos', methods=['GET'])
def export_projetos_ativos():
    """Retorna a lista detalhada de projetos ativos distintos."""
    query = text("""
        SELECT DISTINCT id_proj, projeto, cliente, dt_inicio, dt_fim
        FROM lancamentos_projeto
        WHERE ativo = TRUE
        ORDER BY projeto
    """)
    with database.engine.connect() as conn:
        res = conn.execute(query)
        return jsonify([dict(r._mapping) for r in res])

@app.route('/api/export/projetos-por-status', methods=['GET'])
def export_projetos_por_status():
    """Retorna projetos filtrando por status: 'atrasado' ou 'em_dia'."""
    status = request.args.get('status', 'atrasado').lower()
    
    if status == 'atrasado':
        filter_cond = "dt_fim < CURRENT_DATE"
    else:
        filter_cond = "dt_fim >= CURRENT_DATE"

    query = text(f"""
        SELECT DISTINCT id_proj, projeto, cliente, dt_inicio, dt_fim
        FROM lancamentos_projeto
        WHERE ativo = TRUE AND {filter_cond}
        ORDER BY dt_fim
    """)
    with database.engine.connect() as conn:
        res = conn.execute(query)
        return jsonify([dict(r._mapping) for r in res])

@app.route('/api/export/horas-por-area-detalhado', methods=['GET'])
def export_horas_por_area_detalhado():
    """Retorna todos os lançamentos que compõem o gráfico de horas por área."""
    query = text("""
        SELECT 
            g.area,
            l.projeto,
            l.tarefa,
            l.trab_apontado,
            g.nome as nome_gerente
        FROM lancamentos_projeto l
        LEFT JOIN cad_gerentes g ON l.gerente_tarefa = g.codigo
        WHERE l.ativo = TRUE AND l.trab_apontado > 0
        ORDER BY g.area, l.projeto
    """)
    with database.engine.connect() as conn:
        res = conn.execute(query)
        # Converte o resultado para um formato JSON amigável
        data = [
            {
                "area": r.area,
                "projeto": r.projeto,
                "tarefa": r.tarefa,
                "horas_apontadas": float(r.trab_apontado),
                "gerente": r.nome_gerente
            } for r in res
        ]
        return jsonify(data)


# --- ENDPOINTS DE CADASTRO (CRUD) ---

@app.route('/api/cadastros/gerentes', methods=['GET', 'POST'])
def gerenciar_gerentes():
    if request.method == 'POST':
        dados = request.json
        query = text("""
            INSERT INTO cad_gerentes (codigo, nome, area) 
            VALUES (:codigo, :nome, :area)
            ON CONFLICT (codigo) DO UPDATE SET nome = :nome, area = :area
        """)
        with database.engine.begin() as conn:
            conn.execute(query, dados)
        return jsonify({"status": "sucesso"})
    
    with database.engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM cad_gerentes ORDER BY codigo"))
        return jsonify([dict(r._mapping) for r in res])

@app.route('/api/cadastros/gerentes/<codigo>', methods=['DELETE'])
def excluir_gerente(codigo):
    query = text("DELETE FROM cad_gerentes WHERE codigo = :codigo")
    with database.engine.begin() as conn:
        conn.execute(query, {"codigo": codigo})
    return jsonify({"status": "sucesso"})

@app.route('/api/cadastros/atividades', methods=['GET', 'POST'])
def gerenciar_atividades():
    if request.method == 'POST':
        dados = request.json
        query = text("""
            INSERT INTO cad_atividades (codigo, tipo_hora, descricao, estrategia)
            VALUES (:codigo, :tipo_hora, :descricao, :estrategia)
            ON CONFLICT (codigo) DO UPDATE 
            SET tipo_hora = :tipo_hora, descricao = :descricao, estrategia = :estrategia
        """)
        with database.engine.begin() as conn:
            conn.execute(query, dados)
        return jsonify({"status": "sucesso"})

    with database.engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM cad_atividades ORDER BY codigo"))
        return jsonify([dict(r._mapping) for r in res])

@app.route('/api/cadastros/atividades/<codigo>', methods=['DELETE'])
def excluir_atividade(codigo):
    query = text("DELETE FROM cad_atividades WHERE codigo = :codigo")
    with database.engine.begin() as conn:
        conn.execute(query, {"codigo": codigo})
    return jsonify({"status": "sucesso"})

@app.route('/api/projetos/conferencia', methods=['GET'])
def listar_conferencia():
    query = text("""
        SELECT 
            -- Colunas enriquecidas com COALESCE e concatenação
            COALESCE(l.gerente_tarefa || ' - ' || g.nome, l.gerente_tarefa) as gerente_tarefa,
            COALESCE(l.cod_resultado || ' - ' || a.descricao, l.cod_resultado) as cod_resultado,
            
            l.gerente,
            l.cliente,
            l.id_proj,
            l.projeto, 
            l.centro_resultado,
            l.tp_proj,
            l.id_tarefa, 
            l.tarefa, 
            l.dt_inicio,
            l.dt_fim,
            l.trab_prev,
            l.trab_apontado,
            l.sld_hrs
        FROM 
            lancamentos_projeto l
        LEFT JOIN 
            cad_gerentes g ON l.gerente_tarefa = g.codigo
        LEFT JOIN 
            cad_atividades a ON l.cod_resultado = a.codigo
        WHERE 
            l.ativo = TRUE
        ORDER BY 
            (l.gerente_tarefa IS NULL OR l.gerente_tarefa = '') DESC, 
            (l.cod_resultado IS NULL OR l.cod_resultado = '') DESC,
            l.dt_inicio DESC
    """)
    with database.engine.connect() as conn:
        res = conn.execute(query)
        # É importante converter os tipos de dados que não são JSON-serializáveis (como Decimal)
        data = [dict(r._mapping) for r in res]
        for row in data:
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    row[key] = float(value)
        return jsonify(data)

# --- ROTA DE ATUALIZAÇÃO MANUAL ---

@app.route('/api/extrair/projetos', methods=['POST'])
def rota_extrair_projetos():
    try:
        main.iniciar_fluxo_projetos() 
        return jsonify({"status": "sucesso", "mensagem": "Base PSOffice atualizada com sucesso!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)