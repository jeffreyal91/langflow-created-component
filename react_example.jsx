/**
 * Ejemplo de componente React para monitorear logs en tiempo real de Langflow
 *
 * Instalación requerida:
 * npm install react
 *
 * Uso:
 * import FlowLogMonitor from './react_example';
 * <FlowLogMonitor apiUrl="http://localhost:7860" flowId="your-flow-id" />
 */

import React, { useState, useEffect, useRef } from 'react';

// Hook personalizado para manejar SSE
function useFlowSSE(apiUrl, jobId) {
  const [logs, setLogs] = useState([]);
  const [messages, setMessages] = useState([]);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('disconnected'); // disconnected | connecting | connected | error
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!apiUrl || !jobId) return;

    setStatus('connecting');
    const sseUrl = `${apiUrl}/api/v1/build/${jobId}/events`;
    console.log('Conectando a SSE:', sseUrl);

    const eventSource = new EventSource(sseUrl);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('SSE conectado');
      setStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Evento recibido:', data);

        // Agregar a eventos generales
        setEvents((prev) => [{ ...data, timestamp: new Date() }, ...prev]);

        // Procesar por tipo
        switch (data.event) {
          case 'log':
            setLogs((prev) => [{ ...data.data, timestamp: new Date() }, ...prev]);
            break;

          case 'message':
            setMessages((prev) => [{ ...data.data, timestamp: new Date() }, ...prev]);
            break;

          case 'token':
            // Acumular tokens si es necesario
            console.log('Token:', data.data.chunk);
            break;

          case 'error':
            console.error('Error del flow:', data.data);
            setStatus('error');
            break;

          case 'end':
            console.log('Flow completado');
            setStatus('completed');
            eventSource.close();
            break;
        }
      } catch (error) {
        console.error('Error parseando evento:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Error en SSE:', error);
      setStatus('error');
      eventSource.close();
    };

    // Cleanup
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [apiUrl, jobId]);

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setStatus('disconnected');
    }
  };

  const clearLogs = () => setLogs([]);
  const clearMessages = () => setMessages([]);
  const clearEvents = () => setEvents([]);

  return {
    logs,
    messages,
    events,
    status,
    disconnect,
    clearLogs,
    clearMessages,
    clearEvents,
  };
}

// Componente de Log Entry
function LogEntry({ log }) {
  const message =
    typeof log.message === 'object'
      ? JSON.stringify(log.message, null, 2)
      : log.message;

  const level = log.message?.level || 'INFO';
  const levelColors = {
    INFO: 'bg-blue-100 text-blue-800',
    DEBUG: 'bg-purple-100 text-purple-800',
    WARNING: 'bg-yellow-100 text-yellow-800',
    ERROR: 'bg-red-100 text-red-800',
  };

  return (
    <div className="border-l-4 border-blue-500 bg-gray-50 p-4 mb-3 rounded-r-lg animate-slide-in">
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-blue-600">{log.name || 'LOG'}</span>
          <span className={`text-xs px-2 py-1 rounded ${levelColors[level] || levelColors.INFO}`}>
            {level}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          {log.timestamp?.toLocaleTimeString() || new Date().toLocaleTimeString()}
        </span>
      </div>
      <pre className="bg-white p-2 rounded text-xs overflow-x-auto font-mono">
        {message}
      </pre>
    </div>
  );
}

// Componente de Message Entry
function MessageEntry({ message }) {
  return (
    <div className="border-l-4 border-green-500 bg-green-50 p-4 mb-3 rounded-r-lg animate-slide-in">
      <div className="flex justify-between items-center mb-2">
        <span className="font-bold text-green-600">{message.sender || 'System'}</span>
        <span className="text-xs text-gray-500">
          {message.timestamp?.toLocaleTimeString() || new Date().toLocaleTimeString()}
        </span>
      </div>
      <div className="text-gray-800">{message.text || JSON.stringify(message)}</div>
    </div>
  );
}

