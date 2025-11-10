import React from 'react';

const TestPage = () => {
  return (
    <div style={{ 
      padding: '20px', 
      color: 'white', 
      background: 'linear-gradient(135deg, #002B4B, #00578A)', 
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>🧪 Test Page</h1>
      <p>If you can see this page, React is working correctly!</p>
      
      <div style={{ 
        marginTop: '20px', 
        padding: '20px', 
        background: 'rgba(76, 212, 176, 0.2)', 
        borderRadius: '10px',
        border: '1px solid rgba(76, 212, 176, 0.3)'
      }}>
        <h2>✅ System Status:</h2>
        <ul>
          <li>React: Working</li>
          <li>CSS: Working</li>
          <li>Routing: Working</li>
          <li>Components: Working</li>
        </ul>
      </div>
      
      <button 
        onClick={() => alert('JavaScript is working!')}
        style={{
          marginTop: '20px',
          padding: '15px 30px',
          background: 'linear-gradient(135deg, #4CD4B0, #3BC4A0)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '16px',
          fontWeight: 'bold'
        }}
      >
        🎯 Test JavaScript
      </button>
    </div>
  );
};

export default TestPage;




























