# 🎯 GUÍA DEFINITIVA DE TROUBLESHOOTING - Logs en Tiempo Real

**Flow ID:** `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
**Fecha:** 2025-11-13
**Estado:** 🔴 DIAGNÓSTICO FINAL

---

## ✅ LO QUE YA ESTÁ CORRECTO

Según el análisis del flow JSON:

1. ✅ **El componente Real-Time Logger tiene el código correcto**
   - Usa `await self.send_message()`
   - Formato: `[LANGFLOW_LOG] {json}`
   - ID: `CustomComponent-l1TtC`

2. ✅ **El logger ESTÁ conectado en el flujo**
   ```
   Agent-62OgV → Real-Time Logger → SQLComponent-eZku5
   ```

3. ✅ **Configuración del logger es correcta**
   - `log_prefix`: "FLOW_LOG"
   - `log_level`: "INFO"
   - `include_timestamp`: true
   - `log_input_data`: true
   - `include_metadata`: true

---

## 🔴 PROBLEMA IDENTIFICADO

**EL ISSUE MÁS PROBABLE: Estás usando `stream=false`**

### ¿Por qué es un problema?

| Parámetro | ¿Cómo se transmiten los logs? | ¿Ves logs en tiempo real? |
|-----------|-------------------------------|---------------------------|
| `stream=false` | Solo en JSON final en `logs.output` | ❌ NO |
| `stream=true` | Vía SSE (Server-Sent Events) | ✅ SÍ |

**Tu comando actual:**
```bash
curl ... ?stream=false
```

**Con `stream=false`:**
- Los logs se generan ✅
- Pero NO se transmiten vía SSE ❌
- Solo aparecen en el JSON final ✅
- El frontend NO los recibe en tiempo real ❌

---

## 🧪 PRUEBA 1: Verificar con stream=true

**IMPORTANTE:** Reemplaza `YOUR_API_KEY_HERE` con tu API key real.

```bash
# Test con streaming habilitado
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: YOUR_API_KEY_HERE' \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }' 2>&1
```

### ✅ Resultado ESPERADO si funciona:

```
event: message
data: {"type":"message","chunk":"..."}

event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","level":"INFO","message":"Processing data in Real-Time Logger","timestamp":"2025-11-13T..."}

event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","level":"INFO","message":"Input data received","data":"...","timestamp":"2025-11-13T..."}

event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","level":"INFO","message":"Processing completed","timestamp":"2025-11-13T..."}

event: end
data: {"result":"..."}
```

### ❌ Si NO ves `[LANGFLOW_LOG]`:

El flow no está llegando al logger. Ir a **PRUEBA 2**.

---

## 🧪 PRUEBA 2: Verificar que el Flow Se Ejecuta

### Opción A: Usando Playground de Langflow

1. Abre: http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
2. Ve al flow: `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
3. Haz clic en **"Playground"**
4. Envía: `SELECT 1 FROM DUAL`

**Resultado esperado:**
- ✅ Debe generar una respuesta SQL
- ❌ Si NO genera respuesta → Ir a **PRUEBA 3**

### Opción B: Test sin streaming (ver JSON final)

```bash
curl --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=false' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: YOUR_API_KEY_HERE' \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }' | python3 -m json.tool
```

**Busca en el JSON:**

```json
{
  "outputs": [
    {
      "outputs": [
        // ← ¿HAY CONTENIDO AQUÍ?
      ]
    }
  ],
  "logs": {
    "output": [
      // ← ¿HAY LOGS AQUÍ?
    ]
  }
}
```

**Interpretación:**

| `outputs` | `logs.output` | Diagnóstico |
|-----------|---------------|-------------|
| ✅ Con datos | ✅ Con logs | Logger funciona, usa `stream=true` |
| ✅ Con datos | ❌ Vacío | Logger no se ejecuta (desconectado) |
| ❌ Vacío | ❌ Vacío | El flow no se ejecuta (ir a PRUEBA 3) |
| ❌ Vacío | ✅ Con logs | Flow falla después del logger |

---

## 🧪 PRUEBA 3: Verificar Agente "Gerador query"

El primer componente después del input es **Agent-62OgV** (Gerador query).

**Si este agente no se ejecuta, el flow NUNCA llega al logger.**

### ¿Por qué puede fallar el agente?

1. ❌ **Falta OpenAI API Key**
2. ❌ **El modelo no está configurado**
3. ❌ **El system prompt está vacío**
4. ❌ **Hay errores en el código del agente**

### Cómo verificar:

1. Abre Langflow en el navegador
2. Ve al componente **"Gerador query"** (Agent-62OgV)
3. Haz clic en el componente
4. Verifica:
   - ✅ Campo "OpenAI API Key" tiene un valor
   - ✅ Campo "Model Name" tiene un modelo (ej: gpt-4o)
   - ✅ Campo "System Message" NO está vacío
   - ✅ NO hay ícono rojo de error

