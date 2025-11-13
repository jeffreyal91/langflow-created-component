# 🔴 PROBLEMA: Logs Se Generan Pero No Llegan al Frontend

## 🔍 Situación Actual

### ✅ Lo Que Funciona:
- Langflow **SÍ genera los 3 logs** (vimos esto en el JSON):
  ```json
  "logs": {
    "output": [
      {"name": "03_DECISAO_PROCESSO", "message": {...}},
      {"name": "03_DECISAO_PROCESSO_DETAIL", "message": {...}},
      {"name": "03_DECISAO_PROCESSO_COMPLETE", "message": {...}}
    ]
  }
  ```

### ❌ El Problema:
- Los logs **NO llegan al frontend** vía SSE
- El backend solo recibe **1 evento** (add_message)
- Los logs están en el JSON final, pero **NO se transmiten en tiempo real**

---

## 🎯 Causa Raíz

El componente **Real-Time Logger** está usando:
```python
self.log(message=log_entry, name=f"{self.log_prefix}")
```

**Este método:**
- ✅ Guarda logs en el JSON final
- ❌ **NO transmite vía SSE**

---

## ✅ La Solución: Cambiar a `send_message()`

El componente debe usar:
```python
log_message = Message(
    text=f"[LANGFLOW_LOG] {json.dumps(log_data)}",
    sender="RealTimeLogger"
)
await self.send_message(log_message)
```

**Este método:**
- ✅ Guarda logs en el JSON
- ✅ **Transmite vía SSE en tiempo real** ⭐

---

## 🔧 Pasos Para Arreglar

### 1️⃣ Actualizar el Componente Real-Time Logger

1. **Abre Langflow:** http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
2. **Ve al workflow:** ID `23a4a54b-1bae-4d1b-a51e-f2d6c5f386a7`
3. **Localiza el componente:** Real-Time Logger (ID: `RealTimeLogger-vwujw`)
4. **Haz clic en "Edit" o "Code"**

### 2️⃣ Reemplazar el Código

**BUSCA esta sección:**
```python
async def process_and_log(self) -> Message:
    # Construir el log entry
    log_entry = self._build_log_entry()

    # ❌ ESTO NO FUNCIONA PARA SSE
    self.log(message=log_entry, name=f"{self.log_prefix}")

    if self.log_input_data and self.input_data:
        detail_log = {...}
        self.log(message=detail_log, name=f"{self.log_prefix}_DETAIL")

    # Crear mensaje de salida
    output_text = self.input_data if self.input_data else "No input data"
    message = Message(text=output_text)

    # Enviar mensaje
    await self.send_message(message)

    completion_log = {...}
    self.log(message=completion_log, name=f"{self.log_prefix}_COMPLETE")

    return message
```

**REEMPLAZA con:**
```python
async def process_and_log(self) -> Message:
    # Construir el log entry
    log_entry = self._build_log_entry()

    # ✅ ENVIAR COMO MENSAJE PARA SSE
    log_msg = Message(
        text=f"[LANGFLOW_LOG] {json.dumps(log_entry)}",
        sender="RealTimeLogger"
    )
    await self.send_message(log_msg)

    # Log detallado con datos de entrada
    if self.log_input_data and self.input_data:
        detail_log = {
            "prefix": self.log_prefix,
            "level": self.log_level,
            "message": "Input data received",
            "data": self._serialize_data(self.input_data),
            "timestamp": datetime.now().isoformat() if self.include_timestamp else None
        }

        detail_msg = Message(
            text=f"[LANGFLOW_LOG] {json.dumps(detail_log)}",
            sender="RealTimeLogger"
        )
        await self.send_message(detail_msg)

    # Crear mensaje de salida para continuar el flow
    if isinstance(self.input_data, Message):
        output_message = self.input_data
    elif self.input_data:
        output_message = Message(text=str(self.input_data))
    else:
        output_message = Message(text="No input data")

    # Log de finalización
    completion_log = {
        "prefix": self.log_prefix,
        "level": "INFO",
        "message": "Processing completed",
        "timestamp": datetime.now().isoformat() if self.include_timestamp else None
    }

    completion_msg = Message(
        text=f"[LANGFLOW_LOG] {json.dumps(completion_log)}",
        sender="RealTimeLogger"
    )
    await self.send_message(completion_msg)

    return output_message
```

