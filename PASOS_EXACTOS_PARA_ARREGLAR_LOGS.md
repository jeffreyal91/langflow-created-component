# 🚀 Pasos Exactos Para Arreglar los Logs (5 Minutos)

## 📋 Paso 1: Copiar el Código Corregido

1. **Abre el archivo:** `RealTimeLogger_COPIAR_EN_LANGFLOW.py`
2. **Selecciona TODO el código** (Ctrl+A)
3. **Copia** (Ctrl+C)

---

## 🔧 Paso 2: Actualizar el Componente en Langflow

### 2.1 Abrir Langflow
```
http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860
```

### 2.2 Ir al Workflow
1. Busca el workflow: **ID `23a4a54b-1bae-4d1b-a51e-f2d6c5f386a7`**
2. Haz clic para abrirlo

### 2.3 Editar el Componente Real-Time Logger
1. Localiza el componente **"Real-Time Logger"** en el canvas
   - ID del componente: `RealTimeLogger-vwujw`
   - Busca el ícono de Monitor 🖥️
2. **Haz clic derecho** sobre el componente → **"Edit"** o **"Code"**
3. **BORRA TODO** el código existente
4. **PEGA** el código que copiaste (Ctrl+V)
5. **Haz clic en "Save"** o **"Guardar"**

### 2.4 Guardar el Workflow
1. Presiona **Ctrl+S** o haz clic en **"Save"** arriba
2. Espera la confirmación de que se guardó

---

## 🧪 Paso 3: Probar que Funciona

### 3.1 Test desde Terminal

Copia y ejecuta esto en tu terminal:

```bash
# Obtener token
TOKEN=$(curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"empresa": 1, "username": "intersys", "password": "1234"}' \
  -s | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."
echo ""
echo "=== BUSCANDO LOGS ==="

# Enviar mensaje y buscar logs
timeout 30 curl -N -X POST "http://localhost:5000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content": "ola"}' 2>&1 | grep -E "\[LANGFLOW_LOG\]|langflow_log" | head -20
```

### 3.2 ¿Qué Debes Ver?

✅ **SI FUNCIONA, verás algo como:**
```
data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","level":"INFO","message":"Processing data in Real-Time Logger","timestamp":"2025-11-13T..."}

event: langflow_log
data: {"type":"langflow_log","log":{"prefix":"03_DECISAO_PROCESSO",...}}

data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","message":"Input data received",...}

event: langflow_log
data: {"type":"langflow_log","log":{...}}

data: [LANGFLOW_LOG] {"prefix":"03_DECISAO_PROCESSO","message":"Processing completed",...}

event: langflow_log
data: {"type":"langflow_log","log":{...}}
```

❌ **SI NO FUNCIONA, verás:**
```
(nada o solo eventos sin [LANGFLOW_LOG])
```

---

## 🔍 Paso 4: Ver Logs en el Backend

### 4.1 Mirar la Consola del Backend

Ve a donde está corriendo tu backend (donde ejecutaste `python app/main.py`)

Deberías ver:
```
[LANGFLOW LOGS] Found log in message: [LANGFLOW_LOG] {...}
[LANGFLOW LOGS] Parsed log data: {'prefix': '03_DECISAO_PROCESSO', ...}
[LANGFLOW LOGS] Emitting log from message
```

---

## 🎯 Paso 5: Verificar en el Frontend

### 5.1 Abrir el Chat en el Navegador

1. Ve a: `http://localhost:5000` (o tu URL de Replit)
2. Haz login
3. Envía: "ola"

### 5.2 Abrir Consola del Navegador

1. Presiona **F12**
2. Ve a la pestaña **"Console"**
3. Deberías ver mensajes como:
   ```
   📝 LOG: {prefix: "03_DECISAO_PROCESSO", level: "INFO", ...}
   ```

---

## ✅ Checklist de Verificación

Marca cada paso que completaste:

### En Langflow:
- [ ] Copié el código de `RealTimeLogger_COPIAR_EN_LANGFLOW.py`
- [ ] Abrí Langflow en el navegador
- [ ] Localicé el workflow correcto
- [ ] Edité el componente Real-Time Logger
- [ ] Pegué el nuevo código
- [ ] Guardé el componente
- [ ] Guardé el workflow

### En Terminal:
- [ ] Ejecuté el test con curl
- [ ] Vi líneas con `[LANGFLOW_LOG]`
- [ ] Vi eventos `langflow_log`

### En Backend:
- [ ] Vi logs en la consola del backend
- [ ] Los logs dicen "Found log in message"
- [ ] Los logs dicen "Emitting log from message"

### En Frontend:
- [ ] Envié un mensaje en el chat
- [ ] Abrí la consola del navegador (F12)
- [ ] Vi logs en la consola

---

