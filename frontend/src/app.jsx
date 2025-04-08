import { useState } from 'react';
import axios from 'axios';

function App() {
  const [desc, setDesc] = useState('');
  const [result, setResult] = useState('');

  const analyze = async () => {
    const response = await axios.post('http://localhost:8000/analyze', {
      name: 'Frank',
      email: 'frank@example.com',
      description: desc
    });
    setResult(response.data.result);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Fintech Digital</h2>
      <textarea onChange={(e) => setDesc(e.target.value)} rows="5" cols="40" />
      <br />
      <button onClick={analyze}>Analizar</button>
      <p><strong>Resultado IA:</strong> {result}</p>
    </div>
  );
}

export default App;
