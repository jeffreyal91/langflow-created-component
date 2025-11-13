# 🔧 Cómo Arreglar los Logs en Tiempo Real

## 🔍 El Problema

**Lo que descubrimos:**
- ✅ El componente Real-Time Logger **SÍ genera logs** (los vemos en el JSON)
- ❌ Pero los logs **NO aparecen en el streaming SSE** porque Langflow no los envía como eventos separados
- ❌ El método `self.log()` solo guarda logs internamente, NO los transmite vía SSE

**Eventos SSE que Langflow envía:**
- ✅ `chunk` - fragmentos de texto
- ✅ `message` - mensajes completos
- ✅ `end` - finalización
- ❌ **logs** - NO se envían automáticamente

---

## ✅ La Solución: Enviar Logs como Mensajes

En lugar de usar `self.log()`, enviaremos los logs como **mensajes** usando `self.send_message()`, que SÍ se transmite vía SSE.

---

## 📝 Paso 1: Actualizar el Componente en Langflow

### Opción A: Reemplazar el código del componente

1. **Abre Langflow** en tu navegador
2. **Ve al componente Real-Time Logger** en tu flow
3. **Haz clic en "Edit"** o abre el código del componente
4. **Reemplaza TODO el código** con el contenido de: **`RealTimeLogger_FIXED.py`**
5. **Guarda** el componente
6. **Guarda el flow**

### Opción B: Crear un nuevo Custom Component

1. En Langflow, ve a **"Custom Components"**
2. Crea un nuevo componente llamado **"Real-Time Logger v2"**
3. Pega el código de **`RealTimeLogger_FIXED.py`**
4. Guarda el componente
5. En tu flow, reemplaza los loggers antiguos con los nuevos

---

## 🔑 Cambios Clave en el Componente

### ❌ ANTES (no funciona con SSE):
```python
# Esto NO se transmite vía SSE
self.log(message=log_entry, name=f"{self.log_prefix}")
```

### ✅ DESPUÉS (funciona con SSE):
```python
# Esto SÍ se transmite vía SSE
log_message = Message(
    text=f"[LANGFLOW_LOG] {json.dumps(log_data)}",
    sender="RealTimeLogger",
)
await self.send_message(log_message)
```

---

## 📊 Formato de Logs en SSE

Con el componente corregido, los logs aparecerán así en el stream SSE:

```json
{
  "event": "message",
  "chunk": "[LANGFLOW_LOG] {\"prefix\": \"03_DECISAO_PROCESSO\", \"level\": \"INFO\", \"message\": \"Processing data in Real-Time Logger\", \"timestamp\": \"2025-11-13T14:01:05.700434\"}"
}
```

---

## 🔧 Paso 2: Actualizar el Backend (ya está listo)

Tu backend en `app/services/langflow_service.py` ya detecta estos logs automáticamente:

```python
# Detectar logs de Langflow
if isinstance(chunk_text, str) and "[LANGFLOW_LOG]" in chunk_text:
    try:
        log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
        log_data = json.loads(log_json)

        # Emitir evento de log
        yield {
            "event": "langflow_log",
            "data": json.dumps({
                "prefix": log_data.get("prefix"),
                "level": log_data.get("level"),
                "message": log_data.get("message"),
                "timestamp": log_data.get("timestamp"),
                "data": log_data.get("data")
            })
        }
    except:
        pass
```

---

## 🧪 Paso 3: Probar

### En Replit (Frontend):

```javascript
const eventSource = new EventSource('/api/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ content: 'Hola' })
});

eventSource.addEventListener('langflow_log', (event) => {
  const logData = JSON.parse(event.data);
  console.log(`🔷 [${logData.prefix}] ${logData.message}`);

  // Mostrar en la UI
  document.getElementById('logs').innerHTML += `
    <div class="log-entry">
      <span class="prefix">${logData.prefix}</span>
      <span class="message">${logData.message}</span>
      <span class="timestamp">${logData.timestamp}</span>
    </div>
  `;
});
```

### Resultado esperado:

```
🔷 [01_JWT_VALIDADO] Processing data in Real-Time Logger
🔷 [01_JWT_VALIDADO] Input data received
🔷 [01_JWT_VALIDADO] Processing completed
🔷 [02_VALIDACAO_SEGURANCA] Processing data in Real-Time Logger
🔷 [02_VALIDACAO_SEGURANCA] Input data received
...
```

---

## 📋 Checklist de Implementación

### En Langflow:
- [ ] Actualizar componente Real-Time Logger con el código corregido
- [ ] Verificar que `send_as_messages` está en `true`
- [ ] Guardar el componente
- [ ] Guardar el flow
- [ ] Probar en Playground de Langflow

### En Replit:
- [ ] Verificar que el backend detecta `[LANGFLOW_LOG]`
- [ ] Crear event listener para `langflow_log`
- [ ] Mostrar logs en la UI
- [ ] Probar con un mensaje de prueba

---

## 🎯 Configuración del Componente

