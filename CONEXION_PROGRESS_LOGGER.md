# 🎯 Cómo Conectar el Progress Logger Simple

**Para el flow:** `1c1866c5-0c5a-4b47-884d-f3f4545b80f1` (Query and Output)

---

## 📍 Dónde Conectar Cada Logger

Tu flow actual:
```
TextInput → Agent Gerador → SQL → Parser → Agent Formatador → Output
```

Insertar 5 loggers:
```
TextInput
  ↓
[Logger 1: Recibe input]
  ↓
Agent Gerador
  ↓
[Logger 2: Genera query SQL]
  ↓
SQL Component
  ↓
[Logger 3: Ejecuta query Oracle]
  ↓
Parser
  ↓
[Logger 4: Procesa resultado]
  ↓
Agent Formatador
  ↓
[Logger 5: Formatea resultado]
  ↓
Output
```

---

## 🔧 PASO 1: Crear el Componente

1. Abre Langflow
2. Crea nuevo componente "Custom"
3. Copia y pega el código de `ProgressLogger_SIMPLE.py`
4. Guarda como "Progress Logger"

---

## 🔧 PASO 2: Agregar 5 Instancias

1. En el canvas, agrega **5 veces** el componente "Progress Logger"
2. Configura cada uno:

### Logger 1: Después de TextInput
- **Nombre del Paso:** `Input recibido`
- **Ícono:** `📥`

### Logger 2: Después de Agent Gerador
- **Nombre del Paso:** `Query SQL generada`
- **Ícono:** `🔍`

### Logger 3: Después de SQL Component
- **Nombre del Paso:** `Query ejecutada en Oracle`
- **Ícono:** `💾`

### Logger 4: Después de Parser
- **Nombre del Paso:** `Resultado procesado`
- **Ícono:** `⚙️`

### Logger 5: Después de Agent Formatador
- **Nombre del Paso:** `Resultado formateado`
- **Ícono:** `✨`

---

## 🔧 PASO 3: Conectar los Loggers

### Conexión 1:
```
TextInput (output)
  ↓ conectar a
Logger 1 (input_data)
  ↓ conectar desde output a
Agent Gerador (input)
```

### Conexión 2:
```
Agent Gerador (output)
  ↓ conectar a
Logger 2 (input_data)
  ↓ conectar desde output a
SQL Component (query)
```

### Conexión 3:
```
SQL Component (output)
  ↓ conectar a
Logger 3 (input_data)
  ↓ conectar desde output a
Parser (input)
```

### Conexión 4:
```
Parser (output)
  ↓ conectar a
Logger 4 (input_data)
  ↓ conectar desde output a
Agent Formatador (input)
```

### Conexión 5:
```
Agent Formatador (output)
  ↓ conectar a
Logger 5 (input_data)
  ↓ conectar desde output a
ChatOutput (message)
```

---

## 🔧 PASO 4: Guardar y Probar

1. Guarda el workflow (Ctrl+S)
2. Ejecuta con `stream=true`:

```bash
curl -N --request POST \
  --url 'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/1c1866c5-0c5a-4b47-884d-f3f4545b80f1?stream=true' \
  --header 'x-api-key: TU_API_KEY' \
  --header 'Content-Type: application/json' \
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

## ✅ Resultado Esperado

Verás en el stream:

```json
// Logger 1
event: message
data: [LANGFLOW_LOG] {"step":"Input recibido","icon":"📥","timestamp":"2025-11-13T...","status":"in_progress","preview":"SELECT 1 FROM DUAL"}

// Logger 2
event: message
data: [LANGFLOW_LOG] {"step":"Query SQL generada","icon":"🔍","timestamp":"2025-11-13T...","status":"in_progress","preview":"SELECT 1 FROM DUAL"}

// Logger 3
event: message
data: [LANGFLOW_LOG] {"step":"Query ejecutada en Oracle","icon":"💾","timestamp":"2025-11-13T...","status":"in_progress","preview":"1"}

// Logger 4
event: message
data: [LANGFLOW_LOG] {"step":"Resultado procesado","icon":"⚙️","timestamp":"2025-11-13T...","status":"in_progress"}

// Logger 5
event: message
data: [LANGFLOW_LOG] {"step":"Resultado formateado","icon":"✨","timestamp":"2025-11-13T...","status":"in_progress","preview":"<table>...</table>"}
```

---

## 🎨 Cómo Mostrar en el Frontend

### Opción 1: Área Flotante Simple

```javascript
// En tu frontend JavaScript
eventSource.addEventListener('message', (event) => {
  const data = event.data;

  // Detectar logs
  if (data.includes('[LANGFLOW_LOG]')) {
    const match = data.match(/\[LANGFLOW_LOG\]\s*(\{.*?\})/);
    if (match) {
      const log = JSON.parse(match[1]);

      // Mostrar notificación flotante
      showToast(`${log.icon} ${log.step}`);
    }
  }
});

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: #4361ee;
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    z-index: 9999;
    animation: slideIn 0.3s ease;
  `;

  document.body.appendChild(toast);

  // Remover después de 2 segundos
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}
```