### Si falta la API key:

1. Haz clic en el campo "OpenAI API Key"
2. Selecciona o ingresa tu API key
3. Guarda el componente (botón "Save")
4. Guarda el workflow (Ctrl+S)
5. Prueba de nuevo

---

## 🧪 PRUEBA 4: Verificar Logs en el Backend (Si usas Replit)

Si tu backend está intermediando entre el frontend y Langflow, verifica que esté parseando los logs correctamente.

### En el código del backend (app/services/langflow_service.py):

```python
# ✅ Debe tener este código
if "[LANGFLOW_LOG]" in chunk_text:
    try:
        log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
        log_data = json.loads(log_json)

        yield {
            "event": "langflow_log",
            "data": json.dumps({
                "type": "langflow_log",
                "log": log_data
            })
        }
    except Exception as e:
        print(f"[LANGFLOW LOGS] Error parsing log: {e}")
```

### Test directo desde el backend:

```bash
# Obtener token
TOKEN=$(curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"empresa": 1, "username": "intersys", "password": "1234"}' \
  -s | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."
echo ""

# Enviar mensaje y buscar logs
timeout 30 curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content": "SELECT 1 FROM DUAL"}' 2>&1 | grep -E "\[LANGFLOW_LOG\]|langflow_log" | head -20
```

**Resultado esperado:**
```
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG",...}
event: langflow_log
```

**Si NO ves nada:**
- El backend NO está recibiendo logs de Langflow
- Volver a **PRUEBA 1** con `stream=true`

---

## 📊 MATRIZ DE DIAGNÓSTICO

| Test | Resultado | Diagnóstico | Solución |
|------|-----------|-------------|----------|
| PRUEBA 1 | ✅ Veo `[LANGFLOW_LOG]` | Logger funciona | Usar `stream=true` en tus llamadas |
| PRUEBA 1 | ❌ NO veo logs | Flow no llega al logger | Ir a PRUEBA 2 |
| PRUEBA 2 (Playground) | ✅ Genera respuesta | Flow funciona | Problema en la API call |
| PRUEBA 2 (Playground) | ❌ NO genera respuesta | Flow no se ejecuta | Ir a PRUEBA 3 |
| PRUEBA 2 (JSON) | `outputs` vacío | Flow falla | Revisar logs de error |
| PRUEBA 2 (JSON) | `logs.output` con logs | Logger funciona | Usar `stream=true` |
| PRUEBA 3 | ❌ Falta API key | Agente no se ejecuta | Configurar API key |
| PRUEBA 4 | ❌ Backend no parsea | Backend incorrecto | Actualizar código backend |

---

## 🎯 SOLUCIONES POR PROBLEMA

### Problema 1: Uso de `stream=false`

**Síntoma:** Logs aparecen en `logs.output` del JSON pero NO en tiempo real.

**Solución:**
```bash
# ❌ ANTES
curl ... ?stream=false

# ✅ DESPUÉS
curl -N ... ?stream=true
```

**En tu código del frontend:**
```javascript
// ✅ Asegúrate de usar streaming
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: message })
});

const reader = response.body.getReader();
// Leer chunks...
```

---

### Problema 2: Falta API Key en el Agente

**Síntoma:** Flow no genera ninguna respuesta.

**Solución:**
1. Abre Langflow
2. Ve al agente "Gerador query"
3. Configura "OpenAI API Key"
4. Guarda
5. Prueba de nuevo

---

### Problema 3: Logger Desconectado (Solo para Main pra Samara)

**Síntoma:** En el flow grande (23a4a54b-1bae-4d1b-a51e-f2d6c5f386a7), el logger tiene 0 conexiones.

**Solución:**
1. Abre el workflow en Langflow
2. Conecta el logger:
   ```
   JWT Validator → Real-Time Logger → Agente Validador
   ```
3. Guarda
4. Prueba

**NOTA:** Este NO es el problema del flow `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`, donde el logger SÍ está conectado.

---

### Problema 4: Backend No Parsea Logs

**Síntoma:** Curl con `stream=true` muestra `[LANGFLOW_LOG]` pero el frontend NO los recibe.

**Solución:**

Actualiza `app/services/langflow_service.py`:

