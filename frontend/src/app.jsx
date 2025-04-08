import { useState } from 'react';
import axios from 'axios';

function App() {
  const [desc, setDesc] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (desc.length < parseInt(process.env.REACT_APP_MIN_DESC_LENGTH)) {
      setError(`El texto debe tener al menos ${process.env.REACT_APP_MIN_DESC_LENGTH} caracteres`);
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/analyze`, {
        name: 'Usuario Demo',
        email: 'demo@fintech.com',
        description: desc
      });
      setResult(response.data.result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar la solicitud');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: '0 auto' }}>
      <h2 style={{ color: '#2c3e50' }}>Fintech Digital</h2>
      <p>Ingrese los datos financieros a analizar:</p>
      
      <textarea 
        value={desc}
        onChange={(e) => setDesc(e.target.value)} 
        rows="5" 
        style={{ width: '100%', padding: 8 }}
        placeholder={`Mínimo ${process.env.REACT_APP_MIN_DESC_LENGTH} caracteres`}
      />
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <button 
        onClick={analyze}
        disabled={loading}
        style={{
          background: '#3498db',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: 4,
          cursor: 'pointer',
          marginTop: 10
        }}
      >
        {loading ? 'Procesando...' : 'Analizar'}
      </button>
      
      {result && (
        <div style={{ marginTop: 20, padding: 15, background: '#f8f9fa', borderRadius: 4 }}>
          <h3>Resultado del análisis:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default App;
