# 🔍 Debug: Logs No Aparecen en el Frontend

## 🔴 Problema Actual

El frontend solo recibe:
```
✅ Langflow confirmou: User - (mensagem enviada) [complete]
❌ PROBLEMA: Nenhuma resposta recebida
```

**NO recibe:**
- ❌ Logs de Langflow (`langflow_log` events)
- ❌ Respuesta final del agente

---

## 🧪 Paso 1: Verificar Qué Está Enviando Langflow

### Test desde Terminal

Ejecuta esto para ver TODOS los eventos que Langflow envía:

```bash
# Obtener token
TOKEN=$(curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"empresa": 1, "username": "intersys", "password": "1234"}' \
  -s | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Ver stream completo sin filtros
curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content": "ola"}' 2>&1
```

### ¿Qué Debes Ver?

**SI el sistema funciona correctamente:**
```
event: langflow_log
data: {"type":"langflow_log","log":{...}}

event: message
data: {"type":"message","content":"respuesta del agente"}

event: end
data: {"type":"end"}
```

**SI solo ves esto (PROBLEMA):**
```
event: message
data: {"type":"message","properties":{"state":"complete"}}
```

---

## 🔧 Paso 2: Verificar el Backend

### Archivo: `app/services/langflow_service.py`

Busca esta función y agrega **prints de debug**:

```python
async def process_langflow_stream(
    text: str,
    flow_id: str,
    session_id: str,
    user_data: dict,
    empresa_id: int
) -> AsyncGenerator[dict, None]:
    """
    Procesa el stream de Langflow y emite eventos SSE
    """
    # ... código existente ...

    async for chunk in response.aiter_lines():
        if not chunk:
            continue

        # DEBUG: Ver qué llega de Langflow
        print(f"[DEBUG LANGFLOW] Raw chunk: {chunk[:200]}")

        # Parsear línea SSE
        if chunk.startswith(b'event:'):
            current_event_type = chunk[6:].decode().strip()
            print(f"[DEBUG EVENT] Event type: {current_event_type}")
            continue

        if chunk.startswith(b'data:'):
            data_str = chunk[5:].decode().strip()
            print(f"[DEBUG DATA] Data: {data_str[:200]}")

            try:
                event_data = json.loads(data_str)
                print(f"[DEBUG PARSED] Event data keys: {event_data.keys()}")

                # Verificar si hay logs
                if "logs" in event_data:
                    print(f"[DEBUG LOGS] Found logs: {event_data['logs']}")

                # ... resto del código ...
```

Reinicia el backend y prueba de nuevo. Los prints te dirán exactamente qué está llegando.

---

## 🎯 Paso 3: Verificar el Flow en Langflow

### Problema Común: El Flow No Tiene Output Final

1. **Abre Langflow** en el navegador
2. **Ve a tu flow** (ID: `23a4a54b-1bae-4d1b-a51e-f2d6c5f386a7`)
3. **Verifica que haya un componente de OUTPUT al final:**
   - ✅ `Chat Output`
   - ✅ `Text Output`
   - ❌ Si termina en un agente sin output → **ESTE ES EL PROBLEMA**

### Solución:

Si el flow termina en un agente, debes agregar un **Chat Output** al final:

```
Agente Final
    ↓
Chat Output  ← AGREGAR ESTO
```

---

## 📋 Paso 4: Verificar el Componente Real-Time Logger

### Ir a Langflow y verificar:

1. **Abre el componente Real-Time Logger**
2. **Verifica el código:**

```python
async def process_and_log(self) -> Message:
    # Construir log
    log_entry = {
        "prefix": self.log_prefix,
        "level": self.log_level,
        "message": f"Processing data in {self.log_prefix}",
        "timestamp": datetime.now().isoformat()
    }

    # ⚠️ IMPORTANTE: Debe usar send_message
    log_message = Message(
        text=f"[LANGFLOW_LOG] {json.dumps(log_entry)}",
        sender="RealTimeLogger"
    )
    await self.send_message(log_message)  # ← VERIFICA ESTO

    # Pasar datos al siguiente nodo
    return self.input_data  # ← DEBE RETORNAR LOS DATOS
```

3. **Configuración del logger:**
   - ✅ `send_as_messages` = **true**
   - ✅ `log_prefix` = nombre único
   - ✅ Está **CONECTADO** en el flow

---

## 🔍 Paso 5: Verificar el Frontend

### Archivo: Tu código JavaScript del frontend

Verifica que estés escuchando TODOS los eventos:

```javascript
const eventSource = new EventSource('/api/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ content: message })
});

// ⚠️ IMPORTANTE: Escuchar eventos específicos
eventSource.addEventListener('langflow_log', (event) => {
  console.log('📝 LOG RECIBIDO:', event.data);
  const log = JSON.parse(event.data);
  // Mostrar en UI
});

eventSource.addEventListener('message', (event) => {
  console.log('💬 MENSAJE RECIBIDO:', event.data);
  const data = JSON.parse(event.data);

  if (data.type === 'message') {
    // Mostrar respuesta del agente
  }
});

eventSource.addEventListener('error', (event) => {
  console.error('❌ ERROR SSE:', event);
});

// ⚠️ TAMBIÉN escuchar evento genérico
eventSource.onmessage = (event) => {
  console.log('📨 EVENTO GENÉRICO:', event.data);
};
```

