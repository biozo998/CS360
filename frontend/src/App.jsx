import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './App.css';

function App() {
  const [dados, setDados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState('Sistema pronto.');

  const atualizarDashboard = () => {
    axios.get('http://localhost:5000/api/dash/horas-por-gerente')
      .then(res => setDados(res.data))
      .catch(err => console.error("Erro ao buscar dados", err));
  };

  useEffect(() => {
    atualizarDashboard();
  }, []);

  const dispararExtracao = async () => {
    setLoading(true);
    setMensagem('O robô está trabalhando no PSOffice... aguarde.');
    try {
      const res = await axios.post('http://localhost:5000/api/extrair/projetos');
      setMensagem(res.data.mensagem);
      atualizarDashboard(); // Atualiza o gráfico após extrair
    } catch (err) {
      setMensagem('Erro na extração. Verifique o backend.');
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <header className="header">
        <div className="logo">CS<span>360</span></div>
        <div className="status-indicator">Status: {mensagem}</div>
        <button onClick={dispararExtracao} disabled={loading}>
          {loading ? 'Extraindo...' : 'Atualizar Dados Agora'}
        </button>
      </header>

      <div className="card">
        <h3>Carga de Horas por Gerente</h3>
        <p style={{color: '#666', fontSize: '14px', marginBottom: '20px'}}>
          Horas apontadas em projetos ativos (Código CS360)
        </p>
        
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={dados} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="gerente" />
              <YAxis />
              <Tooltip cursor={{fill: '#f4f7f9'}} />
              <Bar dataKey="horas" fill="#0A86A3" radius={[4, 4, 0, 0]}>
                {dados.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#30B199' : '#0A86A3'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Aqui poderemos adicionar mais cards futuramente */}
    </div>
  );
}

export default App;