# Instrucciones para Conectar Replit con Langflow - Samara Flow

## 🔌 Configuración de Conexión

### Endpoint Base
```
http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
```

### API Key
```
YOUR_API_KEY_HERE
```
⚠️ **IMPORTANTE**: Reemplazar con tu API key real antes de usar

---

## 📤 Enviar Mensajes al Flow (POST Request)

### Endpoint
```
POST /api/v1/run/input?stream=false
```

### Headers Requeridos
```json
{
  "Content-Type": "application/json",
  "x-api-key": "YOUR_API_KEY_HERE"
}
```

### Body (JSON)
```json
{
  "output_type": "chat",
  "input_type": "chat",
  "tweaks": {
    "TextInput-Kw2w4": {
      "input_value": "Tu mensaje aquí"
    }
  },
  "session_id": "YOUR_SESSION_ID_HERE"
}
```

### Ejemplo cURL
```bash
curl --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/input?stream=false' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: YOUR_API_KEY_HERE' \
  --data '{
    "output_type": "chat",
    "input_type": "chat",
    "tweaks": {
      "TextInput-Kw2w4": {
        "input_value": "¿Cuáles son los pedidos de venta pendientes?"
      }
    },
    "session_id": "session-123"
  }'
```

### Ejemplo Python (Requests)
```python
import requests
import json

LANGFLOW_URL = "http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"
API_KEY = "YOUR_API_KEY_HERE"

def send_message(message: str, session_id: str = "default-session"):
    """
    Envía un mensaje al flow de Langflow

    Args:
        message: El texto a enviar
        session_id: ID de sesión para mantener contexto

    Returns:
        Respuesta del flow
    """
    url = f"{LANGFLOW_URL}/api/v1/run/input?stream=false"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "TextInput-Kw2w4": {
                "input_value": message
            }
        },
        "session_id": session_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")
        return None

# Uso
if __name__ == "__main__":
    result = send_message("Consulta pedidos de venta del cliente ABC", "session-001")
    print(json.dumps(result, indent=2))
```

---

## 📊 Conectarse a Logs en Tiempo Real (SSE - Server-Sent Events)

### Endpoint de Streaming
```
GET /api/v1/run/input?stream=true
```

### ¿Qué son Server-Sent Events (SSE)?
SSE es una tecnología que permite que el servidor envíe actualizaciones en tiempo real al cliente a través de una conexión HTTP persistente.

### Ejemplo Python con SSE
```python
import requests
import json
import sseclient  # pip install sseclient-py

LANGFLOW_URL = "http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"
API_KEY = "YOUR_API_KEY_HERE"

def stream_logs(message: str, session_id: str = "default-session"):
    """
    Se conecta a los logs en tiempo real del flow

    Args:
        message: El mensaje a procesar
        session_id: ID de sesión

    Yields:
        Eventos de log en tiempo real
    """
    url = f"{LANGFLOW_URL}/api/v1/run/input?stream=true"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "Accept": "text/event-stream"
    }

    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "TextInput-Kw2w4": {
                "input_value": message
            }
        },
        "session_id": session_id
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)
    client = sseclient.SSEClient(response)

    for event in client.events():
        try:
            data = json.loads(event.data)
            yield data
        except json.JSONDecodeError:
            continue

# Uso
if __name__ == "__main__":
    print("🔄 Conectando a logs en tiempo real...")

    for log_event in stream_logs("Consulta inventario almacén principal"):
        print(f"📝 Log: {json.dumps(log_event, indent=2)}")
```

### Ejemplo JavaScript/Node.js con EventSource
```javascript
const EventSource = require('eventsource');

const LANGFLOW_URL = 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860';
const API_KEY = 'YOUR_API_KEY_HERE';

function streamLogs(message, sessionId = 'default-session') {
  const url = `${LANGFLOW_URL}/api/v1/run/input?stream=true`;

  const payload = JSON.stringify({
    output_type: 'chat',
    input_type: 'chat',
    tweaks: {
      'TextInput-Kw2w4': {
        input_value: message
      }
    },
    session_id: sessionId
  });

  const eventSource = new EventSource(url, {
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY
    },
    method: 'POST',
    body: payload
  });

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('📝 Log:', data);
    } catch (e) {
      console.error('Error parsing event:', e);
    }
  };

  eventSource.onerror = (error) => {
    console.error('❌ Error en conexión SSE:', error);
    eventSource.close();
  };

  return eventSource;
}

// Uso
const stream = streamLogs('Consulta pedidos pendientes');

// Para cerrar la conexión después de 30 segundos
setTimeout(() => {
  stream.close();
  console.log('🔌 Conexión cerrada');
}, 30000);
```

---

## 🔧 Implementación Completa para Replit

### Estructura de Proyecto Recomendada
```
replit-langflow-client/
├── main.py                 # Script principal
├── requirements.txt        # Dependencias
├── config.py              # Configuración
├── langflow_client.py     # Cliente Langflow
└── README.md              # Documentación
```

### requirements.txt
```txt
requests==2.31.0
sseclient-py==1.8.0
python-dotenv==1.0.0
```

### config.py
```python
import os
from dotenv import load_dotenv

load_dotenv()

LANGFLOW_URL = os.getenv(
    "LANGFLOW_URL",
    "http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"
)
API_KEY = os.getenv("LANGFLOW_API_KEY", "YOUR_API_KEY_HERE")
TEXT_INPUT_ID = "TextInput-Kw2w4"
```

