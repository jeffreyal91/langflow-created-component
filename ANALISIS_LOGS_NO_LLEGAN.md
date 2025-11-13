# 🔴 Análisis: Logs No Llegan del Flow 1c1866c5-0c5a-4b47-884d-f3f4545b80f1

## 📊 Información del Flow

- **Flow ID:** `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
- **Endpoint:** `http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860`
- **Input Component:** `TextInput-ghNJt`
- **Input Value:** `SELECT 1 FROM DUAL`

---

## 🔍 Diagnóstico: Por Qué No Llegan Logs

### Causas Posibles

#### 1️⃣ **El Flow NO Tiene Real-Time Logger**

**Probabilidad:** 🔴 ALTA

**Verificar:**
- Abre Langflow en el navegador
- Ve al flow con ID `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
- Busca componentes llamados "Real-Time Logger"

**Si NO hay loggers:**
→ Los logs nunca se generan, por eso no llegan

**Solución:**
1. Agregar componente Real-Time Logger
2. Usar el código de `RealTimeLogger_COPIAR_EN_LANGFLOW.py`
3. Conectar en el flujo

---

#### 2️⃣ **El Logger Usa `self.log()` en Vez de `send_message()`**

**Probabilidad:** 🔴 ALTA

**Problema:**
```python
# ❌ ESTO NO TRANSMITE VÍA SSE
self.log(message=data, name="log_name")
```

**Verificar:**
1. Abre el componente Real-Time Logger
2. Revisa el código
3. Busca `self.log(` en el código

**Si usa `self.log()`:**
→ Los logs se guardan en JSON final pero NO se transmiten en tiempo real

**Solución:**
Cambiar a:
```python
# ✅ ESTO SÍ TRANSMITE VÍA SSE
log_msg = Message(
    text=f"[LANGFLOW_LOG] {json.dumps(log_data)}",
    sender="RealTimeLogger"
)
await self.send_message(log_msg)
```

---

#### 3️⃣ **El Logger Está Desconectado**

**Probabilidad:** 🟡 MEDIA

**Verificar:**
1. Abre el flow en Langflow
2. Busca el componente Real-Time Logger
3. Verifica que tenga:
   - ✅ Línea entrante (flecha verde que llega)
   - ✅ Línea saliente (flecha verde que sale)

**Si NO tiene conexiones:**
→ El logger nunca se ejecuta

**Solución:**
Conectar entre dos componentes:
```
[Componente A] → [Real-Time Logger] → [Componente B]
```

---

#### 4️⃣ **Estás Usando `stream=false`**

**Probabilidad:** 🟡 MEDIA

**Problema:**
Con `stream=false`, los logs aparecen en el JSON final pero NO en tiempo real.

**Tu comando actual:**
```bash
curl ... ?stream=false
```

**Verificar:**
Cambia a `stream=true`:
```bash
curl ... ?stream=true
```

**Con `stream=true`:**
- ✅ Los logs aparecen en tiempo real
- ✅ Usas SSE (Server-Sent Events)
- ✅ Puedes ver el progreso del flow

**Con `stream=false`:**
- ❌ Solo ves el resultado final
- ❌ Los logs están en `response.logs.output` al final
- ❌ No puedes ver progreso en tiempo real

---

#### 5️⃣ **El Flow Tiene Errores y No Se Ejecuta**

**Probabilidad:** 🟢 BAJA

**Verificar:**
1. Ejecuta el script `test_logs_flow.sh`
2. Mira la respuesta del TEST 1 (sin streaming)
3. Busca:
   ```json
   {
     "outputs": [{"outputs": []}]  // ← VACÍO = ERROR
   }
   ```

**Si outputs está vacío:**
→ El flow no se está ejecutando correctamente

**Verificar en Langflow:**
1. Abre el Playground
2. Envía: "SELECT 1 FROM DUAL"
3. ¿Genera respuesta?
   - ✅ SÍ → El problema es solo de logs
   - ❌ NO → Hay errores en el flow

---

## 🧪 Cómo Probar

### Paso 1: Ejecutar el Script de Prueba

```bash
# 1. Editar el script con tu API key
nano test_logs_flow.sh

# 2. Cambiar esta línea:
API_KEY="YOUR_API_KEY_HERE"
# Por:
API_KEY="tu_api_key_real"

# 3. Dar permisos de ejecución
chmod +x test_logs_flow.sh

# 4. Ejecutar
./test_logs_flow.sh
```

### Paso 2: Analizar Resultados

**TEST 1 (stream=false):**
```json
{
  "logs": {
    "output": [
      {"name": "LOG_NAME", "message": {...}}  // ← ¿HAY LOGS AQUÍ?
    ]
  },
  "outputs": [...]
}
```

✅ **Si hay logs en `logs.output`:**
→ El logger funciona pero NO transmite vía SSE (problema de código)

❌ **Si NO hay logs:**
→ El logger no se está ejecutando (desconectado o no existe)

---

**TEST 2 (stream=true):**
```
event: message
data: {...}

event: logs  // ← ¿HAY ESTE EVENTO?
data: {...}
```

✅ **Si ves eventos con `event: logs`:**
→ Los logs se transmiten correctamente

