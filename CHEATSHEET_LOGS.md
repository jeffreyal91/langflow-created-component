# ⚡ CHEATSHEET - Logs en Tiempo Real

**Flow ID:** `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`

---

## 🎯 DIAGNÓSTICO: stream=false vs stream=true

```bash
# ❌ PROBLEMA (stream=false)
curl ... ?stream=false
# → Los logs NO se transmiten en tiempo real

# ✅ SOLUCIÓN (stream=true)
curl -N ... ?stream=true
# → Los logs SÍ se transmiten en tiempo real
```

---

## 🧪 TEST RÁPIDO

**Reemplaza `TU_API_KEY` y ejecuta:**

```bash
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: TU_API_KEY' \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }' 2>&1 | grep "\[LANGFLOW_LOG\]"
```

**✅ Si ves `[LANGFLOW_LOG]` → ¡Funciona! Solo usa `stream=true` en tu código**

**❌ Si NO ves nada → Ejecuta:**
```bash
# Ver JSON completo con logs al final
curl --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=false' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: TU_API_KEY' \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }' | python3 -m json.tool | grep -A5 '"logs"'
```

---

## 📝 CÓDIGO FRONTEND

```javascript
// ✅ Capturar logs en tiempo real
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ content: message })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);

  // Detectar logs
  if (chunk.includes('[LANGFLOW_LOG]')) {
    const match = chunk.match(/\[LANGFLOW_LOG\]\s*(\{.*?\})/);
    if (match) {
      const log = JSON.parse(match[1]);
      console.log('📝 LOG:', log);
      displayLog(log); // Mostrar en UI
    }
  }
}
```

---

## 📝 CÓDIGO BACKEND (Python)

```python
# ✅ Llamar a Langflow con streaming
langflow_url = f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}?stream=true"

async with aiohttp.ClientSession() as session:
    async with session.post(langflow_url, json=data) as response:
        async for chunk in response.content.iter_any():
            chunk_text = chunk.decode('utf-8')

            # Detectar logs
            if "[LANGFLOW_LOG]" in chunk_text:
                log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
                log_data = json.loads(log_json)

                # Emitir como evento SSE
                yield {
                    "event": "langflow_log",
                    "data": json.dumps({"type": "langflow_log", "log": log_data})
                }

            # Emitir chunk
            yield {"event": "message", "data": chunk_text}
```

---

## 🔍 VERIFICACIONES RÁPIDAS

### 1. ¿Logger tiene código correcto?
```bash
# Buscar en el flow JSON
grep -A5 "send_message" flow.json
# ✅ Debe tener: await self.send_message()
```

### 2. ¿Logger está conectado?
```bash
# Buscar conexiones del logger
grep -A10 "CustomComponent-l1TtC" flow.json | grep -E "source|target"
# ✅ Debe tener source y target
```

### 3. ¿Agente tiene API key?
- Abrir Langflow UI
- Clic en "Gerador query" (Agent-62OgV)
- Verificar campo "OpenAI API Key"

### 4. ¿Backend parsea logs?
```bash
# En la consola del backend, debes ver:
[LANGFLOW LOGS] Found log in message: [LANGFLOW_LOG] {...}
[LANGFLOW LOGS] Parsed log data: {'prefix': 'FLOW_LOG', ...}
[LANGFLOW LOGS] Emitting log from message
```

---

## 📊 TABLA DE DIAGNÓSTICO RÁPIDO

| Síntoma | Causa | Solución |
|---------|-------|----------|
| Logs NO aparecen en tiempo real | Usas `stream=false` | Cambiar a `stream=true` |
| curl con `stream=true` muestra logs | ✅ Logger funciona | Actualizar frontend/backend |
| curl NO muestra logs | Flow no se ejecuta | Verificar API key del agente |
| Logs en JSON final pero NO en stream | Backend no parsea | Actualizar código backend |
| Flow NO genera respuesta | Agente sin API key | Configurar en Langflow |

---

## 🚀 ARCHIVOS DE REFERENCIA

| Archivo | Para qué sirve |
|---------|----------------|
| **RESUMEN_EJECUTIVO_FINAL.md** | Diagnóstico completo con solución |
| **GUIA_DEFINITIVA_TROUBLESHOOTING.md** | 4 pruebas exhaustivas |
| **PASOS_EXACTOS_PARA_ARREGLAR_LOGS.md** | Guía paso a paso |
| **RealTimeLogger_COPIAR_EN_LANGFLOW.py** | Código del logger |
| **test_logs_flow.sh** | Script automatizado |
| **CHEATSHEET_LOGS.md** (este) | Referencia rápida |

---

## ⚡ ACCIÓN INMEDIATA (30 segundos)

```bash
# 1. Copia este comando
# 2. Reemplaza TU_API_KEY
# 3. Ejecuta
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'x-api-key: TU_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{"output_type":"chat","input_type":"text","tweaks":{"TextInput-ghNJt":{"input_value":"SELECT 1 FROM DUAL"}}}' | grep LANGFLOW_LOG
```

**¿Ves `[LANGFLOW_LOG]`?**
- ✅ **SÍ** → Cambia tu código para usar `stream=true`
- ❌ **NO** → Lee `GUIA_DEFINITIVA_TROUBLESHOOTING.md`

---

**Última actualización:** 2025-11-13
