import { useState, useEffect, useMemo, useRef } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter, faCheck, faExclamationTriangle, faFileExcel } from '@fortawesome/free-solid-svg-icons';
import { formatarHoraDecimal, formatarDataBR } from '../utils/formatters';
import './Conferencia.css';

const Conferencia = () => {
  const [dados, setDados] = useState([]);
  const [somenteErros, setSomenteErros] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  const [colunas, setColunas] = useState([
    { key: 'gerente_tarefa', label: 'Gerente Tarefa', width: 250 },
    { key: 'cod_resultado', label: 'Cód. Área', width: 250 },
    { key: 'gerente', label: 'Gerente Proj.', width: 130 },
    { key: 'cliente', label: 'Cliente', width: 120 },
    { key: 'id_proj', label: 'ID Proj.', width: 65 },
    { key: 'projeto', label: 'Projeto', width: 150 },
    { key: 'centro_resultado', label: 'CR', width: 120 },
    { key: 'tp_proj', label: 'TP Proj', width: 65 },
    { key: 'id_tarefa', label: 'ID Tarefa', width: 75 },
    { key: 'tarefa', label: 'Tarefa', width: 300 },
    { key: 'dt_inicio', label: 'Início', width: 115, type: 'date' },
    { key: 'dt_fim', label: 'Fim', width: 115, type: 'date' },
    { key: 'trab_prev', label: 'Trab. Prev', width: 75, type: 'time' },
    { key: 'trab_apontado', label: 'Apontado', width: 75, type: 'time' },
    { key: 'sld_hrs', label: 'Saldo', width: 100, type: 'time' },
  ]);

  const activeIndex = useRef(null);

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

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const filteredData = useMemo(() => {
    let data = somenteErros 
      ? dados.filter(d => !d.gerente_tarefa || !d.cod_resultado || !d.gerente_tarefa.includes('-') || !d.cod_resultado.includes('-'))
      : dados;

    return data.filter(row => {
      for (let key in filters) {
        if (filters[key]) {
          const rowValue = String(row[key] || '').toLowerCase();
          if (!rowValue.includes(filters[key].toLowerCase())) {
            return false;
          }
        }
      }
      return true;
    });
  }, [dados, somenteErros, filters]);

  const handleExport = () => {
    const dataToExport = filteredData.map(row => {
        const newRow = {};
        colunas.forEach(col => {
            let value = row[col.key];
            if (col.type === 'date') value = formatarDataBR(value);
            if (col.type === 'time') value = formatarHoraDecimal(value);
            newRow[col.label] = value;
        });
        return newRow;
    });

    const worksheet = XLSX.utils.json_to_sheet(dataToExport);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Conferencia');
    XLSX.writeFile(workbook, 'Conferencia_Filtrada.xlsx');
  };

  // Lógica de Resize
  const mouseMove = (e) => { /* ... (mantida igual) ... */ };
  const mouseUp = () => { /* ... (mantida igual) ... */ };
  const mouseDown = (e, index) => { /* ... (mantida igual) ... */ };

  const totalErros = dados.filter(d => !d.gerente_tarefa || !d.cod_resultado || !d.gerente_tarefa.includes('-') || !d.cod_resultado.includes('-')).length;

  return (
    <div className="fluid-container">
      <div className="view-card" style={{ width: '100%', border: 'none', boxShadow: 'none', padding: '20px' }}>
        
        <div className="header-conferencia">
          <div>
            <h2>Conferência de Extração</h2>
            <p>Visualização completa de dados brutos.</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              className={`btn-filter ${somenteErros ? 'active' : ''}`} 
              onClick={() => setSomenteErros(!somenteErros)}
            >
              <FontAwesomeIcon icon={somenteErros ? faExclamationTriangle : faFilter} />
              {somenteErros ? ' Mostrando Inconsistentes' : ' Filtrar Inconsistências'}
            </button>
            <button className="btn-export" onClick={handleExport}>
                <FontAwesomeIcon icon={faFileExcel} />
                Exportar Filtrados
            </button>
          </div>
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
              <tr className="filter-row">
                {colunas.map((col) => (
                  <th key={`${col.key}-filter`}>
                    <input
                      type="text"
                      placeholder={`Filtrar ${col.label}`}
                      value={filters[col.key] || ''}
                      onChange={(e) => handleFilterChange(col.key, e.target.value)}
                    />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={colunas.length}>Carregando...</td></tr>
              ) : filteredData.map((d, i) => (
                <tr key={i}>
                  {colunas.map(col => {
                    let className = '';
                    let content = d[col.key];

                    if ((col.key === 'gerente_tarefa' || col.key === 'cod_resultado')) {
                        if (!content || !content.includes('-')) {
                            className = 'cell-error';
                            content = <span className="tag-missing">{content || 'PENDENTE'}</span>;
                        } else {
                            content = <><span className="cell-ok"><FontAwesomeIcon icon={faCheck} size="xs"/></span>{content}</>;
                        }
                    } 
                    else if (col.type === 'date') content = formatarDataBR(content);
                    else if (col.type === 'time') {
                        content = formatarHoraDecimal(content);
                        className = 'text-right';
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
            <span>Mostrando: <strong>{filteredData.length}</strong> de <strong>{dados.length}</strong></span>
        </div>
      </div>
    </div>
  );
};

export default Conferencia;