import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import logging
import re
from datetime import datetime
from config import config
from database import get_db
from sqlalchemy.orm import Session
from models.integration import Usuario, Cliente, Projeto, Atividade, Apontamento, ProjetoAgile, Sprint, Issue, BucketIssue

logger = logging.getLogger(__name__)

class ETLEngine:
    def __init__(self):
        self.pso_client = PSOfficeClient()
        self.agile_client = AgileClient()

    def sync_users_identity(self):
        """Cross references emails from the Agile API to update agile_id on PostgreSQL"""
        logger.info("[ETL] Syncing User Identities...")
        agile_users = self.agile_client.get_users()
        
        email_to_agile_id = {u['email']: u['id'] for u in agile_users if 'email' in u and 'id' in u}
        
        db = next(get_db())
        try:
            usuarios = db.query(Usuario).all()
            updated = 0
            for u in usuarios:
                if u.email in email_to_agile_id:
                    if u.agile_id != email_to_agile_id[u.email]:
                        u.agile_id = email_to_agile_id[u.email]
                        updated += 1
            db.commit()
            logger.info(f"[ETL] Updated {updated} user identities with Agile IDs.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Sync Users Error: {e}")
            raise
        finally:
            db.close()

    def parse_apontamento_regex(self, comentarios):
        """Extracts CARD_VINCULADO from 'Esse apontamento foi realizado no card: (.*?) -'"""
        if not comentarios:
            return None
        match = re.search(r"Esse apontamento foi realizado no card:\s*(.*?)\s*-", comentarios)
        if match:
            return match.group(1).strip()
        return None

    def parse_atividade_regex(self, cliente_cnpj, centro_res_nome, atividade_nome):
        """Extracts cod_resultado and g_tarefa based on Client CNPJ rule."""
        if not cliente_cnpj or not atividade_nome:
            return None, None
            
        cnpj_limpo = re.sub(r"[^\d]", "", cliente_cnpj)
        
        # CNPJ clients logic: "07.444.561/0001-29" -> "07444561000129"
        # "15.491.115/0001-01" -> "15491115000101"
        target_cnpjs = ["07444561000129", "15491115000101"]
        
        cod_resultado = None
        g_tarefa = None
        
        if cnpj_limpo in target_cnpjs:
            # Look for 000-000 pattern in atividade_nome
            match = re.search(r'(\d{3})-(\d{3})', atividade_nome)
            if match:
                cod_resultado = match.group(1)
                g_tarefa = match.group(2)
        else:
            # Default behavior
            if centro_res_nome:
                match_cr = re.match(r'^(\d{3})', centro_res_nome)
                if match_cr:
                    cod_resultado = match_cr.group(1)
            if atividade_nome:
                match_tar = re.match(r'^(\d{3})', atividade_nome)
                if match_tar:
                    g_tarefa = match_tar.group(1)
                    
        return cod_resultado, g_tarefa

    def sync_clientes(self):
        logger.info("[ETL] Syncing Clientes...")
        clientes_data = self.pso_client.get_clientes()
        # The API usually returns paginated or unwrapped list. Assuming unwrapped based on goals.
        # If wrapped, should extract from 'data' or similar wrapper.
        
        db = next(get_db())
        try:
            seen_pj_ids = set()
            for item in clientes_data:
                pj_id = item.get('pjId')
                if not pj_id or pj_id in seen_pj_ids:
                    continue
                    
                seen_pj_ids.add(pj_id)
                cliente = db.query(Cliente).filter(Cliente.pj_id == pj_id).first()
                if not cliente:
                    cliente = Cliente(pj_id=pj_id)
                    db.add(cliente)
                
                cliente.codigo = item.get('codigo')
                cliente.nome = item.get('nome')
                cliente.razao_social = item.get('razaoSocial', item.get('nome', ''))
                cliente.cnpj = item.get('cnpj')
                cliente.ativo = item.get('ativo', True)
            db.commit()
            logger.info("[ETL] Clientes Sync complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing clientes: {e}")
            raise e
        finally:
            db.close()

    def sync_usuarios(self):
        logger.info("[ETL] Syncing Usuarios...")
        usuarios_data = self.pso_client.get_usuarios()
        
        # Fetch Agile Users to cross-reference agile_id by email
        agile_map = {}
        try:
            agile_users_data = self.agile_client.get_users()
            if isinstance(agile_users_data, list):
                for au in agile_users_data:
                    email_str = au.get('email')
                    if email_str:
                        agile_map[email_str.strip().lower()] = str(au.get('id', ''))
            logger.info(f"[ETL] Mapped {len(agile_map)} Agile users for cross-referencing.")
        except Exception as ae:
            logger.warning(f"[ETL] Could not fetch Agile Users for cross-referencing: {ae}")
            
        db = next(get_db())
        try:
            seen_usu_ids = set()
            for item in usuarios_data:
                usu_id = item.get('usuId')
                if not usu_id or usu_id in seen_usu_ids:
                    continue
                seen_usu_ids.add(usu_id)
                
                usu = db.query(Usuario).filter(Usuario.usu_id == usu_id).first()
                if not usu:
                    usu = Usuario(usu_id=usu_id)
                    db.add(usu)
                
                usu.nome = item.get('nome')
                usu.sigla = item.get('sigla')
                usu.login = item.get('login')
                email = item.get('email')
                usu.email = email
                usu.ativo = item.get('ativo', True)
                
                # Cross-reference Agile ID
                if email and email.strip().lower() in agile_map:
                    usu.agile_id = agile_map[email.strip().lower()]
                
                dt_nasc = item.get('dtNascimento')
                if dt_nasc:
                    try:
                        usu.dt_nascimento = datetime.strptime(dt_nasc, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass # Ignore if format differs
            db.commit()
            logger.info("[ETL] Usuarios Sync complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing usuarios: {e}")
            raise e
        finally:
            db.close()

    def sync_projetos(self):
        logger.info("[ETL] Syncing Projetos...")
        projetos_data = self.pso_client.get_projetos()
        
        db = next(get_db())
        try:
            seen_proj_ids = set()
            for item in projetos_data:
                proj_id = item.get('projId')
                if not proj_id or proj_id in seen_proj_ids:
                    continue
                seen_proj_ids.add(proj_id)
                proj = db.query(Projeto).filter(Projeto.proj_id == proj_id).first()
                if not proj:
                    proj = Projeto(proj_id=proj_id)
                    db.add(proj)
                
                proj.codigo = item.get('codigo')
                proj.nome = item.get('nome')
                proj.objetivo = item.get('objetivo')
                
                empresa = item.get('empresa', {})
                proj.empresa_pj_id = str(empresa.get('pjId', ''))
                proj.empresa_codigo = empresa.get('codigo')
                proj.empresa_nome = empresa.get('nome')
                
                cliente = item.get('cliente', {})
                proj.cliente_pj_id = cliente.get('pjId')
                proj.cliente_codigo = cliente.get('codigo')
                proj.cliente_nome = cliente.get('nome')
                
                cr = item.get('centroResultado', {})
                proj.centro_resultado_cr_id = cr.get('crId')
                proj.centro_resultado_nome = cr.get('nome')
                
                gp = item.get('gerenteProjeto', {})
                proj.gerente_usu_id = gp.get('usuId')
                proj.gerente_nome = gp.get('nome')
                if gp.get('dtAdmissao'):
                    try: proj.gerente_dt_admissao = datetime.strptime(gp.get('dtAdmissao'), "%Y-%m-%d %H:%M:%S")
                    except ValueError: pass
                if gp.get('dtNascimento'):
                    try: proj.gerente_dt_nascimento = datetime.strptime(gp.get('dtNascimento'), "%Y-%m-%d %H:%M:%S")
                    except ValueError: pass
                
                for dt_field in ['dtInicio', 'dtFim', 'dtEncerramento']:
                    if item.get(dt_field):
                        setattr(proj, 'dt_' + dt_field[2:].lower(), item.get(dt_field)) # Assuming the API returns YYYY-MM-DD or similar
                
                proj.trabalho_previsto = item.get('trabalhoPrevisto')
                proj.trabalho_faltando = item.get('trabalhoFaltando')
                proj.trabalho_apontado = item.get('trabalhoApontado')
                proj.duracao_prevista = item.get('duracaoPrevista')
                proj.co_situacao = item.get('coSituacao')
                proj.situacao_desc = item.get('situacaoDesc')
                proj.horas_faturaveis = item.get('horasFaturaveis')

            db.commit()
            logger.info("[ETL] Projetos Sync complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing projetos: {e}")
            raise e
        finally:
            db.close()

    def sync_atividades(self, proj_id):
        logger.info(f"[ETL] Syncing Atividades for proj_id: {proj_id}")
        atividades_data = self.pso_client.get_atividades(proj_id)
        
        db = next(get_db())
        try:
            # Need project data to run Rules
            projeto = db.query(Projeto).filter(Projeto.proj_id == proj_id).first()
            if not projeto:
                logger.warning(f"[ETL] Projeto {proj_id} not found locally. Atividades will lack Regex cross-references.")
                
            try:
                import requests # Ensure it's reachable for exception catching
                atividades_data = self.pso_client.get_atividades(proj_id)
            except Exception as req_e:
                logger.warning(f"[ETL] Skipping atividades for proj {proj_id} due to API error: {req_e}")
                return # Skip if the API throws a 400 for this specific project
                
            if not isinstance(atividades_data, list):
                logger.warning(f"[ETL] Skipping atividades for proj {proj_id} (Returned dict instead of list)")
                return

            seen_ativ_ids = set()
            for item in atividades_data:
                ativ_id = item.get('ativId')
                if not ativ_id or ativ_id in seen_ativ_ids:
                    continue
                seen_ativ_ids.add(ativ_id)
                
                ativ = db.query(Atividade).filter(Atividade.ativ_id == ativ_id).first()
                if not ativ:
                    ativ = Atividade(ativ_id=ativ_id)
                    db.add(ativ)
                    
                ativ.proj_id = proj_id
                ativ.id = item.get('id')
                ativ.nome = item.get('nome')
                ativ.tipo = item.get('tipo')
                ativ.nivel = item.get('nivel')
                
                for dt_field in ['dtInicioPlanejado', 'dtFimPlanejado']:
                    if item.get(dt_field):
                         try: setattr(ativ, 'dt_' + dt_field[2:].lower() + '_planejado', datetime.strptime(item.get(dt_field), "%Y-%m-%d %H:%M:%S"))
                         except ValueError: pass
                
                ativ.trabalho_previsto = item.get('trabalhoPrevisto')
                ativ.trabalho_faltando = item.get('trabalhoFaltando')
                ativ.trabalho = item.get('trabalho')
                ativ.encerrada = item.get('encerrada')
                ativ.situacao = item.get('situacao')
                ativ.situacao_desc = item.get('situacaoDesc')
                
                # Apply Regex Rule
                if projeto:
                    cod_res, g_tar = self.parse_atividade_regex(projeto.cliente_cnpj if hasattr(projeto, 'cliente_cnpj') else projeto.cliente_codigo, projeto.centro_resultado_nome, ativ.nome)
                    ativ.cod_resultado = cod_res
                    ativ.g_tarefa = g_tar

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing atividades for proj {proj_id}: {e}")
            raise e
        finally:
            db.close()

    def sync_apontamentos(self, data_inicio, data_fim):
        logger.info(f"[ETL] Syncing Apontamentos from {data_inicio} to {data_fim}")
        apontamentos_data = self.pso_client.get_apontamentos(data_inicio, data_fim)
        
        db = next(get_db())
        try:
            seen_apon_ids = set()
            for item in apontamentos_data:
                apon_id = item.get('APON_ID')
                if not apon_id or apon_id in seen_apon_ids:
                    continue
                seen_apon_ids.add(apon_id)
                
                apon = db.query(Apontamento).filter(Apontamento.apon_id == apon_id).first()
                if not apon:
                    apon = Apontamento(apon_id=apon_id)
                    db.add(apon)
                
                for dt_field in ['DT_SUBMISSAO', 'DT_INICIO', 'HR_INICIO']:
                    if item.get(dt_field):
                         try: setattr(apon, dt_field.lower(), datetime.strptime(item.get(dt_field), "%Y-%m-%d %H:%M:%S"))
                         except ValueError: pass
                
                apon.minutos_reconhecidos = int(item.get('MINUTOS_RECONHECIDOS', 0)) if item.get('MINUTOS_RECONHECIDOS') else 0
                apon.minutos = int(item.get('MINUTOS', 0)) if item.get('MINUTOS') else 0
                apon.minutos_faturados = int(item.get('MINUTOS_FATURADOS', 0)) if item.get('MINUTOS_FATURADOS') else 0
                apon.comentarios = item.get('COMENTARIOS')
                
                apon.proj_id = int(item.get('PROJ_ID')) if item.get('PROJ_ID') else None
                apon.ativ_id = int(item.get('ATIV_ID')) if item.get('ATIV_ID') else None
                apon.usu_id = int(item.get('USU_ID')) if item.get('USU_ID') else None
                
                apon.nome_atividade = item.get('NOME_ATIVIDADE')
                apon.usuario = item.get('USUARIO')
                apon.nome_projeto = item.get('NOME_PROJETO')
                
                # Regex Rule
                apon.card_vinculado = self.parse_apontamento_regex(apon.comentarios)

            db.commit()
            logger.info("[ETL] Apontamentos Sync complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing apontamentos: {e}")
            raise e
        finally:
            db.close()
            
    def sync_agile(self):
        """Fetches Agile boundaries (Projects, Epics, Sprints, Issues)"""
        logger.info("[ETL] Syncing Agile Infrastructure...")
        db = next(get_db())
        try:
            # 1. Projects
            agile_projs = self.agile_client.get_projects()
            for p in agile_projs:
                proj = db.query(ProjetoAgile).filter(ProjetoAgile.id == p.get('id')).first()
                if not proj: proj = ProjetoAgile(id=p.get('id')); db.add(proj)
                proj.code = p.get('code')
                proj.name = p.get('name')
                proj.author = p.get('author')
                proj.archived = p.get('archived')
            db.commit()
            

            
            # 3. Sprints
            agile_sprints = self.agile_client.get_sprints()
            seen_sprints = set()
            for s in agile_sprints:
                s_id = s.get('id')
                if not s_id or s_id in seen_sprints: continue
                seen_sprints.add(s_id)
                sprint = db.query(Sprint).filter(Sprint.id == s_id).first()
                if not sprint: sprint = Sprint(id=s_id); db.add(sprint)
                sprint.code = str(s.get('code'))
                sprint.name = s.get('name')
                sprint.status = s.get('status')
                sprint.agile_project_id = s.get('agileProjectId')
                for dt_f in ['startDate', 'endDate']:
                    if s.get(dt_f):
                         try: setattr(sprint, re.sub(r'(?<!^)(?=[A-Z])', '_', dt_f).lower(), datetime.strptime(s.get(dt_f).split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                         except ValueError: pass
            db.commit()
            
            # 4. Issues & Buckets (Iterating across mapped agile projects)
            mapped_projs = db.query(ProjetoAgile.id).all()
            for (p_id,) in mapped_projs:
                time.sleep(0.5) # Rate limit protection
                try:
                    # Sync Issues
                    issues = self.agile_client.get_issues(p_id)
                    seen_issues = set()
                    for i in issues:
                        i_id = i.get('id')
                        if not i_id or i_id in seen_issues: continue
                        seen_issues.add(i_id)
                        issue = db.query(Issue).filter(Issue.id == i_id).first()
                        if not issue: issue = Issue(id=i_id); db.add(issue)
                        issue.code = str(i.get('code'))
                        issue.agile_project_id = i.get('agileProjectId')
                        issue.agile_project_name = i.get('agileProjectName')
                        issue.title = i.get('title')
                        issue.points = i.get('points', 0)
                        issue.status = i.get('status')
                        issue.author = i.get('author')
                        issue.sprint_id = i.get('sprintId')

                        issue.estimated_minutes = i.get('estimatedMinutes')
                        issue.remaining_minutes = i.get('remainingMinutes')
                        for dt_f in ['targetDate', 'finishedDate']:
                            if i.get(dt_f):
                                 try: setattr(issue, re.sub(r'(?<!^)(?=[A-Z])', '_', dt_f).lower(), datetime.strptime(i.get(dt_f).split('.')[0], "%Y-%m-%dT%H:%M:%S"))
                                 except ValueError: pass
                    db.commit()
                    
                    # Sync Buckets for the project
                    buckets = self.agile_client.get_bucket_issues(p_id)
                    seen_buckets = set()
                    for b in buckets:
                        b_id = b.get('id')
                        if not b_id or b_id in seen_buckets: continue
                        seen_buckets.add(b_id)
                        bk = db.query(BucketIssue).filter(BucketIssue.id == b_id).first()
                        if not bk: bk = BucketIssue(id=b_id); db.add(bk)
                        bk.bucket_id = b.get('bucketId')
                        bk.bucket_name = b.get('bucketName')
                        bk.agile_project_id = b.get('agileProjectId')
                        bk.sprint_id = b.get('sprintId')
                        bk.issue_id = b.get('issueId')
                        bk.issue_title = b.get('issueTitle')
                    db.commit()
                    
                except Exception as loop_e:
                    db.rollback()
                    logger.warning(f"[ETL] Skipping issues/buckets for agile_proj {p_id} due to API Error: {loop_e}")
            
            logger.info("[ETL] Agile Sync Complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ETL] Error syncing agile: {e}")
        finally:
            db.close()

    def parse_atividade_regex(self, cnpj_ou_codigo, centro_resultado_nome, atividade_nome):
        """
        Parses Atividade names based on specific CNPJ Business Rules.
        """
        if not atividade_nome:
            return None, None
            
        cnpj_limpo = re.sub(r'[^0-9]', '', str(cnpj_ou_codigo)) if cnpj_ou_codigo else ""
        
        # Rule Set 1: Special Clients (CS-Integra and specific cases)
        if cnpj_limpo.startswith('15491115') or cnpj_limpo.startswith('07444561'):
            match = re.search(r'(\d{3})-(\d{3})', atividade_nome)
            if match:
                return match.group(1), match.group(2)
            return None, None
            
        # Rule Set 2: Standard Clients
        cod_resultado = None
        if centro_resultado_nome:
            cr_match = re.search(r'^(\d{3})\b', centro_resultado_nome.strip())
            if cr_match:
                cod_resultado = cr_match.group(1)
                
        g_tarefa = None
        g_match = re.search(r'^(\d{3})\b', atividade_nome.strip())
        if g_match:
            g_tarefa = g_match.group(1)
            
        return cod_resultado, g_tarefa
        
    def parse_apontamento_regex(self, comentarios):
        """
        Extrai o CARD_VINCULADO caso a string 'Esse apontamento foi realizado no card: XXX -' 
        exista no comentario do apontamento lido da API.
        """
        if not comentarios:
            return None
            
        match = re.search(r'Esse apontamento foi realizado no card:\s*([^\s]+)', comentarios)
        if match:
            return match.group(1).strip()
            
        return None
