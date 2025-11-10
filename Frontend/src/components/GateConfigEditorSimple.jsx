import React from 'react';

const GateConfigEditorSimple = () => {
  return (
    <div style={{ padding: '20px', color: 'white', background: '#002B4B', minHeight: '100vh' }}>
      <h1>🚪 Gate Configuration Editor</h1>
      <p>This is a simple test version of the gate configuration editor.</p>
      <p>If you can see this, the component is loading correctly.</p>
      
      <div style={{ marginTop: '20px', padding: '20px', background: 'rgba(76, 212, 176, 0.1)', borderRadius: '10px' }}>
        <h2>Features:</h2>
        <ul>
          <li>✅ Visual polygon drawing</li>
          <li>✅ Real-time coordinate conversion</li>
          <li>✅ Settings panel</li>
          <li>✅ Save/Load configuration</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={() => alert('Configuration saved!')}
          style={{
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #4CD4B0, #3BC4A0)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          💾 Test Save Button
        </button>
      </div>
    </div>
  );
};

export default GateConfigEditorSimple;




























