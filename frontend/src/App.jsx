import { useState } from 'react';
import Sidebar from './components/Sidebar'; // Importação do novo componente
import Dashboard from './pages/Dashboard';
import CadGerentes from './pages/CadGerentes';
import CadAtividades from './pages/CadAtividades';
import './App.css';

function App() {
  const [telaAtiva, setTelaAtiva] = useState('dashboard');

  return (
    <div className="app-layout">
      {/* Menu Lateral Profissional */}
      <Sidebar telaAtiva={telaAtiva} setTelaAtiva={setTelaAtiva} />
      
      {/* Área de Conteúdo Dinâmico */}
      <main className="main-content">
        {telaAtiva === 'dashboard' && <Dashboard />}
        {telaAtiva === 'gerentes' && <CadGerentes />}
        {telaAtiva === 'atividades' && <CadAtividades />}
      </main>
    </div>
  );
}

export default App;