---

## 🧩 Problemas Comunes y Soluciones

### Problema 1: Solo Recibo Evento de "complete"

**Causa:** El flow no tiene un output final o termina sin generar respuesta.

**Solución:**
1. Agregar `Chat Output` al final del flow
2. Conectar el último agente al Chat Output
3. Guardar el flow

---

### Problema 2: No Recibo Logs de Real-Time Logger

**Causa:** El logger no está enviando mensajes correctamente.

**Solución:**
1. Verificar que `send_as_messages = true`
2. Verificar que usa `await self.send_message()`
3. Verificar que el formato es `[LANGFLOW_LOG] {json}`

**Test rápido:**
```python
# En el componente, agregar print para debug
print(f"[LOGGER DEBUG] Sending log: {log_message.text}")
```

---

### Problema 3: Backend No Parsea los Logs

**Causa:** El backend no detecta el formato `[LANGFLOW_LOG]`.

**Solución:**

Verifica en `langflow_service.py`:

```python
# Debe haber código como este:
if "[LANGFLOW_LOG]" in chunk_text:
    log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
    log_data = json.loads(log_json)

    yield {
        "event": "langflow_log",
        "data": json.dumps({
            "type": "langflow_log",
            "log": log_data
        })
    }
```

---

### Problema 4: Frontend No Recibe Eventos SSE

**Causa:** Configuración incorrecta de EventSource o CORS.

**Solución:**

```javascript
// ❌ INCORRECTO - EventSource no soporta POST directamente
const eventSource = new EventSource('/api/chat/stream', {
  method: 'POST'  // ← NO FUNCIONA
});

// ✅ CORRECTO - Usar fetch con ReadableStream
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ content: message })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  console.log('CHUNK:', chunk);

  // Parsear eventos SSE
  const lines = chunk.split('\n');
  for (const line of lines) {
    if (line.startsWith('event:')) {
      eventType = line.substring(6).trim();
    } else if (line.startsWith('data:')) {
      const data = JSON.parse(line.substring(5).trim());

      if (eventType === 'langflow_log') {
        console.log('📝 LOG:', data);
      } else if (data.type === 'message') {
        console.log('💬 MESSAGE:', data);
      }
    }
  }
}
```

---

## 📊 Checklist de Diagnóstico

Marca cada item que verificaste:

### En Langflow:
- [ ] El flow tiene un componente `Chat Output` al final
- [ ] El último agente está conectado al Chat Output
- [ ] El Real-Time Logger usa `send_as_messages = true`
- [ ] El Real-Time Logger usa `await self.send_message()`
- [ ] El logger está conectado en el flow (no aislado)
- [ ] Guardé el componente
- [ ] Guardé el flow

### En Backend:
- [ ] Agregué prints de debug en `langflow_service.py`
- [ ] Reinicié el backend después de cambios
- [ ] Vi los prints en la consola cuando envío un mensaje
- [ ] Los prints muestran que llegan eventos de Langflow
- [ ] El código detecta `[LANGFLOW_LOG]` correctamente

### En Frontend:
- [ ] Uso `fetch` con `ReadableStream` (no EventSource básico)
- [ ] Escucho el evento `langflow_log`
- [ ] Escucho el evento `message`
- [ ] Agregué `console.log` para ver todos los chunks
- [ ] Vi en la consola del navegador qué eventos llegan

### Test Manual:
- [ ] Ejecuté el curl desde terminal
- [ ] Vi eventos en la respuesta del curl
- [ ] Vi logs con formato `[LANGFLOW_LOG]`
- [ ] Vi respuesta final del agente

---

## 🎯 Próximos Pasos

Según lo que encuentres en el diagnóstico:

### Si NO ves eventos en el curl:
→ **Problema en Langflow o Backend**
- Revisa el flow en Langflow
- Verifica que tenga output final
- Verifica que el logger esté conectado

### Si VES eventos en curl pero NO en frontend:
→ **Problema en Frontend**
- Revisa el código JavaScript
- Usa `fetch` + `ReadableStream`
- Agrega `console.log` para debug

### Si ves eventos pero NO logs:
→ **Problema en Real-Time Logger**
- Actualiza el código del componente
- Verifica `send_as_messages = true`
- Verifica formato `[LANGFLOW_LOG]`

---

## 📞 Para Obtener Ayuda

Ejecuta este comando y envía la salida:

```bash
TOKEN=$(curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"empresa": 1, "username": "intersys", "password": "1234"}' \
  -s | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "=== TEST COMPLETO ==="
curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content": "ola"}' 2>&1 | head -50
```

Esto mostrará los primeros 50 eventos que el backend envía.

---

**Última actualización:** 2025-11-13
**Siguiente paso:** Ejecutar diagnóstico del Paso 1
