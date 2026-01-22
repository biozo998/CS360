import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine, faUsers, faTasks } from '@fortawesome/free-solid-svg-icons';

const Sidebar = ({ telaAtiva, setTelaAtiva }) => {
  return (
    <aside className="sidebar">
      <div className="logo-container">
        CS<span>360</span>
      </div>
      
      <nav className="nav-links">
        <button 
          className={`nav-item ${telaAtiva === 'dashboard' ? 'active' : ''}`}
          onClick={() => setTelaAtiva('dashboard')}
        >
          <FontAwesomeIcon icon={faChartLine} /> 
          <span>Dashboard</span>
        </button>

        <div className="nav-section-title">Cadastros</div>

        <button 
          className={`nav-item ${telaAtiva === 'gerentes' ? 'active' : ''}`}
          onClick={() => setTelaAtiva('gerentes')}
        >
          <FontAwesomeIcon icon={faUsers} />
          <span>Gerentes</span>
        </button>

        <button 
          className={`nav-item ${telaAtiva === 'atividades' ? 'active' : ''}`}
          onClick={() => setTelaAtiva('atividades')}
        >
          <FontAwesomeIcon icon={faTasks} />
          <span>Atividades</span>
        </button>
      </nav>

      <div className="sidebar-footer">
        <small>v1.0.0 | CS-Integra</small>
      </div>
    </aside>
  );
};

export default Sidebar;