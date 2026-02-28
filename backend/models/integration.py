from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, TIMESTAMP, ForeignKey
from database import Base

# PSOffice Models
class Usuario(Base):
    __tablename__ = "usuarios"

    usu_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    sigla = Column(String(50))
    login = Column(String(50))
    email = Column(String(100), unique=True)
    ativo = Column(Boolean, default=True)
    dt_nascimento = Column(TIMESTAMP)
    
    # Custom Internal logic
    id_equipe = Column(Integer, ForeignKey("cad_gerentes.id"), nullable=True)
    agile_id = Column(String(100), nullable=True) # From /users agile tracking
    password_hash = Column(String(255), nullable=True) # Authentication handling
    reset_token = Column(String(255), nullable=True) # Password recovery token

class Cliente(Base):
    __tablename__ = "cliente"

    pj_id = Column(Integer, primary_key=True, autoincrement=True) # Or Serial
    codigo = Column(String(20), nullable=False)
    nome = Column(String(100), nullable=False)
    razao_social = Column(String(255), nullable=False)
    cnpj = Column(String(20), unique=False, nullable=True) # JExperts API allows null/duplicates
    ativo = Column(Boolean, default=True, nullable=False)

class Projeto(Base):
    __tablename__ = "projetos"

    proj_id = Column(Integer, primary_key=True)
    codigo = Column(String(100))
    nome = Column(String(500))
    objetivo = Column(Text)
    
    # Desnormalizado
    empresa_pj_id = Column(String(20))
    empresa_codigo = Column(String(30))
    empresa_nome = Column(String(100))
    
    cliente_pj_id = Column(Integer, ForeignKey("cliente.pj_id"), nullable=True)
    cliente_codigo = Column(String(30))
    cliente_nome = Column(String(100))
    
    centro_resultado_cr_id = Column(Integer, ForeignKey("centro_de_resultado.id"), nullable=True)
    centro_resultado_nome = Column(String(255))
    
    gerente_usu_id = Column(Integer, ForeignKey("usuarios.usu_id"), nullable=True)
    gerente_nome = Column(String(100))
    gerente_dt_admissao = Column(TIMESTAMP)
    gerente_dt_nascimento = Column(TIMESTAMP)
    
    # Datas & Work
    dt_inicio = Column(TIMESTAMP)
    dt_fim = Column(TIMESTAMP)
    dt_encerramento = Column(TIMESTAMP)
    trabalho_previsto = Column(Integer)
    trabalho_faltando = Column(Integer)
    trabalho_apontado = Column(Integer)
    duracao_prevista = Column(Integer)
    
    # Situação / Flags
    co_situacao = Column(String(5))
    situacao_desc = Column(String(50))
    horas_faturaveis = Column(Boolean)

class Atividade(Base):
    __tablename__ = "atividades"

    ativ_id = Column(Integer, primary_key=True)
    proj_id = Column(Integer, ForeignKey("projetos.proj_id"))
    id = Column(Integer)
    nome = Column(String(500))
    tipo = Column(String(20))
    nivel = Column(Integer)
    
    dt_inicio_planejado = Column(TIMESTAMP)
    dt_fim_planejado = Column(TIMESTAMP)
    
    trabalho_previsto = Column(Integer)
    trabalho_faltando = Column(Integer)
    trabalho = Column(Integer)
    
    encerrada = Column(Boolean)
    situacao = Column(String(20))
    situacao_desc = Column(String(100))
    
    # Regra de negocio ETL preenchimento
    cod_resultado = Column(String(10), nullable=True)
    g_tarefa = Column(String(10), nullable=True)

class Apontamento(Base):
    __tablename__ = "apontamentos"
    
    apon_id = Column(Integer, primary_key=True)
    dt_submissao = Column(TIMESTAMP)
    minutos_reconhecidos = Column(Integer)
    dt_inicio = Column(TIMESTAMP)
    comentarios = Column(Text)
    minutos = Column(Integer)
    minutos_faturados = Column(Integer)
    
    proj_id = Column(Integer, ForeignKey("projetos.proj_id"))
    ativ_id = Column(Integer, ForeignKey("atividades.ativ_id"))
    usu_id = Column(Integer, ForeignKey("usuarios.usu_id"))
    nome_atividade = Column(Text)
    usuario = Column(String(100))
    hr_inicio = Column(TIMESTAMP)
    nome_projeto = Column(Text)
    
    # Campo extraido do ETL
    card_vinculado = Column(String(255), nullable=True)

# Agile Models
class ProjetoAgile(Base):
    __tablename__ = "projetos_agile"

    id = Column(Integer, primary_key=True)
    code = Column(String(100))
    name = Column(String(100))
    author = Column(String(100))
    archived = Column(Integer)


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    name = Column(String(255))
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    status = Column(String(50))
    agile_project_id = Column(Integer, ForeignKey("projetos_agile.id"))

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    agile_project_id = Column(Integer, ForeignKey("projetos_agile.id"))
    agile_project_name = Column(String(255))
    impediment = Column(Text, nullable=True)
    target_date = Column(TIMESTAMP)
    finished_date = Column(TIMESTAMP, nullable=True)
    author = Column(String(100))
    estimated_minutes = Column(Integer)
    remaining_minutes = Column(Integer)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    sprint_name = Column(String(255), nullable=True)
    title = Column(String(500))
    points = Column(Integer) # For "Valor Entregue" calculus
    status = Column(String(50))
    description = Column(Text)

class BucketIssue(Base):
    """ Represents Kanbam mapping """
    __tablename__ = "buckets_issues"
    
    id = Column(Integer, primary_key=True)
    bucket_id = Column(Integer)
    bucket_name = Column(String(100))
    agile_project_id = Column(Integer, ForeignKey("projetos_agile.id"))
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    issue_title = Column(String(500))
