import { useState, useEffect } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import './CadAtividades.css';

const CadAtividades = () => {
  const [atividades, setAtividades] = useState([]);
  const [form, setForm] = useState({ codigo: '', tipo_hora: 'CS', descricao: '', estrategia: 'Consolidar' });
  const [editando, setEditando] = useState(false);

  const carregar = () => {
    axios.get('http://localhost:5000/api/cadastros/atividades')
      .then(res => setAtividades(res.data));
  };

  useEffect(() => carregar(), []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/cadastros/atividades', form);
      Swal.fire({ icon: 'success', title: 'Salvo!', text: 'Atividade registada com sucesso.', timer: 2000, showConfirmButton: false });
      setForm({ codigo: '', tipo_hora: 'CS', descricao: '', estrategia: 'Consolidar' });
      setEditando(false);
      carregar();
    } catch (err) { Swal.fire('Erro', 'Não foi possível salvar os dados.', 'error'); }
  };

  const prepararEdicao = (a) => {
    setForm(a);
    setEditando(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const excluirAtividade = (codigo) => {
    Swal.fire({
      title: 'Confirmar Exclusão',
      text: `Deseja remover a atividade ${codigo}?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#0A86A3',
      cancelButtonColor: '#EF4444',
      confirmButtonText: 'Sim, excluir',
      cancelButtonText: 'Cancelar',
      reverseButtons: true
    }).then(async (result) => {
      if (result.isConfirmed) {
        await axios.delete(`http://localhost:5000/api/cadastros/atividades/${codigo}`);
        carregar();
        Swal.fire('Excluído!', 'O registro foi removido.', 'success');
      }
    });
  };

  return (
    <div className="page-container">
      <div className="view-card">
        <h2>{editando ? 'Editar Atividade' : 'Gestão de Atividades e Estratégia'}</h2>
        
        <form onSubmit={handleSubmit} className="form-grid">
          <div className="form-group">
            <label>Cód. Resultado</label>
            <input value={form.codigo} disabled={editando} onChange={e => setForm({...form, codigo: e.target.value})} placeholder="Ex: 062" required />
          </div>
          <div className="form-group">
            <label>Tipo Hora</label>
            <select value={form.tipo_hora} onChange={e => setForm({...form, tipo_hora: e.target.value})}>
              <option value="CS">CS</option>
              <option value="CLIENTE">CLIENTE</option>
            </select>
          </div>
          <div className="form-group">
            <label>Estratégia</label>
            <select value={form.estrategia} onChange={e => setForm({...form, estrategia: e.target.value})}>
              <option value="Expandir">Expandir</option>
              <option value="Fortalecer">Fortalecer</option>
              <option value="Consolidar">Consolidar</option>
            </select>
          </div>
          <div className="form-group" style={{gridColumn: 'span 2'}}>
            <label>Descrição</label>
            <input value={form.descricao} onChange={e => setForm({...form, descricao: e.target.value})} placeholder="Descreva a atividade..." />
          </div>
          <button type="submit" className="btn-save">{editando ? 'Atualizar' : 'Salvar'}</button>
        </form>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Cód</th>
                <th>Tipo</th>
                <th>Estratégia</th>
                <th>Descrição</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {atividades.map(a => (
                <tr key={a.codigo}>
                  <td><strong>{a.codigo}</strong></td>
                  <td><span className={`badge badge-${a.tipo_hora.toLowerCase()}`}>{a.tipo_hora}</span></td>
                  <td><span className={`badge badge-${a.estrategia.toLowerCase()}`}>{a.estrategia}</span></td>
                  <td>{a.descricao}</td>
                  <td className="actions-cell">
                    <button className="btn-edit" onClick={() => prepararEdicao(a)}>Editar</button>
                    <button className="btn-delete" onClick={() => excluirAtividade(a.codigo)}>Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CadAtividades;