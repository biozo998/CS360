import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter, faCheck, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
import { formatarHoraDecimal, formatarDataBR } from '../utils/formatters';
import './Conferencia.css';

const Conferencia = () => {
  const [dados, setDados] = useState([]);
  const [somenteErros, setSomenteErros] = useState(false);
  const [loading, setLoading] = useState(true);

  // --- CONFIGURAÇÃO DAS COLUNAS ---
  const [colunas, setColunas] = useState([
    { key: 'gerente_tarefa', label: 'Gerente Tarefa', width: 65 },
    { key: 'cod_resultado', label: 'Cód. Área', width: 65 },
    { key: 'gerente', label: 'Gerente Proj.', width: 130 },
    { key: 'cliente', label: 'Cliente', width: 120 },
    { key: 'id_proj', label: 'ID Proj.', width: 65 },
    { key: 'projeto', label: 'Projeto', width: 150 },
    { key: 'centro_resultado', label: 'CR', width: 120 },
    { key: 'tp_proj', label: 'TP Proj', width: 65 },
    { key: 'id_tarefa', label: 'ID Tarefa', width: 75 },
    { key: 'tarefa', label: 'Tarefa', width: 300 },
    // Colunas de Data e Hora
    { key: 'dt_inicio', label: 'Início', width: 115, type: 'date' },
    { key: 'dt_fim', label: 'Fim', width: 115, type: 'date' },
    // Colunas Numéricas
    { key: 'trab_prev', label: 'Trab. Prev', width: 75, type: 'time' },
    { key: 'trab_apontado', label: 'Apontado', width: 75, type: 'time' },
    { key: 'sld_hrs', label: 'Saldo', width: 100, type: 'time' },
  ]);

  const activeIndex = useRef(null);

  // --- HELPERS DE FORMATAÇÃO ---
  const formatarData = (valor) => {
    if (!valor) return '-';
    // Converte string GMT para Objeto Date e formata DD/MM/AAAA
    return new Date(valor).toLocaleDateString('pt-BR');
  };

  const formatarNumero = (valor) => {
    if (valor === null || valor === undefined) return '-';
    // Formata para 0,00 (vírgula decimal, ponto milhar)
    return Number(valor).toLocaleString('pt-BR', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    });
  };

  const carregarDados = () => {
    setLoading(true);
    axios.get('http://localhost:5000/api/projetos/conferencia')
      .then(res => {
        setDados(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => { carregarDados(); }, []);

  // Lógica de Resize (Mantida igual)
  const mouseMove = (e) => {
    if (activeIndex.current === null) return;
    const gridColumns = [...colunas];
    const col = gridColumns[activeIndex.current];
    if(e.movementX !== 0) {
        col.width = Math.max(50, col.width + e.movementX);
        setColunas(gridColumns);
    }
  };

  const mouseUp = () => {
    activeIndex.current = null;
    document.removeEventListener('mousemove', mouseMove);
    document.removeEventListener('mouseup', mouseUp);
    document.body.style.cursor = 'default';
  };

  const mouseDown = (e, index) => {
    activeIndex.current = index;
    document.addEventListener('mousemove', mouseMove);
    document.addEventListener('mouseup', mouseUp);
    document.body.style.cursor = 'col-resize';
  };

  const dadosExibidos = somenteErros 
    ? dados.filter(d => !d.gerente_tarefa || !d.cod_resultado)
    : dados;

  const totalErros = dados.filter(d => !d.gerente_tarefa || !d.cod_resultado).length;

  return (
    <div className="fluid-container">
      <div className="view-card" style={{ width: '100%', border: 'none', boxShadow: 'none', padding: '20px' }}>
        
        <div className="header-conferencia">
          <div>
            <h2>Conferência de Extração</h2>
            <p>Visualização completa de dados brutos.</p>
          </div>
          
          <button 
            className={`btn-filter ${somenteErros ? 'active' : ''}`} 
            onClick={() => setSomenteErros(!somenteErros)}
          >
            <FontAwesomeIcon icon={somenteErros ? faExclamationTriangle : faFilter} />
            {somenteErros ? ' Mostrando Apenas Inconsistentes' : ' Filtrar Inconsistências'}
          </button>
        </div>

        <div className="table-wrapper">
          <table style={{ width: colunas.reduce((acc, c) => acc + c.width, 0) }}>
            <thead>
              <tr>
                {colunas.map((col, index) => (
                  <th key={col.key} style={{ width: col.width }}>
                    <div className="th-content">{col.label}</div>
                    <div className="resizer" onMouseDown={(e) => mouseDown(e, index)} />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={colunas.length} style={{textAlign: 'center', padding: '40px'}}>Carregando dados...</td></tr>
              ) : dadosExibidos.map((d, i) => (
                <tr key={i}>
                  {colunas.map(col => {
                    let className = '';
                    let content = d[col.key];

                    // 1. Validação de Erros (Prioridade)
                    if ((col.key === 'gerente_tarefa' || col.key === 'cod_resultado')) {
                        if (!content) {
                            className = 'cell-error';
                            content = <span className="tag-missing">PENDENTE</span>;
                        } else {
                            content = <><span style={{color:'#10B981', marginRight:4}}><FontAwesomeIcon icon={faCheck} size="xs"/></span>{content}</>;
                        }
                    } 
                    // 2. Formatação de Datas
                    else if (col.type === 'date') {
                        content = formatarData(content);
                    }
                    // 3. Formatação de Horas
                    else if (col.type === 'time') {
                        content = formatarHoraDecimal(content);
                        className = 'text-right'; // Mantém alinhado à direita
                    }

                    return (
                      <td key={col.key} className={className} title={d[col.key]}>
                        {content}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="footer-info">
            <span>Inconsistências: <strong style={{color: '#EF4444'}}>{totalErros}</strong></span>
            <span>Total: <strong>{dadosExibidos.length}</strong></span>
        </div>

      </div>
    </div>
  );
};

export default Conferencia;