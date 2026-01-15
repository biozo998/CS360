from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import processor
import scraper
import os

app = Flask(__name__)
CORS(app) # Permite que o React acesse a API

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "Online", "projeto": "CS360"})

# ROTA PARA O BOTÃO "EXTRAIR AGORA"
@app.route('/api/extrair/projetos', methods=['POST'])
def extrair_projetos():
    try:
        database.inicializar_banco()
        caminho = scraper.extrair_relatorio("projetos")
        if caminho:
            df = processor.processar_projetos(caminho)
            database.upsert_dados(df)
            return jsonify({"status": "sucesso", "mensagem": "Relatório atualizado no banco!"})
        return jsonify({"status": "erro", "mensagem": "Falha no download"}), 500
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# ROTA PARA O GRÁFICO: HORAS POR GERENTE
@app.route('/api/dash/horas-por-gerente', methods=['GET'])
def horas_por_gerente():
    from sqlalchemy import text
    query = """
        SELECT gerente_tarefa, SUM(trab_apontado) as total_horas
        FROM lancamentos_projeto
        WHERE ativo = TRUE AND gerente_tarefa IS NOT NULL
        GROUP BY gerente_tarefa
        ORDER BY total_horas DESC
    """
    with database.engine.connect() as conn:
        result = conn.execute(text(query))
        data = [{"gerente": r[0], "horas": float(r[1])} for r in result]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)