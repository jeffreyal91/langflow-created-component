# Real-Time Logger Component para Langflow

Componente personalizado para Langflow que captura y transmite logs en tiempo real vía Server-Sent Events (SSE).

## 📋 Componentes Incluidos

### 1. **RealTimeLogger** (Recomendado)
Logger que puedes insertar en cualquier punto de tu flow para capturar datos.

### 2. **FlowMonitor**
Monitor global para capturar eventos de inicio/fin del flow y métricas.

### 3. **CustomEventLogger**
Logger para eventos personalizados con formato JSON.

---

## 🚀 Instalación y Uso

### Paso 1: Cargar el Componente en Langflow

Hay dos formas de usar este componente:

#### Opción A: Como Custom Component (Recomendado)

1. Abre Langflow
2. Ve a la sección de **Custom Components**
3. Carga el archivo `real_time_logger.py`
4. Los 3 componentes aparecerán en tu paleta de componentes

#### Opción B: Copiar el código directamente

1. En Langflow, crea un nuevo **Custom Component**
2. Copia el código de `real_time_logger.py`
3. Pégalo en el editor
4. Guarda el componente

---

## 📊 ¿Cómo se Usa en un Flow?

### ✅ **SE INCLUYE DENTRO DE TU FLOW** (No es un flow aparte)

El componente **RealTimeLogger** se comporta como cualquier otro componente de Langflow:

```
[Input] → [RealTimeLogger] → [Tu Procesamiento] → [RealTimeLogger] → [Output]
```

**Ejemplo de Flow Real:**

```
┌─────────────┐
│ Chat Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ RealTimeLogger  │ ← Log entrada del usuario
│ (prefix: USER)  │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ LLM (OpenAI)│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ RealTimeLogger  │ ← Log respuesta del LLM
│ (prefix: LLM)   │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ Chat Output │
└─────────────┘
```

### Configuración del Componente

Al agregar **RealTimeLogger** a tu flow, puedes configurar:

- **Input Data**: Conecta la salida del componente anterior
- **Log Prefix**: Nombre identificador (ej: "USER_INPUT", "LLM_RESPONSE")
- **Log Level**: INFO, DEBUG, WARNING, ERROR
- **Include Timestamp**: true/false
- **Include Metadata**: true/false (ID del componente, nombre, etc)
- **Log Input Data**: true/false (loguear el contenido completo)

---

## 🌐 Endpoint SSE para el Frontend

### **Endpoint Principal:**

```
GET /api/v1/build/{flow_id}/stream/{vertex_id}
```

O si estás ejecutando un build job:

```
GET /api/v1/build/{job_id}/events
```

### Parámetros:

- `flow_id`: ID del flow que está ejecutándose
- `vertex_id`: ID del nodo/vértice específico (opcional)
- `job_id`: ID del job de ejecución del flow

---

## 💻 Ejemplo de Frontend (JavaScript/React)

### Conexión SSE Básica

```javascript
// Conectar al stream de eventos del flow
const flowId = 'tu-flow-id';
const jobId = 'tu-job-id'; // Obtenido al ejecutar el flow

const eventSource = new EventSource(
  `http://localhost:7860/api/v1/build/${jobId}/events`
);

// Escuchar eventos de logs
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.event === 'log') {
    console.log('📝 Log recibido:', data.data);

    // El formato del log es:
    // {
    //   name: "FLOW_LOG",
    //   message: { ... },
    //   type: "object",
    //   output: "output_name",
    //   component_id: "component-id"
    // }
  }
});

// Escuchar mensajes
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.event === 'message') {
    console.log('💬 Message recibido:', data.data);
  }
});

// Escuchar tokens (si hay streaming de LLM)
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.event === 'token') {
    console.log('🔤 Token recibido:', data.data.chunk);
  }
});

// Manejar errores
eventSource.onerror = (error) => {
  console.error('❌ Error en SSE:', error);
  eventSource.close();
};

// Cerrar conexión cuando termine
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.event === 'end') {
    console.log('✅ Flow completado');
    eventSource.close();
  }
});
```

### Ejemplo con React Hook

```javascript
import { useEffect, useState } from 'react';

function useFlowLogs(jobId) {
  const [logs, setLogs] = useState([]);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(
      `http://localhost:7860/api/v1/build/${jobId}/events`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.event) {
        case 'log':
          setLogs((prev) => [...prev, data.data]);
          break;
        case 'message':
          setMessages((prev) => [...prev, data.data]);
          break;
        case 'end':
          eventSource.close();
          break;
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [jobId]);

  return { logs, messages };
}

