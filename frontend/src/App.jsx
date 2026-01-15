import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import CadGerentes from './pages/CadGerentes';
import CadAtividades from './pages/CadAtividades';
import './App.css';

function App() {
  const [telaAtiva, setTelaAtiva] = useState('dashboard');

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="logo">CS<span>360</span></div>
        <nav>
          <button onClick={() => setTelaAtiva('dashboard')} className={telaAtiva === 'dashboard' ? 'active' : ''}>
            <i className="fas fa-chart-line"></i> Dashboard
          </button>
          <button onClick={() => setTelaAtiva('gerentes')} className={telaAtiva === 'gerentes' ? 'active' : ''}>
            <i className="fas fa-users"></i> Cad. Gerentes
          </button>
          <button onClick={() => setTelaAtiva('atividades')} className={telaAtiva === 'atividades' ? 'active' : ''}>
            <i className="fas fa-tasks"></i> Cad. Atividades
          </button>
        </nav>
      </aside>

      <main className="main-content">
        {telaAtiva === 'dashboard' && <Dashboard />}
        {telaAtiva === 'gerentes' && <CadGerentes />}
        {telaAtiva === 'atividades' && <CadAtividades />}
      </main>
    </div>
  );
}

export default App;