// Componente de Status Badge
function StatusBadge({ status }) {
  const statusConfig = {
    disconnected: { color: 'bg-gray-500', icon: '⚫', text: 'Desconectado' },
    connecting: { color: 'bg-yellow-500', icon: '🔄', text: 'Conectando...' },
    connected: { color: 'bg-green-500', icon: '🟢', text: 'Conectado' },
    error: { color: 'bg-red-500', icon: '🔴', text: 'Error' },
    completed: { color: 'bg-blue-500', icon: '✅', text: 'Completado' },
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  return (
    <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-white font-semibold ${config.color}`}>
      <span>{config.icon}</span>
      <span>{config.text}</span>
    </span>
  );
}

// Componente principal
export default function FlowLogMonitor({ apiUrl: initialApiUrl, flowId: initialFlowId }) {
  const [apiUrl, setApiUrl] = useState(initialApiUrl || 'http://localhost:7860');
  const [flowId, setFlowId] = useState(initialFlowId || '');
  const [inputValue, setInputValue] = useState('Test message');
  const [jobId, setJobId] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const { logs, messages, events, status, disconnect, clearLogs, clearMessages, clearEvents } =
    useFlowSSE(apiUrl, jobId);

  const executeFlow = async () => {
    if (!apiUrl || !flowId) {
      alert('Por favor ingresa la URL de la API y el Flow ID');
      return;
    }

    setIsExecuting(true);

    try {
      const response = await fetch(`${apiUrl}/api/v1/run/${flowId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_value: inputValue,
          input_type: 'chat',
          output_type: 'chat',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const newJobId = data.session_id || data.job_id;

      if (!newJobId) {
        throw new Error('No se recibió job_id del servidor');
      }

      console.log('Flow ejecutado, Job ID:', newJobId);
      setJobId(newJobId);
    } catch (error) {
      console.error('Error ejecutando flow:', error);
      alert('Error ejecutando flow: ' + error.message);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleDisconnect = () => {
    disconnect();
    setJobId(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <h1 className="text-4xl font-bold text-white text-center mb-8 drop-shadow-lg">
          🚀 Langflow Real-Time Logger Monitor
        </h1>

        {/* Configuration Panel */}
        <div className="bg-white rounded-xl shadow-2xl p-6 mb-6">
          <h2 className="text-2xl font-bold text-purple-600 mb-4">⚙️ Configuración</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                URL de Langflow API:
              </label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none"
                placeholder="http://localhost:7860"
                disabled={status === 'connected' || status === 'connecting'}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Flow ID:
              </label>
              <input
                type="text"
                value={flowId}
                onChange={(e) => setFlowId(e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none"
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                disabled={status === 'connected' || status === 'connecting'}
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Input Value (opcional):
            </label>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none"
              placeholder="Tu mensaje o input al flow"
              disabled={status === 'connected' || status === 'connecting'}
            />
          </div>

          <div className="flex gap-4 items-center">
            {status === 'disconnected' || status === 'error' || status === 'completed' ? (
              <button
                onClick={executeFlow}
                disabled={isExecuting}
                className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExecuting ? '🔄 Ejecutando...' : '🚀 Ejecutar Flow y Conectar SSE'}
              </button>
            ) : (
              <button
                onClick={handleDisconnect}
                className="flex-1 bg-red-500 text-white font-semibold py-3 px-6 rounded-lg hover:bg-red-600 transition-all"
              >
                🛑 Desconectar
              </button>
            )}

            <StatusBadge status={status} />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-6 text-center">
            <div className="text-4xl font-bold text-purple-600">{logs.length}</div>
            <div className="text-gray-600 mt-2">Logs Recibidos</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 text-center">
            <div className="text-4xl font-bold text-blue-600">{messages.length}</div>
            <div className="text-gray-600 mt-2">Mensajes</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 text-center">
            <div className="text-4xl font-bold text-green-600">{events.length}</div>
            <div className="text-gray-600 mt-2">Eventos Totales</div>
          </div>
        </div>

        {/* Logs and Messages */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Logs Panel */}
          <div className="bg-white rounded-xl shadow-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-purple-600">📝 Logs en Tiempo Real</h3>
              <button
                onClick={clearLogs}
                className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600 transition-all"
              >
                🗑️ Limpiar
              </button>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  No hay logs todavía...
                </div>
              ) : (
                logs.map((log, index) => <LogEntry key={index} log={log} />)
              )}
            </div>
          </div>

          {/* Messages Panel */}
          <div className="bg-white rounded-xl shadow-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-green-600">💬 Mensajes</h3>
              <button
                onClick={clearMessages}
                className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600 transition-all"
              >
                🗑️ Limpiar
              </button>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  No hay mensajes todavía...
                </div>
              ) : (
                messages.map((message, index) => <MessageEntry key={index} message={message} />)
              )}
            </div>
          </div>
        </div>

        {/* All Events Panel */}
        <div className="bg-white rounded-xl shadow-2xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-700">🔔 Todos los Eventos (Raw JSON)</h3>
            <button
              onClick={clearEvents}
              className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600 transition-all"
            >
              🗑️ Limpiar
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {events.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                No hay eventos todavía...
              </div>
            ) : (
              events.map((event, index) => (
                <div key={index} className="bg-gray-50 p-3 mb-2 rounded-lg border border-gray-200">
                  <div className="flex justify-between mb-1">
                    <span className="font-bold text-gray-700">{event.event}</span>
                    <span className="text-xs text-gray-500">
                      {event.timestamp?.toLocaleTimeString()}
                    </span>
                  </div>
                  <pre className="text-xs overflow-x-auto font-mono bg-white p-2 rounded">
                    {JSON.stringify(event, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-in {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
