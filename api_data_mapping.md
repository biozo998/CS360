# Mapeamento de Rotas API e Tabela de Destino

| Sistema Origem | Endpoint | Tipo de Dados Extraídos | Tabela Destino no Banco |
| :--- | :--- | :--- | :--- |
| **PSOffice** | `/projetos/` | Projetos base e metadados estruturais | `projetos` |
| **PSOffice** | `/projetos/{id}/atividades/` | WBS (Atividades de projetos) | `atividades` |
| **PSOffice** | `/usuarios/` | Cadastro de Usuários Ativos/Inativos | `usuarios` |
| **PSOffice** | `/clientes/` | Cadastro de Clientes (PJ) | `cliente` |
| **PSOffice** | `/apontamento_horas/` | Horas lançadas dia a dia | `apontamentos` |
| **Agile (JExperts)** | `/projects/` | Projetos contextuais de Metodologia Ágil| `projetos_agile` |
| **Agile (JExperts)** | `/sprints/` | Ciclos iterativos de desenvolvimento | `sprints` |
| **Agile (JExperts)** | `/projects/{id}/issues/` | Cards consolidados, épicos e bugs | `issues` |
| **Agile (JExperts)** | `/projects/{id}/bucket-issues/`| Mapeamento de Issues para repositórios | `bucket_issues` |

---

## Diagrama de Banco de Dados

### Visualização do Relacionamento (Mermaid)

```mermaid
erDiagram
    %% Core Entities
    cliente { int pj_id PK }
    cad_gerentes { int id PK }
    centro_de_resultado { int id PK }
    usuarios { int usu_id PK }
    
    %% Main PSOffice Work
    projetos {
        int proj_id PK
        int cliente_pj_id FK
        int centro_resultado_cr_id FK
        int gerente_usu_id FK
    }
    
    atividades {
        int ativ_id PK
        int proj_id FK
        string g_tarefa "Logico"
        string cod_resultado "Logico"
    }

    apontamentos {
        int id PK
        int ativ_id FK
        int usu_id FK
        string card_vinculado "Logico"
    }
    
    %% Agile Models
    projetos_agile { int id PK }
    sprints { 
        int id PK
        int agile_project_id FK
    }
    issues {
        int id PK
        string code UK
        int sprint_id FK
        int agile_project_id FK
    }
    bucket_issues {
        int id PK
        int issue_id FK
    }

    %% Support Linking
    prioridade_gerente_cr {
        int id PK
        int id_centro_resultado FK
        int usu_id_gerente FK
    }
    agrupamentos_customizados {
        int id PK
        int usu_id_gerente FK
        int ativ_id FK
    }

    %% Relacionamentos Físicos (Foreign Keys)
    projetos }o--|| cliente : "Pertence a"
    projetos }o--|| centro_de_resultado : "Aloca em"
    projetos }o--|| usuarios : "Gerenciado por"
    
    usuarios }o--|| cad_gerentes : "É membro de"
    
    atividades }o--|| projetos : "Faz parte de"
    apontamentos }o--|| atividades : "Aponta horas em"
    apontamentos }o--|| usuarios : "Lançado por"
    
    sprints }o--|| projetos_agile : "Ciclo de"
    issues }o--|| sprints : "Resolvido na"
    issues }o--|| projetos_agile : "Pertence a"
    bucket_issues }o--|| issues : "Agrupa a"
    
    prioridade_gerente_cr }o--|| cad_gerentes : "Definida por"
    prioridade_gerente_cr }o--|| centro_de_resultado : "Aplica ao"
    
    agrupamentos_customizados }o--|| cad_gerentes : "Agrupado por"
    agrupamentos_customizados }o--|o atividades : "Pode listar"

    %% Relacionamentos Lógicos Adicionados Conforme Pedido (Pontilhados)
    apontamentos }o..|o issues : "(Lógico) card_vinculado -> code"
    atividades }o..|| cad_gerentes : "(Lógico) g_tarefa -> cod_g_tarefa"
    atividades }o..|| centro_de_resultado : "(Lógico) cod_resultado -> codigo"
```

### Explicação dos Relacionamentos Lógicos Identificados
As ligações desenhadas como `pontilhadas` acima representam as uniões de Soft-Link solicitadas, que não possuem travas estruturais (Foreign Key dura no Postgres) para garantir estabilidade da sua API:

1. **Apontamentos -> Issues**: A coluna de texto `card_vinculado` de um apontamento liga-se logicamente à coluna `code` de uma Issue, permitindo saber indiretamente de qual requisição ágil aquelas horas pertencem.
2. **Atividades -> Cadastro de Gerentes**: A coluna gerada por RegExp `g_tarefa` correlaciona-se com `cod_g_tarefa` na tabela do respectivo gestor.
3. **Atividades -> Centro de Resultado**: A coluna gerada `cod_resultado` tem correlação direta com o `codigo` oficial da tabela Centro de Resultado.
