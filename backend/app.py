from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import processor
import scraper
from sqlalchemy import text

app = Flask(__name__)
# O CORS(app) resolve o erro que você viu na imagem
CORS(app) 

# Garante que as tabelas (inclusive as novas de cadastro) sejam criadas ao iniciar
database.inicializar_banco()

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

@app.route('/api/dash/horas-por-gerente', methods=['GET'])
def horas_por_gerente():
    # SQL MELHORADO: Faz um JOIN com a tabela de cadastro para pegar o NOME
    query = text("""
        SELECT 
            COALESCE(g.nome, l.gerente_tarefa) as gerente, 
            SUM(l.trab_apontado) as horas
        FROM lancamentos_projeto l
        LEFT JOIN cad_gerentes g ON l.gerente_tarefa = g.codigo
        WHERE l.ativo = TRUE AND l.gerente_tarefa IS NOT NULL
        GROUP BY 1
        ORDER BY horas DESC
    """)
    with database.engine.connect() as conn:
        result = conn.execute(query)
        data = [{"gerente": r[0], "horas": float(r[1])} for r in result]
    return jsonify(data)

# No seu backend/app.py

@app.route('/api/cadastros/atividades', methods=['GET', 'POST'])
def gerenciar_atividades():
    if request.method == 'POST':
        dados = request.json
        # Importante: O SQL deve bater com os nomes das colunas que criamos
        query = text("""
            INSERT INTO cad_atividades (codigo, tipo_hora, descricao, estrategia)
            VALUES (:codigo, :tipo_hora, :descricao, :estrategia)
            ON CONFLICT (codigo) DO UPDATE 
            SET tipo_hora = :tipo_hora, descricao = :descricao, estrategia = :estrategia
        """)
        with database.engine.begin() as conn:
            conn.execute(query, dados)
        return jsonify({"status": "sucesso"})

    # Para o GET (Listagem)
    with database.engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM cad_atividades ORDER BY codigo"))
        return jsonify([dict(r._mapping) for r in res])

# Rota de exclusão para manter o padrão CRUD
@app.route('/api/cadastros/atividades/<codigo>', methods=['DELETE'])
def excluir_atividade(codigo):
    query = text("DELETE FROM cad_atividades WHERE codigo = :codigo")
    with database.engine.begin() as conn:
        conn.execute(query, {"codigo": codigo})
    return jsonify({"status": "sucesso"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)