### 3️⃣ Agregar Import de json

Al inicio del archivo, asegúrate de tener:
```python
import json
from datetime import datetime
```

### 4️⃣ Guardar y Probar

1. **Guarda el componente** (botón "Save")
2. **Guarda el workflow** (Ctrl+S o botón Save)
3. **Prueba desde terminal:**

```bash
TOKEN=$(curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"empresa": 1, "username": "intersys", "password": "1234"}' \
  -s | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "=== LOGS EN TIEMPO REAL ==="
timeout 30 curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content": "ola"}' 2>&1 | grep -E "LANGFLOW_LOG|langflow_log"
```

**Deberías ver:**
```
data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","level":"INFO",...}
event: langflow_log
data: {"type":"langflow_log","log":{...}}
```

---

## 🧪 Verificar Que Funciona

### Test 1: Ver Eventos SSE Crudos

```bash
# Ver TODOS los eventos que llegan
curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "ola"}' 2>&1 | head -100
```

**Busca líneas con:**
- `[LANGFLOW_LOG]` → El componente está enviando logs
- `event: langflow_log` → El backend está parseando logs
- `event: message` → Mensajes normales

### Test 2: Ver Logs del Backend

Mira la consola del backend (donde ejecutaste `python app/main.py`).

**Deberías ver:**
```
[LANGFLOW LOGS] Found log in message: [LANGFLOW_LOG] {...}
[LANGFLOW LOGS] Parsed log data: {'prefix': '03_DECISAO_PROCESSO', ...}
[LANGFLOW LOGS] Emitting log from message
```

**Si NO ves esto:**
→ El componente NO está enviando mensajes con `[LANGFLOW_LOG]`

### Test 3: Ver en el Frontend

Abre la consola del navegador (F12) y ejecuta:
```javascript
const eventSource = new EventSource('/api/chat/stream');

eventSource.addEventListener('langflow_log', (event) => {
  console.log('✅ LOG RECIBIDO:', event.data);
});

eventSource.onmessage = (event) => {
  console.log('📨 EVENTO:', event.data);
};
```

---

## 📋 Checklist de Verificación

Después de actualizar el componente:

- [ ] Cambié `self.log()` por `await self.send_message()`
- [ ] Los mensajes tienen formato `[LANGFLOW_LOG] {json}`
- [ ] Agregué `import json` al inicio del archivo
- [ ] Guardé el componente en Langflow
- [ ] Guardé el workflow
- [ ] Ejecuté el test desde terminal
- [ ] Veo `[LANGFLOW_LOG]` en la salida del curl
- [ ] Veo logs en la consola del backend
- [ ] Veo eventos `langflow_log` en el frontend

---

## 🔍 Debugging Paso a Paso

### Paso 1: Verificar que el Componente Envía Mensajes

En el código del componente, agrega un print temporal:

```python
async def process_and_log(self) -> Message:
    log_entry = self._build_log_entry()

    log_text = f"[LANGFLOW_LOG] {json.dumps(log_entry)}"
    print(f"🔷 [DEBUG] Enviando log: {log_text[:100]}...")  # ← AGREGAR ESTO

    log_msg = Message(text=log_text, sender="RealTimeLogger")
    await self.send_message(log_msg)

    # ... resto del código
```

Ejecuta el workflow y **revisa los logs de Langflow**. Deberías ver:
```
🔷 [DEBUG] Enviando log: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO"...
```

### Paso 2: Verificar que Llega al Backend

