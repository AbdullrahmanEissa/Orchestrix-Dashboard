import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Server, Cpu, MemoryStick } from 'lucide-react';
import './App.css'; // Ensure this file exists for basic styling

function App() {
  // Store live and historical data for each server.
  const [serversData, setServersData] = useState({});

  useEffect(() => {
    // Connect to the backend WebSocket.
    const ws = new WebSocket("ws://localhost:3000/ws/dashboard");

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.event === "initial_state") {
        // Optional: handle initial data snapshot here.
        console.log("Connected to Backend:", message);
      } 
      else if (message.event === "server_update") {
        const serverName = message.server_name;
        const payload = message.payload;

        setServersData(prevData => {
          const currentServer = prevData[serverName] || { history: [], current: null };
          
          // Build a new chart point from incoming data.
          const newPoint = {
            time: new Date().toLocaleTimeString('en-GB', { hour12: false }), // 24-hour format
            cpu: payload.system?.cpu_percent || 0,
            ram: payload.system?.memory_percent || 0
          };

          // Keep only the latest 15 readings for chart clarity.
          const updatedHistory = [...currentServer.history, newPoint].slice(-15);

          return {
            ...prevData,
            [serverName]: {
              current: payload,
              history: updatedHistory
            }
          };
        });
      }
    };

    return () => ws.close(); // Close connection on component unmount.
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', backgroundColor: '#f4f7f6', minHeight: '100vh' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#2c3e50' }}>
        <Server size={32} />
        Server Orchestration Dashboard
      </h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginTop: '20px' }}>
        {Object.entries(serversData).map(([name, data]) => (
          <div key={name} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            
            {/* Card header (server name) */}
            <div style={{ borderBottom: '2px solid #eee', paddingBottom: '10px', marginBottom: '15px' }}>
              <h2 style={{ margin: 0, color: '#34495e' }}>{name}</h2>
              <small style={{ color: '#7f8c8d' }}>Last seen: {new Date().toLocaleTimeString()}</small>
            </div>

            {/* Live metrics */}
            <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
              <div style={{ textAlign: 'center', color: '#e74c3c' }}>
                <Cpu size={24} />
                <h3 style={{ margin: '5px 0' }}>{data.current.system?.cpu_percent}%</h3>
                <small>CPU Usage</small>
              </div>
              <div style={{ textAlign: 'center', color: '#3498db' }}>
                <MemoryStick size={24} />
                <h3 style={{ margin: '5px 0' }}>{data.current.system?.memory_percent}%</h3>
                <small>RAM Usage</small>
              </div>
            </div>

            {/* Chart (Recharts) */}
            <div style={{ height: '200px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{fontSize: 10}} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="cpu" stroke="#e74c3c" strokeWidth={2} dot={false} name="CPU %" />
                  <Line type="monotone" dataKey="ram" stroke="#3498db" strokeWidth={2} dot={false} name="RAM %" />
                </LineChart>
              </ResponsiveContainer>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}

export default App;