## 🆘 Troubleshooting

### ❌ Problema 1: No veo `[LANGFLOW_LOG]` en el test

**Causa:** El componente no se guardó correctamente o está desconectado.

**Solución:**
1. Ve a Langflow
2. Verifica que el componente **Real-Time Logger** esté **conectado** en el workflow
3. Debe haber una línea que conecte:
   ```
   [Componente Anterior] → [Real-Time Logger] → [Componente Siguiente]
   ```
4. Si no está conectado, conéctalo
5. Guarda el workflow
6. Prueba de nuevo

---

### ❌ Problema 2: Veo `[LANGFLOW_LOG]` pero no `event: langflow_log`

**Causa:** El backend no está parseando los logs.

**Solución:**
1. Verifica que el backend esté corriendo
2. Revisa el archivo `app/services/langflow_service.py`
3. Debe tener este código:
   ```python
   if "[LANGFLOW_LOG]" in chunk_text:
       log_json = chunk_text.split("[LANGFLOW_LOG]", 1)[1].strip()
       log_data = json.loads(log_json)
       yield {
           "event": "langflow_log",
           "data": json.dumps({"type": "langflow_log", "log": log_data})
       }
   ```
4. Si no está, agrégalo
5. Reinicia el backend
6. Prueba de nuevo

---

### ❌ Problema 3: Funciona en curl pero no en frontend

**Causa:** El frontend no está escuchando el evento correcto.

**Solución:**

Verifica tu código JavaScript:

```javascript
// ✅ CORRECTO
eventSource.addEventListener('langflow_log', (event) => {
  const log = JSON.parse(event.data);
  console.log('📝 LOG:', log);
  // Mostrar en UI
});

// ❌ INCORRECTO
eventSource.onmessage = (event) => {
  // Esto NO captura eventos 'langflow_log'
};
```

---

## 📊 Diagrama del Flujo de Logs

```
Langflow (RealTimeLogger)
    ↓
Envía: Message(text="[LANGFLOW_LOG] {...}")
    ↓
Backend (langflow_service.py)
    ↓
Detecta: "[LANGFLOW_LOG]" en chunk_text
    ↓
Parsea: json.loads(...)
    ↓
Emite: event: langflow_log
       data: {"type":"langflow_log","log":{...}}
    ↓
Frontend (JavaScript)
    ↓
Escucha: eventSource.addEventListener('langflow_log', ...)
    ↓
Muestra: En área flotante y panel de logs
```

---

## 🎯 Resultado Final Esperado

Cuando todo esté funcionando:

### En el Chat:
```
Usuario: "ola"

[Área flotante - aparece 3 segundos]
  ℹ️ [03_DECISAO_PROCESSO] Processing data in Real-Time Logger (14:01:05)
  ℹ️ [03_DECISAO_PROCESSO] Input data received (14:01:05)
  ℹ️ [03_DECISAO_PROCESSO] Processing completed (14:01:05)

[Panel lateral - persiste]
  1. ℹ️ [03_DECISAO_PROCESSO] Processing data in Real-Time Logger
     14:01:05 | Data: {...}

  2. ℹ️ [03_DECISAO_PROCESSO] Input data received
     14:01:05 | Data: "ola"

  3. ℹ️ [03_DECISAO_PROCESSO] Processing completed
     14:01:05
```

---

## 📞 Próximos Pasos

Una vez que funcione con **1 logger** (`03_DECISAO_PROCESSO`), puedes:

1. **Duplicar el logger** 12 veces
2. **Cambiar el `log_prefix`** en cada uno según la tabla:
   - `01_JWT_VALIDADO`
   - `02_VALIDACAO_SEGURANCA`
   - `03_DECISAO_PROCESSO`
   - `04_TIPO_PERGUNTA`
   - etc.
3. **Conectar cada logger** después de cada componente importante
4. Ver **TODO el flujo** paso a paso en tiempo real

---

## 📄 Archivos de Referencia

1. **`RealTimeLogger_COPIAR_EN_LANGFLOW.py`** ⭐ - Código para copiar
2. **`SOLUCION_LOGS_NO_LLEGAN_FRONTEND.md`** - Guía técnica completa
3. **`CONEXIONES_FALTANTES.md`** - Lista de conexiones necesarias
4. **`RESUMEN_RAPIDO.md`** - Resumen visual

---

**Última actualización:** 2025-11-13
**Tiempo estimado:** 5-10 minutos
**Dificultad:** ⭐⭐ Media

---

## 🚀 ¡Empieza Ahora!

1. Abre `RealTimeLogger_COPIAR_EN_LANGFLOW.py`
2. Copia el código
3. Ve a Langflow
4. Pega el código
5. Guarda
6. Prueba con el curl
7. ✅ ¡Listo!
