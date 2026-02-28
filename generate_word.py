import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import base64
import requests
import zlib

def encode_puml(text):
    # Just in case we wanted plantuml, but we are using mermaid... Let's use mermaid.ink
    pass

def generate_word():
    doc = Document()
    
    # Title
    doc.add_heading('Mapeamento de Rotas API e Tabela de Destino', 0)
    
    # Text intro
    doc.add_paragraph('Este documento consolida os endpoints de extração do ETL com suas respectivas tabelas finais no Banco de Dados.')
    
    # Table Mapping
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Sistema Origem'
    hdr_cells[1].text = 'Endpoint'
    hdr_cells[2].text = 'Tipo de Dados Extraídos'
    hdr_cells[3].text = 'Tabela Destino no Banco'
    
    rows = [
        ('PSOffice', '/projetos/', 'Projetos base e metadados estruturais', 'projetos'),
        ('PSOffice', '/projetos/{id}/atividades/', 'WBS (Atividades de projetos)', 'atividades'),
        ('PSOffice', '/usuarios/', 'Cadastro de Usuários Ativos/Inativos', 'usuarios'),
        ('PSOffice', '/clientes/', 'Cadastro de Clientes (PJ)', 'cliente'),
        ('PSOffice', '/apontamento_horas/', 'Horas lançadas dia a dia', 'apontamentos'),
        ('Agile (JExperts)', '/projects/', 'Projetos contextuais de Metodologia Ágil', 'projetos_agile'),
        ('Agile (JExperts)', '/sprints/', 'Ciclos iterativos de desenvolvimento', 'sprints'),
        ('Agile (JExperts)', '/projects/{id}/issues/', 'Cards consolidados, épicos e bugs', 'issues'),
        ('Agile (JExperts)', '/projects/{id}/bucket-issues/', 'Mapeamento de Issues para repositórios', 'bucket_issues')
    ]
    
    for origin, endpoint, dtype, table_dest in rows:
        row_cells = table.add_row().cells
        row_cells[0].text = origin
        row_cells[1].text = endpoint
        row_cells[2].text = dtype
        row_cells[3].text = table_dest
        
    doc.add_heading('Diagrama de Banco de Dados', level=1)
    
    # Logic relationships text
    doc.add_heading('Explicação dos Relacionamentos Lógicos Identificados', level=2)
    doc.add_paragraph('As uniões de "Soft-Link" (Mapeamentos lógicos em código) representam associações que não possuem travas estruturais estritas físicas ("Foreign Key" dura no Postgres) para garantir estabilidade da integração API:')
    doc.add_paragraph('1. Apontamentos -> Issues: A coluna de texto card_vinculado de um apontamento liga-se logicamente à coluna code de uma Issue.', style='List Bullet')
    doc.add_paragraph('2. Atividades -> Cadastro de Gerentes: A coluna gerada g_tarefa correlaciona-se com cod_g_tarefa na tabela do respectivo gestor.', style='List Bullet')
    doc.add_paragraph('3. Atividades -> Centro de Resultado: A coluna gerada cod_resultado tem correlação direta com o codigo oficial da tabela Centro de Resultado.', style='List Bullet')

    doc.add_heading('Diagrama Visual', level=2)
    
    # Save the doc
    doc.save('Mapeamento_API_e_Diagrama.docx')
    print("Docx created and saved as Mapeamento_API_e_Diagrama.docx successfully.")

if __name__ == '__main__':
    try:
        generate_word()
    except Exception as e:
        print(f"Error: {e}")
