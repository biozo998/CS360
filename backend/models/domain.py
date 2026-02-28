from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class CentroDeResultado(Base):
    __tablename__ = "centro_de_resultado"
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    tipo_hora = Column(String(50))
    descricao = Column(String(255))
    estrategia = Column(String(100)) # Expandir, Consolidar, Fortalecer

class PrioridadeGerenteCR(Base):
    __tablename__ = "prioridade_gerente_cr"
    
    id = Column(Integer, primary_key=True)
    id_centro_resultado = Column(Integer, ForeignKey("centro_de_resultado.id"))
    usu_id_gerente = Column(Integer, ForeignKey("cad_gerentes.id"))
    prioridade = Column(String(20)) # Alta, Média, Baixa
    descricao = Column(Text)

class CadGerentes(Base):
    __tablename__ = "cad_gerentes"
    
    id_user = Column(Integer, ForeignKey("usuarios.usu_id"), primary_key=True)
    cod_id_agile = Column(Integer, ForeignKey("projetos_agile.id"), primary_key=True)
    nome_usuario = Column(String(100))
    cod_g_tarefa = Column(String(100))
    nome_agile = Column(String(100))

class AgrupamentoCustomizado(Base):
    __tablename__ = "agrupamentos_customizados"
    
    id = Column(Integer, primary_key=True)
    usu_id_gerente = Column(Integer, ForeignKey("cad_gerentes.id"))
    tipo = Column(String(50)) # 'FEEDZ' ou 'LIVRE'
    nome_grupo = Column(String(100))
    ativ_id = Column(Integer, ForeignKey("atividades.ativ_id"), nullable=True) # Optional link
