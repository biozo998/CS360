import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [dados, setDados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState('Sistema pronto.');

  const atualizarDashboard = () => {
    // Note que agora estamos usando a rota que busca os nomes cadastrados!
    axios.get('http://localhost:5000/api/dash/horas-por-gerente')
      .then(res => setDados(res.data))
      .catch(err => console.error("Erro ao buscar dados", err));
  };

  useEffect(() => {
    atualizarDashboard();
  }, []);

  const dispararExtracao = async () => {
    setLoading(true);
    setMensagem('O robô está trabalhando no PSOffice...');
    try {
      const res = await axios.post('http://localhost:5000/api/extrair/projetos');
      setMensagem(res.data.mensagem);
      atualizarDashboard();
    } catch (err) {
      setMensagem('Erro na extração.');
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="header-dashboard" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
         <h2><i className="fas fa-chart-line"></i> Performance de Projetos</h2>
         <button onClick={dispararExtracao} disabled={loading}>
            {loading ? 'Extraindo...' : 'Atualizar Base PSOffice'}
         </button>
      </div>

      <div className="card">
        <h3>Carga de Horas por Gerente</h3>
        <p style={{color: '#666', fontSize: '14px', marginBottom: '20px'}}>Status: {mensagem}</p>
        
      <div className="chart-container-fixed">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={dados}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="gerente" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="horas" fill="#0A86A3" radius={[4, 4, 0, 0]}>
              {dados.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 0 ? '#30B199' : '#0A86A3'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      </div>
    </div>
  );
};

export default Dashboard;