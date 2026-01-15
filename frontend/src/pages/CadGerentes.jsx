import { useState, useEffect } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import './CadGerentes.css';

const CadGerentes = () => {
  const [gerentes, setGerentes] = useState([]);
  const [form, setForm] = useState({ codigo: '', nome: '', area: '' });
  const [editando, setEditando] = useState(false);

  const carregar = () => {
    axios.get('http://localhost:5000/api/cadastros/gerentes').then(res => setGerentes(res.data));
  };

  useEffect(() => carregar(), []);

  const carregarGerentes = () => {
    axios.get('http://localhost:5000/api/cadastros/gerentes')
      .then(res => setGerentes(res.data))
      .catch(err => console.error("Erro ao carregar gerentes:", err));
  };

  useEffect(() => carregarGerentes(), []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/cadastros/gerentes', form);
      setForm({ codigo: '', nome: '', area: '' });
      setEditando(false);
      carregarGerentes();
    } catch (err) { alert("Erro ao salvar gerente."); }
  };

  const prepararEdicao = (g) => {
    setForm(g);
    setEditando(true);
    // Rola para o topo para facilitar a edição no formulário
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const excluirGerente = (codigo) => {
      // Confirmação Profissional
      Swal.fire({
        title: 'Tem certeza?',
        text: `O gerente ${codigo} será removido permanentemente.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#0A86A3',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
      }).then(async (result) => {
        if (result.isConfirmed) {
          await axios.delete(`http://localhost:5000/api/cadastros/gerentes/${codigo}`);
          carregar();
          Swal.fire('Excluído!', 'O registro foi removido.', 'success');
        }
      });
    };

  return (
    <div className="page-container">
    <div className="view-card">
      <h2>{editando ? 'Editar Gerente' : 'Cadastro de Gerentes da Tarefa'}</h2>
      
      <form onSubmit={handleSubmit} className="form-grid">
        <div className="form-group">
          <label>Cód. PSOffice</label>
          <input 
            value={form.codigo} 
            onChange={e => setForm({...form, codigo: e.target.value})} 
            placeholder="Ex: 033" 
            required 
            disabled={editando} // Impede mudar o código durante edição
          />
        </div>
        <div className="form-group">
          <label>Nome Completo</label>
          <input 
            value={form.nome} 
            onChange={e => setForm({...form, nome: e.target.value})} 
            placeholder="Ex: Antonio Nunes" 
            required 
          />
        </div>
        <div className="form-group">
          <label>Área de Atuação</label>
          <input 
            value={form.area} 
            onChange={e => setForm({...form, area: e.target.value})} 
            placeholder="Ex: Administrativo" 
            required 
          />
        </div>
        <div style={{ display: 'flex', gap: '10px', alignSelf: 'flex-end' }}>
          <button type="submit" className="btn-save">
            {editando ? 'Atualizar' : 'Salvar Gerente'}
          </button>
          {editando && (
            <button 
              type="button" 
              onClick={() => {setEditando(false); setForm({codigo:'', nome:'', area:''})}}
              style={{ background: '#64748B', color: 'white' }}
              className="btn-save"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th style={{ width: '232px' }}>Nome do Gerente</th>
              <th>Área</th>
              <th style={{ textAlign: 'right' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {gerentes.map(g => (
              <tr key={g.codigo}>
                <td><strong>{g.codigo}</strong></td>
                <td>{g.nome}</td>
                <td>{g.area}</td>
                <td style={{ textAlign: 'right' }}>
                  <button className="btn-edit" onClick={() => prepararEdicao(g)}>Editar</button>
                  <button className="btn-delete" onClick={() => excluirGerente(g.codigo)}>Excluir</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div></div>
  );
};

export default CadGerentes;