# 🎯 Respuestas Rápidas - Real-Time Logger para Langflow

## ❓ Pregunta 1: ¿Es un flow aparte o lo incluyo en mi flow?

### ✅ **RESPUESTA: LO INCLUYES EN TU FLOW**

El componente **RealTimeLogger** NO es un flow aparte. Es un componente que agregas **DENTRO** de tu flow existente, como cualquier otro nodo.

**Ejemplo visual:**

```
TU FLOW ACTUAL:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Chat Input  │ --> │     LLM     │ --> │ Chat Output │
└─────────────┘     └─────────────┘     └─────────────┘

TU FLOW CON LOGGER:
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Chat Input  │ --> │ RealTimeLogger   │ --> │     LLM     │ --> │ RealTimeLogger   │ --> │ Chat Output │
└─────────────┘     │ (Log entrada)    │     └─────────────┘     │ (Log salida)     │     └─────────────┘
                    └──────────────────┘                          └──────────────────┘
```

**Cómo usarlo:**

1. Abre tu flow en Langflow
2. Agrega el componente **RealTimeLogger** donde quieras capturar datos
3. Conecta el output del componente anterior al input del Logger
4. Conecta el output del Logger al siguiente componente
5. ¡Listo! El Logger capturará y transmitirá los datos sin interrumpir el flujo

---

## ❓ Pregunta 2: ¿Cuál es el endpoint para que el frontend se suscriba?

### ✅ **RESPUESTA:**

```
GET /api/v1/build/{job_id}/events
```

### Pasos completos:

#### 1. **Ejecutar el Flow (obtener job_id)**

```javascript
// POST al API de Langflow
const response = await fetch('http://localhost:7860/api/v1/run/{flow_id}', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input_value: 'Tu mensaje',
    input_type: 'chat',
    output_type: 'chat',
  })
});

const data = await response.json();
const jobId = data.session_id || data.job_id; // Este es el que necesitas
```

#### 2. **Conectar SSE con el job_id**

```javascript
// Conectar a los eventos con el job_id obtenido
const eventSource = new EventSource(
  `http://localhost:7860/api/v1/build/${jobId}/events`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evento recibido:', data);

  // Manejar logs
  if (data.event === 'log') {
    console.log('📝 Log:', data.data);
  }

  // Manejar mensajes
  if (data.event === 'message') {
    console.log('💬 Message:', data.data);
  }
};
```

### Endpoints alternativos (dependiendo de tu versión de Langflow):

```bash
# Opción 1: Por job_id (Recomendado)
GET /api/v1/build/{job_id}/events

# Opción 2: Por flow_id y vertex_id (si conoces el vértice específico)
GET /api/v1/build/{flow_id}/stream/{vertex_id}