// Uso:
function FlowMonitor({ jobId }) {
  const { logs, messages } = useFlowLogs(jobId);

  return (
    <div>
      <h2>Logs en Tiempo Real</h2>
      {logs.map((log, i) => (
        <div key={i}>
          <strong>{log.name}:</strong> {JSON.stringify(log.message)}
        </div>
      ))}
    </div>
  );
}
```

---

## 📡 Formato de Eventos SSE

Los eventos vienen en formato **NDJSON** (Newline Delimited JSON):

```json
{"event": "log", "data": {"name": "FLOW_LOG", "message": {...}, "component_id": "..."}}
{"event": "message", "data": {"text": "...", "sender": "..."}}
{"event": "token", "data": {"chunk": "...", "id": "..."}}
{"event": "end", "data": {}}
```

### Tipos de Eventos:

| Evento | Descripción |
|--------|-------------|
| `log` | Log generado por `self.log()` |
| `message` | Mensaje enviado por `self.send_message()` |
| `token` | Token de streaming (LLMs) |
| `error` | Error durante ejecución |
| `end` | Fin de la ejecución del flow |

---

## 🎯 Casos de Uso

### 1. **Debug de Flows Complejos**
Coloca RealTimeLogger en múltiples puntos para ver qué datos pasan por cada etapa.

### 2. **Monitoring de Producción**
Usa FlowMonitor al inicio del flow para capturar métricas y tiempos de ejecución.

### 3. **Analytics Custom**
Usa CustomEventLogger para enviar eventos específicos (ej: "user_clicked", "payment_processed").

### 4. **Dashboard en Tiempo Real**
Conecta el SSE a un dashboard para visualizar el estado del flow en tiempo real.

---

## 🔧 Troubleshooting

### El frontend no recibe eventos

1. **Verifica que el flow esté ejecutándose**: El SSE solo funciona mientras el flow está activo
2. **Confirma el job_id correcto**: Al ejecutar un flow, Langflow retorna un `job_id`, úsalo en el endpoint
3. **Revisa CORS**: Si tu frontend está en otro dominio, configura CORS en Langflow

### Los logs no aparecen

1. **Verifica que `log_input_data = True`**: Si está en false, no logueará los datos
2. **Conecta el componente correctamente**: El `input_data` debe estar conectado a la salida del componente anterior
3. **Revisa la consola del navegador**: Los errores SSE aparecen ahí

### El componente no aparece en Langflow

1. **Verifica la sintaxis**: Asegúrate de que no hay errores en el código
2. **Revisa los imports**: Deben coincidir con tu versión de Langflow
3. **Reinicia Langflow**: A veces necesita recargar los componentes custom

---

## 📝 Ejemplo Completo de Integración

### Backend (Ejecutar Flow)

```python
import requests

# Ejecutar flow
response = requests.post(
    'http://localhost:7860/api/v1/run/YOUR_FLOW_ID',
    json={
        'input_value': 'Hola, quiero hacer una consulta',
        'input_type': 'chat',
        'output_type': 'chat',
    }
)

job_id = response.json()['job_id']
print(f"Job ID: {job_id}")
```

### Frontend (Recibir Logs)

```javascript
const jobId = 'el-job-id-del-response';

const sse = new EventSource(
  `http://localhost:7860/api/v1/build/${jobId}/events`
);

sse.onmessage = (e) => {
  const { event, data } = JSON.parse(e.data);

  if (event === 'log') {
    console.log(`[${data.name}]`, data.message);
    // Actualizar UI con el log
  }
};
```

---

## 🎨 Personalización Avanzada

### Agregar Logs Personalizados

Puedes modificar el componente para agregar logs adicionales:

```python
# En el método process_and_log():
self.log(
    message={
        "custom_field": "mi valor",
        "otro_campo": 123,
    },
    name="MI_LOG_CUSTOM"
)
```

### Filtrar Logs en el Frontend

```javascript
sse.onmessage = (e) => {
  const { event, data } = JSON.parse(e.data);

  // Solo logs que empiecen con "USER"
  if (event === 'log' && data.name.startsWith('USER')) {
    console.log('User log:', data);
  }
};
```

---

## 📚 Referencias

- [Langflow Docs](https://docs.langflow.org/)
- [Server-Sent Events MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

---

## 🤝 Contribuciones

Si encuentras bugs o quieres mejorar el componente, siéntete libre de modificarlo.

---

## ⚡ Quick Start

1. **Carga `real_time_logger.py` en Langflow como Custom Component**
2. **Agrega RealTimeLogger a tu flow** donde quieras capturar logs
3. **Ejecuta el flow** y obtén el `job_id`
4. **Conecta tu frontend** al endpoint SSE usando el `job_id`
5. **¡Listo!** Recibirás logs en tiempo real

---

**¿Necesitas ayuda?** Revisa la sección de Troubleshooting o abre un issue.