```python
async def stream_chat(self, content: str, token: str):
    """Stream chat responses from Langflow."""

    async for chunk in self._call_langflow_stream(content, token):
        if isinstance(chunk, dict):
            # SSE event
            event_type = chunk.get("event", "message")
            data = chunk.get("data", "")

            # Detectar logs en los datos
            if isinstance(data, str) and "[LANGFLOW_LOG]" in data:
                try:
                    log_json = data.split("[LANGFLOW_LOG]", 1)[1].strip()
                    log_data = json.loads(log_json)

                    # Emitir como evento separado
                    yield {
                        "event": "langflow_log",
                        "data": json.dumps({
                            "type": "langflow_log",
                            "log": log_data
                        })
                    }

                    print(f"[LANGFLOW LOGS] Emitting log: {log_data.get('prefix')}")

                except Exception as e:
                    print(f"[LANGFLOW LOGS] Error parsing log: {e}")

            # Emitir el chunk original también
            yield chunk
```

---

## 🚀 PLAN DE ACCIÓN INMEDIATO

### Paso 1: Ejecutar PRUEBA 1 (2 minutos)

```bash
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: TU_API_KEY_AQUI' \
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

**¿Qué esperar?**
- ✅ Si ves líneas con `[LANGFLOW_LOG]` → **¡FUNCIONA!** Solo necesitas usar `stream=true`
- ❌ Si NO ves nada → Ir a Paso 2

---

### Paso 2: Ejecutar PRUEBA 2 (2 minutos)

Abre Langflow Playground y prueba el flow manualmente.

**¿Genera respuesta?**
- ✅ SÍ → El problema es la API call, revisar backend
- ❌ NO → Ir a Paso 3

---

### Paso 3: Ejecutar PRUEBA 3 (5 minutos)

Verificar API key en el agente "Gerador query".

**¿Tiene API key?**
- ✅ SÍ → Revisar logs de error en Langflow
- ❌ NO → Configurar API key y probar

---

### Paso 4: Verificar Backend (10 minutos)

Si curl con `stream=true` muestra logs pero el frontend NO los recibe, el problema es el backend.

Actualizar código de `langflow_service.py` con el código de **Problema 4** arriba.

---

## 📋 CHECKLIST FINAL

### Antes de contactar soporte:

- [ ] Ejecuté PRUEBA 1 con `stream=true`
- [ ] Ejecuté PRUEBA 2 en Playground o con JSON
- [ ] Verifiqué que el agente tenga API key
- [ ] Verifiqué que el backend esté corriendo
- [ ] Revisé logs de error en la consola del backend
- [ ] Revisé logs de error en la consola de Langflow (F12)

### Información para reportar:

- [ ] Resultado de PRUEBA 1 (copiar output completo)
- [ ] Resultado de PRUEBA 2 (¿genera respuesta?)
- [ ] Screenshot del agente "Gerador query" mostrando configuración
- [ ] Logs de la consola del backend
- [ ] Versión de Langflow que usas

---

## 🎯 RESUMEN: 80% de Probabilidad

Basándome en toda la evidencia:

### 🔴 Causa Más Probable (80%):
**Estás usando `stream=false` en tu frontend/backend**

**Por qué:**
- El componente logger TIENE el código correcto ✅
- El logger ESTÁ conectado en el flujo ✅
- Los logs se generan (viste 3 logs en el output) ✅
- Pero NO llegan en tiempo real al frontend ❌

**Solución:**
Cambiar todas las llamadas a la API de Langflow para usar `stream=true`:

```javascript
// En tu frontend
const url = `/api/chat/stream`; // Asegúrate de que use streaming

// En tu backend (si llama a Langflow)
const langflowUrl = `${LANGFLOW_URL}/api/v1/run/${FLOW_ID}?stream=true`; // ← stream=true
```

---

### 🟡 Causa Alternativa (15%):
**El backend NO está parseando los logs correctamente**

**Solución:**
Actualizar `langflow_service.py` con el código de detección de `[LANGFLOW_LOG]`.

---

### 🟢 Causa Menos Probable (5%):
**Falta API key en el agente o flow no se ejecuta**

**Solución:**
Verificar configuración del agente en Langflow UI.

---

## 📞 SIGUIENTE PASO

**EJECUTA PRUEBA 1 AHORA:**

Reemplaza `TU_API_KEY` con tu API key real y copia-pega este comando:

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
  }' 2>&1 | grep -E "\[LANGFLOW_LOG\]|langflow_log|event:"
```

**Copia y pega el resultado completo para diagnóstico final.**

---

**Archivos de Referencia:**
- `RealTimeLogger_COPIAR_EN_LANGFLOW.py` - Código del logger (ya implementado)
- `test_logs_flow.sh` - Script de pruebas automáticas
- `DIAGNOSTICO_COMPLETO_WORKFLOW.md` - Análisis del flow grande
- Este archivo - Guía definitiva de troubleshooting

---

**Última actualización:** 2025-11-13
**Estado:** 🎯 LISTO PARA EJECUTAR PRUEBAS
