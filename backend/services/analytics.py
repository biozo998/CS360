import logging
from sqlalchemy.orm import Session
from database import get_db
from models.integration import Apontamento, Atividade, Usuario

logger = logging.getLogger(__name__)

class GovernanceAnalytics:
    def __init__(self):
        pass
        
    def get_t1_alerts(self, data_inicio=None, data_fim=None):
        """
        T1: Apontamentos sem Card Vinculado.
        Flags any worked hours where no card was identified in the comments.
        """
        db = next(get_db())
        try:
            query = db.query(
                Apontamento.apon_id, 
                Apontamento.usuario, 
                Apontamento.dt_inicio, 
                Apontamento.minutos, 
                Apontamento.nome_projeto
            ).filter(
                (Apontamento.card_vinculado == None) | (Apontamento.card_vinculado == '')
            )
            
            if data_inicio: query = query.filter(Apontamento.dt_inicio >= data_inicio)
            if data_fim: query = query.filter(Apontamento.dt_inicio <= data_fim)
                
            return [dict(row._mapping) for row in query.all()]
        finally:
            db.close()

    def get_t2_alerts(self):
        """
        T2: Atividades sem g_tarefa ou cod_resultado válido.
        Flags activities missing the essential strategic classification.
        """
        db = next(get_db())
        try:
            query = db.query(
                Atividade.ativ_id,
                Atividade.nome,
                Atividade.situacao_desc,
                Atividade.proj_id
            ).filter(
                (Atividade.g_tarefa == None) | (Atividade.g_tarefa == '') |
                (Atividade.cod_resultado == None) | (Atividade.cod_resultado == '')
            )
            
            return [dict(row._mapping) for row in query.all()]
        finally:
            db.close()
            
    def get_t3_alerts(self):
        """
        T3: Desalinhamento Crítico (Atividades cujo g_tarefa = 000, e cod_resultado = 000)
        Custom logic could expand here based on client priorities.
        """
        db = next(get_db())
        try:
            query = db.query(
                Atividade.ativ_id,
                Atividade.nome,
                Atividade.g_tarefa,
                Atividade.cod_resultado
            ).filter(
                (Atividade.g_tarefa == '000') & (Atividade.cod_resultado == '000')
            )
            
            return [dict(row._mapping) for row in query.all()]
        finally:
            db.close()