# Opción 3: Usando session_id (en algunas versiones)
GET /api/v1/monitor/builds/{session_id}/stream
```

---

## ❓ Pregunta 3: ¿Qué eventos voy a recibir?

### ✅ **RESPUESTA: Estos son los eventos que recibirás**

### Formato general:

Todos los eventos vienen en formato **NDJSON** (Newline Delimited JSON):

```json
{"event": "tipo_evento", "data": {...}}
```

### Tipos de eventos:

#### 1. **`log`** - Logs generados por tu componente

```json
{
  "event": "log",
  "data": {
    "name": "FLOW_LOG",
    "message": {
      "prefix": "USER_INPUT",
      "level": "INFO",
      "message": "Processing data",
      "timestamp": "2025-11-13T12:00:00.000Z",
      "metadata": {
        "component_id": "xxx",
        "component_name": "RealTimeLogger"
      }
    },
    "type": "object",
    "output": "output",
    "component_id": "component-id-here"
  }
}
```

**Cuándo se genera:** Cada vez que tu `RealTimeLogger` llama a `self.log()`

---

#### 2. **`message`** - Mensajes enviados por componentes

```json
{
  "event": "message",
  "data": {
    "text": "Contenido del mensaje",
    "sender": "RealTimeLogger",
    "session_id": "xxx",
    "timestamp": "2025-11-13T12:00:00.000Z"
  }
}
```

**Cuándo se genera:** Cuando tu componente llama a `self.send_message()`

---

#### 3. **`token`** - Streaming de tokens (para LLMs)

```json
{
  "event": "token",
  "data": {
    "chunk": "texto",
    "id": "message-id"
  }
}
```

**Cuándo se genera:** Cuando un LLM está generando respuestas en streaming

---

#### 4. **`error`** - Errores durante la ejecución

```json
{
  "event": "error",
  "data": {
    "error": "Mensaje de error",
    "traceback": "...",
    "component_id": "xxx"
  }
}
```

**Cuándo se genera:** Cuando hay un error en algún componente del flow

---

#### 5. **`end`** - Fin de la ejecución del flow

```json
{
  "event": "end",
  "data": {
    "outputs": {...},
    "duration": 1.234
  }
}
```

**Cuándo se genera:** Cuando el flow completa su ejecución

---

## 🚀 Código completo para copiar y pegar

### Vanilla JavaScript (HTML puro)

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Langflow Logger Monitor</h1>
  <button onclick="startMonitoring()">Iniciar Monitoreo</button>
  <div id="logs"></div>

  <script>
    async function startMonitoring() {
      // 1. Ejecutar el flow
      const response = await fetch('http://localhost:7860/api/v1/run/YOUR_FLOW_ID', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_value: 'Test',
          input_type: 'chat',
          output_type: 'chat',
        })
      });

      const data = await response.json();
      const jobId = data.session_id || data.job_id;

      // 2. Conectar SSE
      const eventSource = new EventSource(
        `http://localhost:7860/api/v1/build/${jobId}/events`
      );

      // 3. Escuchar eventos
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.event === 'log') {
          console.log('📝 Log:', data.data);
          document.getElementById('logs').innerHTML +=
            `<div>${data.data.name}: ${JSON.stringify(data.data.message)}</div>`;
        }

        if (data.event === 'end') {
          console.log('✅ Completado');
          eventSource.close();
        }
      };
    }
  </script>
</body>
</html>
```

### React

```jsx
import { useEffect, useState } from 'react';

function FlowMonitor({ flowId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function start() {
      // 1. Ejecutar flow
      const res = await fetch(`http://localhost:7860/api/v1/run/${flowId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_value: 'Test', input_type: 'chat', output_type: 'chat' })
      });

      const { session_id, job_id } = await res.json();
      const jobId = session_id || job_id;

      // 2. Conectar SSE
      const sse = new EventSource(`http://localhost:7860/api/v1/build/${jobId}/events`);

      sse.onmessage = (e) => {
        const { event, data } = JSON.parse(e.data);
        if (event === 'log') {
          setLogs(prev => [...prev, data]);
        }
        if (event === 'end') sse.close();
      };

      return () => sse.close();
    }

    start();
  }, [flowId]);

  return (
    <div>
      {logs.map((log, i) => (
        <div key={i}>{log.name}: {JSON.stringify(log.message)}</div>
      ))}
    </div>
  );
}
```

---

## 📌 Resumen Ultra-Rápido

| Pregunta | Respuesta |
|----------|-----------|
| **¿Es un flow aparte?** | ❌ NO. Lo incluyes DENTRO de tu flow como un componente más |
| **¿Endpoint SSE?** | `GET /api/v1/build/{job_id}/events` |
| **¿Cómo obtener job_id?** | Ejecuta el flow con POST, te devuelve el job_id en la respuesta |
| **¿Qué eventos recibo?** | `log`, `message`, `token`, `error`, `end` |
| **¿Formato?** | NDJSON (JSON separado por líneas) |

---

## 🎓 Próximos Pasos

1. ✅ Carga `real_time_logger.py` en Langflow como Custom Component
2. ✅ Agrega `RealTimeLogger` a tu flow donde necesites logs
3. ✅ Usa `frontend_example.html` para probar la conexión SSE
4. ✅ Adapta el código React (`react_example.jsx`) a tu app
5. ✅ Lee `README.md` para detalles avanzados

---

**¿Dudas?** Revisa los archivos de ejemplo incluidos:
- `real_time_logger.py` - El componente completo
- `frontend_example.html` - Demo HTML standalone
- `react_example.jsx` - Componente React completo
- `README.md` - Documentación completa