En `app/services/langflow_service.py`, busca esta sección y verifica que esté presente:

```python
# Detectar logs en mensajes de texto
chunk_text = chunk.get("chunk", "") or ""

if isinstance(chunk_text, str) and "[LANGFLOW_LOG]" in chunk_text:
    print(f"[LANGFLOW LOGS] Found log in message: {chunk_text[:100]}")  # ← DEBE ESTAR

    try:
        log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
        log_data = json.loads(log_json)

        print(f"[LANGFLOW LOGS] Parsed log data: {log_data}")  # ← DEBE ESTAR

        yield {
            "event": "langflow_log",
            "data": json.dumps({
                "type": "langflow_log",
                "log": log_data
            })
        }

        print("[LANGFLOW LOGS] Emitting log from message")  # ← DEBE ESTAR
        continue
    except Exception as e:
        print(f"[LANGFLOW LOGS] Error parsing log: {e}")
```

### Paso 3: Verificar que Llega al Frontend

En el código JavaScript del frontend, asegúrate de escuchar el evento correcto:

```javascript
// ✅ CORRECTO - Escuchar evento específico
eventSource.addEventListener('langflow_log', (event) => {
  const log = JSON.parse(event.data);
  console.log('📝 LOG:', log);
});

// ❌ INCORRECTO - Solo escuchar mensajes genéricos
eventSource.onmessage = (event) => {
  // Esto NO captura eventos 'langflow_log'
};
```

---

## 🎯 Resultado Esperado

Después de aplicar los cambios, deberías ver:

### En el Terminal (curl):
```bash
event: message
data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","level":"INFO",...}

event: langflow_log
data: {"type":"langflow_log","log":{"prefix":"03_DECISAO_PROCESSO",...}}

event: message
data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","message":"Input data received",...}

event: langflow_log
data: {"type":"langflow_log","log":{...}}

event: message
data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","message":"Processing completed",...}

event: langflow_log
data: {"type":"langflow_log","log":{...}}
```

### En el Backend (consola):
```
[LANGFLOW LOGS] Found log in message: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO"...
[LANGFLOW LOGS] Parsed log data: {'prefix': '03_DECISAO_PROCESSO', 'level': 'INFO'...
[LANGFLOW LOGS] Emitting log from message
```

### En el Frontend (navegador):
```
📝 LOG: {prefix: "03_DECISAO_PROCESSO", level: "INFO", message: "Processing data..."}
📝 LOG: {prefix: "03_DECISAO_PROCESSO", message: "Input data received", data: "..."}
📝 LOG: {prefix: "03_DECISAO_PROCESSO", message: "Processing completed"}
```

---

## 🆘 Si Aún No Funciona

### Problema: No veo `[LANGFLOW_LOG]` en el curl

**Causa:** El componente no está enviando mensajes correctamente.

**Verifica:**
1. Guardaste el componente en Langflow?
2. Guardaste el workflow?
3. El componente está **conectado** en el workflow?
4. Usaste `await self.send_message()` (no `self.log()`)?

---

### Problema: Veo `[LANGFLOW_LOG]` pero no `event: langflow_log`

**Causa:** El backend no está parseando los logs.

**Verifica:**
1. El código de detección está en `langflow_service.py`?
2. Reiniciaste el backend después de cambios?
3. Los prints aparecen en la consola del backend?

---

### Problema: Veo eventos en curl pero no en frontend

**Causa:** El frontend no está escuchando correctamente.

**Verifica:**
1. Usas `addEventListener('langflow_log', ...)`?
2. La consola del navegador muestra algún error?
3. El EventSource está conectado correctamente?

---

## 📄 Código Completo del Componente

Para referencia, aquí está el componente completo corregido:

**Ver archivo:** `RealTimeLogger_FIXED.py`

---

**Última actualización:** 2025-11-13
**Siguiente paso:** Actualizar el componente Real-Time Logger en Langflow
