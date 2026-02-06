import { useEffect, useState } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileExcel, faProjectDiagram, faClock, faCheckCircle, faChartLine, faSync } from '@fortawesome/free-solid-svg-icons';
import Swal from 'sweetalert2';
import './Dashboard.css';
import { formatarDataBR, formatarHoraDecimal } from '../utils/formatters'; // Importar os formatadores

// Constante para a URL da API para facilitar a manutenção
const API_URL = 'http://localhost:5000/api';

// Componente para os Cards de Estatísticas
const StatCard = ({ title, value, icon, iconClass, onExport }) => (
  <div className="stat-card">
    <div className="stat-card-header">
      <span className="stat-card-title">{title}</span>
      <FontAwesomeIcon icon={icon} className={`stat-card-icon ${iconClass}`} />
      <button onClick={onExport} className="export-button" title={`Exportar ${title}`}>
        <FontAwesomeIcon icon={faFileExcel} />
      </button>
    </div>
    <div>
      <span className="stat-card-value">{value}</span>
    </div>
  </div>
);


const Dashboard = () => {
  const [kpis, setKpis] = useState({
    projetos_ativos: 0,
    projetos_atrasados: 0,
    projetos_em_dia: 0
  });
  const [horasPorArea, setHorasPorArea] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const fetchData = () => {
    const kpisRequest = axios.get(`${API_URL}/dashboard/kpis`);
    const horasRequest = axios.get(`${API_URL}/dashboard/horas-por-area`);

    Promise.all([kpisRequest, horasRequest])
      .then(([kpisRes, horasRes]) => {
        setKpis(kpisRes.data);
        setHorasPorArea(horasRes.data);
      })
      .catch(err => {
        console.error("Erro ao buscar dados do dashboard", err);
        Swal.fire('Erro!', 'Não foi possível carregar os dados do dashboard.', 'error');
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const dispararExtracao = async () => {
    setLoading(true);
    setStatusMessage('O robô está trabalhando, isso pode levar um minuto...');
    try {
      const res = await axios.post(`${API_URL}/extrair/projetos`);
      Swal.fire('Sucesso!', res.data.mensagem, 'success');
      fetchData(); // Re-busca os dados após a extração
    } catch (err) {
      const errorMsg = err.response?.data?.mensagem || 'Ocorreu um erro desconhecido.';
      Swal.fire('Erro na Extração', errorMsg, 'error');
    }
    setLoading(false);
    setStatusMessage('');
  };

  const handleExport = async (endpoint, fileName, sheetName) => {
    try {
      const response = await axios.get(`${API_URL}${endpoint}`);
      let data = response.data;

      if (data.length === 0) {
        Swal.fire('Aviso', 'Não há dados para exportar.', 'warning');
        return;
      }
      
      // Mapear e formatar os dados para o Excel
      data = data.map(row => {
        const newRow = { ...row };
        // Formatar datas
        if (newRow.dt_inicio) newRow.dt_inicio = formatarDataBR(newRow.dt_inicio);
        if (newRow.dt_fim) newRow.dt_fim = formatarDataBR(newRow.dt_fim);
        // Formatar horas
        // A coluna para horas apontadas no export detalhado é 'horas_apontadas'
        if (newRow.horas_apontadas) newRow.horas_apontadas = formatarHoraDecimal(newRow.horas_apontadas);
        // Outras colunas de horas que podem vir em outros exports
        if (newRow.trab_apontado) newRow.trab_apontado = formatarHoraDecimal(newRow.trab_apontado);
        if (newRow.trab_prev) newRow.trab_prev = formatarHoraDecimal(newRow.trab_prev); 
        if (newRow.sld_hrs) newRow.sld_hrs = formatarHoraDecimal(newRow.sld_hrs); 
        
        return newRow;
      });

      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
      XLSX.writeFile(workbook, `${fileName}.xlsx`);

    } catch (error) {
      console.error(`Erro ao exportar dados de ${endpoint}`, error);
      Swal.fire('Erro!', 'Não foi possível gerar o arquivo Excel.', 'error');
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <h2><FontAwesomeIcon icon={faChartLine} /> Dashboard de Projetos</h2>
        <div>
          <button onClick={dispararExtracao} disabled={loading} className="update-button">
            <FontAwesomeIcon icon={loading ? faSync : faSync} spin={loading} /> {loading ? 'Atualizando...' : 'Atualizar Base'}
          </button>
          {statusMessage && <p className="status-message">{statusMessage}</p>}
        </div>
      </div>

      <div className="dashboard-grid">
        <StatCard 
          title="Projetos Ativos" 
          value={kpis.projetos_ativos}
          icon={faProjectDiagram}
          iconClass="icon-projetos"
          onExport={() => handleExport('/export/projetos', 'Projetos_Ativos', 'Projetos')}
        />
        <StatCard 
          title="Projetos Atrasados" 
          value={kpis.projetos_atrasados}
          icon={faClock}
          iconClass="icon-atrasados"
          onExport={() => handleExport('/export/projetos-por-status?status=atrasado', 'Projetos_Atrasados', 'Atrasados')}
        />
        <StatCard 
          title="Projetos Em Dia" 
          value={kpis.projetos_em_dia}
          icon={faCheckCircle}
          iconClass="icon-em-dia"
          onExport={() => handleExport('/export/projetos-por-status?status=em_dia', 'Projetos_Em_Dia', 'Em Dia')}
        />
      </div>

      <div style={{marginTop: '1.5rem'}}>
        <div className="chart-card">
          <div className="chart-card-header">
            <h3>Horas Apontadas por Área</h3>
            <button onClick={() => handleExport('/export/horas-por-area-detalhado', 'Horas_Por_Area_Detalhado', 'Lançamentos')} className="export-button" title="Exportar dados detalhados">
              <FontAwesomeIcon icon={faFileExcel} />
            </button>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={horasPorArea} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="area" interval={0} angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip cursor={{fill: 'rgba(241, 245, 249, 0.5)'}} formatter={(value) => `${formatarHoraDecimal(value)}`} />
                <Legend />
                <Bar dataKey="horas" fill="#0A86A3" name="Horas Apontadas" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;