Cuando agregues el Real-Time Logger al flow, asegúrate de:

✅ **log_prefix:** Nombre único (ej: `01_JWT_VALIDADO`)
✅ **log_level:** `INFO`
✅ **include_timestamp:** `true`
✅ **include_metadata:** `true`
✅ **log_input_data:** `true`
✅ **send_as_messages:** `true` ⭐ **IMPORTANTE**

---

## 🔍 Debugging

### Problema: Sigo sin ver logs

**Verifica:**
1. ¿El campo `send_as_messages` está en `true`?
2. ¿Guardaste el componente Y el flow?
3. ¿El backend está corriendo?
4. ¿Estás usando `stream=true` en la request?

**Prueba esto en terminal:**
```bash
curl -N 'http://localhost:5000/api/chat/stream' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"content": "test"}' | grep -E "langflow_log|LANGFLOW_LOG"
```

Si ves `[LANGFLOW_LOG]` en la salida, el componente funciona.

---

### Problema: Veo `[LANGFLOW_LOG]` pero no se parsea

**Causa:** El backend no está detectando el formato.

**Solución:** Verifica que `langflow_service.py` tenga el código de detección:

```python
if "[LANGFLOW_LOG]" in chunk_text:
    log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
    log_data = json.loads(log_json)
    yield {"event": "langflow_log", "data": json.dumps(log_data)}
```

---

### Problema: Los mensajes del agente aparecen con `[LANGFLOW_LOG]`

**Causa:** Los logs se están mezclando con el texto del agente.

**Solución:** Filtra los logs en el backend antes de enviarlos al frontend:

```python
# No enviar mensajes que contengan [LANGFLOW_LOG] como texto normal
if "[LANGFLOW_LOG]" not in chunk_text:
    yield {"event": "message", "data": chunk_text}
```

---

## 📊 Flujo Completo

```
Usuario envía mensaje
    ↓
Backend recibe → Envía a Langflow con stream=true
    ↓
Langflow ejecuta flow:
    ↓
JWT Validator → Real-Time Logger #1
    ↓
    Logger envía: [LANGFLOW_LOG] {"prefix": "01_JWT_VALIDADO", ...}
    ↓
Agente Validador → Real-Time Logger #2
    ↓
    Logger envía: [LANGFLOW_LOG] {"prefix": "02_VALIDACAO_SEGURANCA", ...}
    ↓
... más componentes ...
    ↓
Backend recibe cada chunk:
    - Detecta [LANGFLOW_LOG]
    - Parsea JSON
    - Emite evento SSE "langflow_log"
    ↓
Replit recibe eventos:
    - langflow_log → Muestra en sección de logs
    - message → Muestra en chat
    ↓
Usuario ve logs en tiempo real mientras el agente procesa
```

---

## 🎨 Ejemplo de UI en Replit

```html
<div class="chat-container">
  <!-- Panel de logs -->
  <div class="logs-panel">
    <h3>📊 Logs en Tiempo Real</h3>
    <div id="logs-container"></div>
  </div>

  <!-- Panel de chat -->
  <div class="chat-panel">
    <div id="messages"></div>
    <input id="message-input" type="text" />
  </div>
</div>

<script>
const logsContainer = document.getElementById('logs-container');

eventSource.addEventListener('langflow_log', (event) => {
  const log = JSON.parse(event.data);

  const logElement = document.createElement('div');
  logElement.className = `log-entry log-${log.level.toLowerCase()}`;
  logElement.innerHTML = `
    <span class="log-prefix">[${log.prefix}]</span>
    <span class="log-message">${log.message}</span>
    ${log.timestamp ? `<span class="log-time">${log.timestamp}</span>` : ''}
  `;

  logsContainer.appendChild(logElement);
  logsContainer.scrollTop = logsContainer.scrollHeight;
});
</script>

<style>
.log-entry {
  padding: 8px;
  margin: 4px 0;
  border-left: 3px solid #ccc;
  font-family: monospace;
  font-size: 12px;
}

.log-prefix {
  color: #0066cc;
  font-weight: bold;
  margin-right: 8px;
}

.log-message {
  color: #333;
}

.log-time {
  color: #999;
  font-size: 10px;
  float: right;
}

.log-info { border-left-color: #0066cc; }
.log-debug { border-left-color: #999; }
.log-warning { border-left-color: #ff9900; }
.log-error { border-left-color: #cc0000; }
</style>
```

---

## ✅ Resumen

**Antes:**
- ❌ `self.log()` → Solo guarda internamente, no transmite vía SSE

**Después:**
- ✅ `self.send_message()` con `[LANGFLOW_LOG]` → Se transmite vía SSE
- ✅ Backend detecta y parsea → Emite evento `langflow_log`
- ✅ Replit recibe y muestra → Usuario ve logs en tiempo real

---

**Última actualización:** 2025-11-13
**Estado:** ✅ SOLUCIÓN COMPLETA - LISTA PARA IMPLEMENTAR