---

### Opción 2: Barra de Progreso

```javascript
const steps = [
  "Input recibido",
  "Query SQL generada",
  "Query ejecutada en Oracle",
  "Resultado procesado",
  "Resultado formateado"
];

let currentStep = 0;

eventSource.addEventListener('message', (event) => {
  const data = event.data;

  if (data.includes('[LANGFLOW_LOG]')) {
    const match = data.match(/\[LANGFLOW_LOG\]\s*(\{.*?\})/);
    if (match) {
      const log = JSON.parse(match[1]);

      currentStep++;
      const progress = (currentStep / steps.length) * 100;

      // Actualizar barra de progreso
      updateProgressBar(progress, log.step, log.icon);
    }
  }
});

function updateProgressBar(progress, stepName, icon) {
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');

  progressBar.style.width = progress + '%';
  progressText.textContent = `${icon} ${stepName}`;
}
```

```html
<!-- HTML para la barra de progreso -->
<div style="width: 100%; background: #e0e0e0; border-radius: 10px; overflow: hidden;">
  <div id="progress-bar" style="width: 0%; height: 30px; background: linear-gradient(90deg, #4361ee, #7209b7); transition: width 0.5s ease;"></div>
</div>
<div id="progress-text" style="margin-top: 10px; text-align: center; font-weight: bold;"></div>
```

---

### Opción 3: Lista de Pasos

```javascript
const stepsList = document.getElementById('steps-list');

eventSource.addEventListener('message', (event) => {
  const data = event.data;

  if (data.includes('[LANGFLOW_LOG]')) {
    const match = data.match(/\[LANGFLOW_LOG\]\s*(\{.*?\})/);
    if (match) {
      const log = JSON.parse(match[1]);

      // Agregar paso a la lista
      const stepItem = document.createElement('div');
      stepItem.className = 'step-item';
      stepItem.innerHTML = `
        <span class="step-icon">${log.icon}</span>
        <span class="step-name">${log.step}</span>
        <span class="step-status">✓</span>
      `;
      stepsList.appendChild(stepItem);
    }
  }
});
```

```html
<!-- HTML para lista de pasos -->
<div id="steps-list" style="max-width: 400px; margin: 20px auto;"></div>

<style>
.step-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-left: 4px solid #4361ee;
  margin-bottom: 10px;
  border-radius: 4px;
  animation: fadeIn 0.5s ease;
}

.step-icon {
  font-size: 24px;
  margin-right: 12px;
}

.step-name {
  flex: 1;
  font-weight: 500;
}

.step-status {
  color: #28a745;
  font-weight: bold;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
```

---

## 🔍 Troubleshooting

### ❌ No aparecen logs

**Verificar:**
1. Cada logger tiene las conexiones (entrante Y saliente)
2. Las líneas están en verde
3. Ejecutas con `stream=true`
4. El código del Progress Logger es correcto

**Debug:**
1. Abre consola del navegador en Langflow (F12)
2. Ejecuta el flow desde Playground
3. Busca errores en rojo

---

### ❌ Los logs aparecen pero no se muestran en frontend

**Verificar:**
1. Tu código JavaScript escucha el evento `message`
2. Estás detectando `[LANGFLOW_LOG]` correctamente
3. El parsing JSON funciona
4. La función de mostrar (toast, barra, lista) se ejecuta

**Debug:**
```javascript
eventSource.addEventListener('message', (event) => {
  console.log('Evento recibido:', event.data);

  if (event.data.includes('[LANGFLOW_LOG]')) {
    console.log('✅ Log detectado!');
    const match = event.data.match(/\[LANGFLOW_LOG\]\s*(\{.*?\})/);
    if (match) {
      const log = JSON.parse(match[1]);
      console.log('📝 Log parseado:', log);
    }
  }
});
```

---

## 📊 Resumen

### Qué logra esto:

✅ **5 logs simples** que muestran progreso del flow
✅ **En tiempo real** con streaming
✅ **Información mínima**: nombre del paso, ícono, timestamp
✅ **Fácil de mostrar** en frontend (toast, barra, lista)

### Lo que NO hace:

❌ **NO** muestra todos los detalles internos
❌ **NO** loguea cada componente pequeño
❌ **NO** genera archivos de logs pesados

---

## 🎯 Resultado Final

**En el frontend verás:**

```
📥 Input recibido
🔍 Query SQL generada
💾 Query ejecutada en Oracle
⚙️ Resultado procesado
✨ Resultado formateado
```

**Simple, limpio, en tiempo real.**

---

**Última actualización:** 2025-11-13
**Para flow:** `1c1866c5-0c5a-4b47-884d-f3f4545b80f1`