### langflow_client.py
```python
import requests
import json
import sseclient
from typing import Dict, Any, Generator
from config import LANGFLOW_URL, API_KEY, TEXT_INPUT_ID

class LangflowClient:
    """Cliente para interactuar con Langflow Samara Flow"""

    def __init__(self):
        self.base_url = LANGFLOW_URL
        self.api_key = API_KEY
        self.text_input_id = TEXT_INPUT_ID

    def _get_headers(self, streaming: bool = False) -> Dict[str, str]:
        """Genera headers para la request"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        if streaming:
            headers["Accept"] = "text/event-stream"
        return headers

    def _build_payload(self, message: str, session_id: str) -> Dict[str, Any]:
        """Construye el payload para la request"""
        return {
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                self.text_input_id: {
                    "input_value": message
                }
            },
            "session_id": session_id
        }

    def send_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Envía mensaje sin streaming

        Args:
            message: Texto del mensaje
            session_id: ID de sesión para contexto

        Returns:
            Respuesta completa del flow
        """
        url = f"{self.base_url}/api/v1/run/input?stream=false"
        headers = self._get_headers()
        payload = self._build_payload(message, session_id)

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    def stream_response(
        self,
        message: str,
        session_id: str = "default"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Envía mensaje con streaming (SSE)

        Args:
            message: Texto del mensaje
            session_id: ID de sesión

        Yields:
            Eventos de log en tiempo real
        """
        url = f"{self.base_url}/api/v1/run/input?stream=true"
        headers = self._get_headers(streaming=True)
        payload = self._build_payload(message, session_id)

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            client = sseclient.SSEClient(response)

            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        yield data
                    except json.JSONDecodeError:
                        yield {"raw": event.data}

        except requests.exceptions.RequestException as e:
            yield {"error": str(e), "status": "failed"}

    def get_flow_status(self) -> Dict[str, Any]:
        """Verifica el estado del servidor Langflow"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            response.raise_for_status()
            return {"status": "online", "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": "offline", "error": str(e)}
```

### main.py
```python
#!/usr/bin/env python3
"""
Script principal para interactuar con Langflow desde Replit
"""

import json
from langflow_client import LangflowClient

def print_separator():
    print("\n" + "="*60 + "\n")

def main():
    print("🚀 Iniciando Cliente Langflow - Samara Flow")
    print_separator()

    # Inicializar cliente
    client = LangflowClient()

    # 1. Verificar estado del servidor
    print("1️⃣ Verificando estado del servidor...")
    status = client.get_flow_status()
    print(f"Estado: {status.get('status')}")
    print_separator()

    # 2. Enviar mensaje sin streaming
    print("2️⃣ Enviando mensaje sin streaming...")
    message = "¿Cuáles son los pedidos de venta pendientes del cliente XYZ?"
    result = client.send_message(message, session_id="test-session-001")
    print(f"Respuesta:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
    print_separator()

    # 3. Enviar mensaje con streaming (logs en tiempo real)
    print("3️⃣ Enviando mensaje con streaming (logs en tiempo real)...")
    message = "Consulta el inventario del almacén principal"

    print("📡 Conectado a logs en tiempo real...\n")
    for event in client.stream_response(message, session_id="test-session-002"):
        if "error" in event:
            print(f"❌ Error: {event['error']}")
            break
        else:
            print(f"📝 Evento: {json.dumps(event, indent=2, ensure_ascii=False)}")

    print_separator()
    print("✅ Proceso completado")

if __name__ == "__main__":
    main()
```

### .env (Crear este archivo en Replit)
```env
LANGFLOW_URL=http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
LANGFLOW_API_KEY=YOUR_API_KEY_HERE
```

---

## 🎯 Pasos para Configurar en Replit

### Paso 1: Crear Nuevo Repl
1. Ve a Replit.com
2. Crea nuevo Repl con Python
3. Nombra: `langflow-samara-client`

### Paso 2: Copiar Archivos
1. Copia todos los archivos mencionados arriba
2. Crea el archivo `.env` con tus credenciales

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar
```bash
python main.py
```

---

## 🐛 Troubleshooting

### Error: "Connection timeout"
- Verifica que la URL del servidor esté correcta
- Confirma que el servidor Langflow esté corriendo

### Error: "Invalid API Key"
- Verifica que la API key en `.env` sea correcta
- Confirma que el header `x-api-key` esté presente

### Error: "Component not found"
- Verifica que el ID `TextInput-Kw2w4` sea correcto
- Revisa el flow en Langflow para confirmar el ID del componente

### Los logs no se reciben en tiempo real
- Asegúrate de usar `stream=true` en la URL
- Verifica que el componente Real-Time Logger esté conectado en el flow
- Confirma que el header `Accept: text/event-stream` esté presente

---

## 📚 Recursos Adicionales

- [Documentación Langflow API](https://docs.langflow.org/)
- [Server-Sent Events MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Replit Docs](https://docs.replit.com/)

---

## ⚠️ Notas Importantes

1. **Seguridad**: Nunca expongas tu API key en código público
2. **Session IDs**: Usa diferentes session IDs para diferentes conversaciones
3. **Timeouts**: Los requests largos pueden tardar hasta 2 minutos
4. **Rate Limiting**: Verifica los límites de uso de tu servidor Langflow

---

Última actualización: 2025-11-13