❌ **Si NO ves eventos de logs:**
→ El logger no usa `send_message()` o está desconectado

---

**TEST 3 (grep LANGFLOW_LOG):**
```
data: [LANGFLOW_LOG] {"prefix":"...", ...}  // ← ¿APARECE ESTO?
```

✅ **Si ves `[LANGFLOW_LOG]`:**
→ El logger funciona con el código correcto

❌ **Si NO aparece:**
→ El logger no está enviando mensajes con el formato correcto

---

## 📋 Checklist de Verificación

### En Langflow (UI):
- [ ] El flow existe y se puede abrir
- [ ] Hay al menos un componente "Real-Time Logger"
- [ ] El logger tiene conexiones entrantes y salientes
- [ ] El logger está en el flujo principal (no aislado)
- [ ] El flow funciona en Playground

### En el Código del Logger:
- [ ] El componente usa `await self.send_message()`
- [ ] Los mensajes tienen formato `[LANGFLOW_LOG] {json}`
- [ ] El código es la versión corregida
- [ ] No usa `self.log()` para logs de tiempo real

### En la Ejecución:
- [ ] Usas `stream=true` para ver logs en tiempo real
- [ ] La API key es válida
- [ ] El flow se ejecuta (outputs no está vacío)
- [ ] No hay errores en la respuesta

---

## 🎯 Plan de Acción

### Prioridad 1: Verificar Si Hay Logger

```bash
# Ver estructura del flow
curl --request GET \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/flows/1c1866c5-0c5a-4b47-884d-f3f4545b80f1' \
  --header "x-api-key: YOUR_API_KEY" \
  | python3 -m json.tool | grep -i "logger\|log"
```

---

### Prioridad 2: Probar en Playground

1. Abre: http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
2. Ve al flow: `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
3. Haz clic en "Playground"
4. Envía: "SELECT 1 FROM DUAL"
5. ¿Genera respuesta?

---

### Prioridad 3: Agregar/Actualizar Logger

Si no hay logger o usa código antiguo:

1. Usar el código de `RealTimeLogger_COPIAR_EN_LANGFLOW.py`
2. Crear o actualizar componente
3. Conectar en el flujo
4. Guardar

---

### Prioridad 4: Probar con Streaming

```bash
# Ejecutar con stream=true
./test_logs_flow.sh

# O manualmente:
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'Content-Type: application/json' \
  --header "x-api-key: YOUR_API_KEY" \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }'
```

---

## 🔍 Debugging Avanzado

### Ver Qué Componentes Tiene el Flow

```bash
# Descargar definición del flow
curl --request GET \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/flows/1c1866c5-0c5a-4b47-884d-f3f4545b80f1' \
  --header "x-api-key: YOUR_API_KEY" \
  > flow_definition.json

# Ver componentes
cat flow_definition.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
nodes = data.get('data', {}).get('nodes', [])
for node in nodes:
    node_type = node.get('data', {}).get('type', 'Unknown')
    node_id = node.get('id', 'Unknown')
    display_name = node.get('data', {}).get('node', {}).get('display_name', 'N/A')
    print(f'{node_type} - {display_name} ({node_id})')
"
```

---

### Ver Logs en el JSON Final

```bash
# Ejecutar sin streaming y ver logs
curl --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=false' \
  --header 'Content-Type: application/json' \
  --header "x-api-key: YOUR_API_KEY" \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    }
  }' | python3 -c "
import json, sys
data = json.load(sys.stdin)
logs = data.get('logs', {}).get('output', [])
print(f'Total logs: {len(logs)}')
for log in logs:
    print(f'- {log.get(\"name\")}: {log.get(\"message\", {})}')
"
```

---

## 📊 Comparación: stream=false vs stream=true

| Aspecto | stream=false | stream=true |
|---------|--------------|-------------|
| **Logs en tiempo real** | ❌ No | ✅ Sí |
| **Formato de respuesta** | JSON completo | SSE events |
| **Ver progreso** | ❌ No | ✅ Sí |
| **Logs al final** | ✅ En `logs.output` | ⚠️ Solo si usa SSE |
| **Uso recomendado** | Testing rápido | Producción/Monitoring |

---

## 🎯 Resultado Esperado

**Cuando funcione correctamente:**

```bash
# Con stream=true
curl ... ?stream=true

# Deberías ver:
event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","level":"INFO","message":"Processing..."}

event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","message":"Input data received"}

event: message
data: [LANGFLOW_LOG] {"prefix":"FLOW_LOG","message":"Processing completed"}

event: end
data: {"result": {...}}
```

---

## 📞 Próximos Pasos

1. **Ejecuta:** `./test_logs_flow.sh` (con tu API key)
2. **Pega** los resultados de los 3 tests
3. **Te diré** exactamente qué está fallando
4. **Aplicaremos** la solución específica

---

**Archivos de Referencia:**
- `test_logs_flow.sh` - Script de prueba
- `RealTimeLogger_COPIAR_EN_LANGFLOW.py` - Código del logger
- `PASOS_EXACTOS_PARA_ARREGLAR_LOGS.md` - Guía paso a paso

---

**Última actualización:** 2025-11-13
**Estado:** 🔴 ESPERANDO RESULTADOS DE PRUEBAS
