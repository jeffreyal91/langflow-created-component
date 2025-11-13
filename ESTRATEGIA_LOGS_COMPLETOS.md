# 🔍 Estrategia para Logs Completos de Todo el Flujo

## 🎯 Objetivo
Capturar logs en tiempo real de **CADA componente** del flujo Samara para ver todo el proceso de ejecución.

---

## 📋 ESTRATEGIA: Múltiples Real-Time Loggers

### ✅ Solución Recomendada
Duplicar el componente **Real-Time Logger** y colocarlo después de cada agente importante con un `log_prefix` diferente.

---

## 🗺️ MAPA DE LOGGERS A AGREGAR

### 📍 **Logger #1: Después de JWT Validator**
```
JWT Validator + Message
    ↓
🔷 Real-Time Logger #1
    ↓
Agente Validador
```
**Configuración:**
- **log_prefix:** `"01_JWT_VALIDATED"`
- **Propósito:** Capturar entrada validada del usuario

---

### 📍 **Logger #2: Después de Agente Validador**
```
Agente Validador
    ↓
🔷 Real-Time Logger #2
    ↓
Agente Interprete decisor
```
**Configuración:**
- **log_prefix:** `"02_VALIDACION_SEGURIDAD"`
- **Propósito:** Ver resultado de validación de seguridad

---

### 📍 **Logger #3: Después de Agente Interprete decisor**
```
Agente Interprete decisor
    ↓
🔷 Real-Time Logger #3
    ↓
Agente detector perguntas amplas
```
**Configuración:**
- **log_prefix:** `"03_DECISION_PROCESO"`
- **Propósito:** Ver qué proceso fue identificado (pedidos, suprimientos, etc.)

---

### 📍 **Logger #4: Después de Agente detector perguntas amplas**
```
Agente detector perguntas amplas
    ↓
🔷 Real-Time Logger #4
    ↓
If-Else (Branch selector)
```
**Configuración:**
- **log_prefix:** `"04_TIPO_PREGUNTA"`
- **Propósito:** Ver si es pregunta amplia o específica

---

### 📍 **Logger #5: En rama de Pedidos de Venta**
```
If-Else #1 (TRUE) → Agente Geral Pedidos de Venda
    ↓
🔷 Real-Time Logger #5
    ↓
Agente especialista Pedidos de Venda
```
**Configuración:**
- **log_prefix:** `"05_PEDIDOS_GENERAL"`
- **Propósito:** Ver procesamiento general de pedidos

---

### 📍 **Logger #6: Después de Especialista Pedidos**
```
Agente especialista Pedidos de Venda
    ↓
🔷 Real-Time Logger #6
    ↓
Run Flow / Output
```
**Configuración:**
- **log_prefix:** `"06_PEDIDOS_ESPECIALISTA"`
- **Propósito:** Ver respuesta final del especialista

---

### 📍 **Logger #7: En rama de Suprimientos (General)**
```
If-Else #3 (TRUE) → Agente geral suprimentos
    ↓
🔷 Real-Time Logger #7
    ↓
[Sub-branches de suprimientos]
```
**Configuración:**
- **log_prefix:** `"07_SUPRIMIENTOS_GENERAL"`
- **Propósito:** Ver entrada a suprimientos

---

### 📍 **Logger #8-11: Subramas de Suprimientos**
```
Esp. solicitacao requisicao → 🔷 Logger #8 ("08_SUPR_REQUISICION")
Esp. solicitacao compra → 🔷 Logger #9 ("09_SUPR_COMPRA")
Esp. cadastro materiais → 🔷 Logger #10 ("10_SUPR_MATERIALES")
Esp suprimentos centro de custo → 🔷 Logger #11 ("11_SUPR_CENTRO_COSTO")
```

---

### 📍 **Logger #12: En rama de Estoque**
```
If-Else #4 (TRUE) → Agente Geral Estoque
    ↓
🔷 Real-Time Logger #12
    ↓
Agente especialista estoque geral
```
**Configuración:**
- **log_prefix:** `"12_ESTOQUE_GENERAL"`

---

### 📍 **Logger #13: Después de Especialista Estoque**
```
Agente especialista estoque geral
    ↓
🔷 Real-Time Logger #13
    ↓
Output
```
**Configuración:**
- **log_prefix:** `"13_ESTOQUE_ESPECIALISTA"`

---

## 🔧 INSTRUCCIONES PASO A PASO EN LANGFLOW

### Paso 1: Duplicar el Componente Real-Time Logger

#### Opción A: Copiar/Pegar en UI
1. Selecciona el componente **Real-Time Logger** existente (`CustomComponent-tKlcR`)
2. Copia: `Ctrl+C` (Windows/Linux) o `Cmd+C` (Mac)
3. Pega: `Ctrl+V` o `Cmd+V`
4. Repite 12 veces (para tener 13 loggers en total)

#### Opción B: Crear desde Custom Components
1. En el sidebar, busca "Custom Components"
2. Encuentra "Real-Time Logger"
3. Arrástralo al canvas
4. Repite 13 veces

---

### Paso 2: Configurar Cada Logger

Para cada logger duplicado:

1. **Haz clic en el componente**
2. **Cambia el campo `log_prefix`** según la tabla de arriba
3. **Verifica que estén habilitados:**
   - ✅ `include_timestamp` = true
   - ✅ `include_metadata` = true
   - ✅ `log_input_data` = true
4. **`log_level`** = "INFO" (o "DEBUG" si quieres más detalle)

---

### Paso 3: Conectar Cada Logger en Su Posición

Para **CADA** logger:

#### A) Romper la conexión existente
- Ejemplo: `Agente Validador` → `Agente Interprete decisor`
- Haz clic en la línea → DELETE

#### B) Insertar el logger
- Conecta: `Agente Validador` → `Logger #2 (input_data)`
- Conecta: `Logger #2 (output)` → `Agente Interprete decisor`

**⚠️ IMPORTANTE:**
- La entrada del logger es **`input_data`**
- La salida del logger es **`output`** (NO uses `logs`, esa es para debugging)

---

## 📊 RESULTADO ESPERADO

### En Replit, verás logs como estos en tiempo real:

```python
# Usuario envía: "¿Cuáles son los pedidos de venta pendientes?"

📝 Log: {
  "prefix": "01_JWT_VALIDATED",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:00.123",
  "message": "Processing data in Real-Time Logger",
  "data": {
    "type": "Message",
    "text": "¿Cuáles son los pedidos de venta pendientes?",
    "sender": "User"
  }
}

📝 Log: {
  "prefix": "02_VALIDACION_SEGURIDAD",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:02.456",
  "message": "Processing data in Real-Time Logger",
  "data": {
    "type": "Message",
    "text": "Usuario validado. Consulta permitida sobre pedidos de venta.",
    "sender": "Agent"
  },
  "metadata": {
    "component_id": "CustomComponent-xxx",
    "component_name": "RealTimeLogger",
    "vertex_id": "Agent-w8SIt"
  }
}

📝 Log: {
  "prefix": "03_DECISION_PROCESO",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:05.789",
  "message": "Processing data in Real-Time Logger",
  "data": {
    "type": "Message",
    "text": "{\"processo\": \"pedido_venda\", \"categoria\": \"consulta\"}",
    "sender": "Agent"
  }
}

📝 Log: {
  "prefix": "04_TIPO_PREGUNTA",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:07.012",
  "data": {
    "type": "Message",
    "text": "Pregunta específica detectada. Enrutando a especialista."
  }
}

📝 Log: {
  "prefix": "05_PEDIDOS_GENERAL",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:10.345",
  "data": "Buscando pedidos pendientes en la base de datos..."
}

📝 Log: {
  "prefix": "06_PEDIDOS_ESPECIALISTA",
  "level": "INFO",
  "timestamp": "2025-11-13T10:30:15.678",
  "data": {
    "type": "Message",
    "text": "Encontrados 5 pedidos pendientes:\n1. Pedido #123 - Cliente ABC\n2. Pedido #124 - Cliente XYZ\n..."
  }
}
```

---

## 🎯 VENTAJAS DE ESTA ESTRATEGIA

✅ **Visibilidad completa:** Ves TODO el flujo paso a paso

✅ **Debugging fácil:** Si algo falla, sabes exactamente en qué paso

✅ **Identificación clara:** Cada log tiene un prefix único

✅ **Timestamps:** Puedes medir tiempo entre pasos

✅ **Metadata:** Incluye IDs de componentes para debugging profundo

✅ **SSE automático:** Todo se transmite en tiempo real a Replit

---

## 🔍 ALTERNATIVA: Usar Flow Monitor (1 solo componente)

### ⚠️ Limitación
El componente `FlowMonitor` (definido en el código del Real-Time Logger) puede capturar eventos globales, pero **NO captura el contenido de cada agente**, solo eventos de inicio/fin de flow.

### Cuándo Usar Flow Monitor
- Si solo necesitas saber CUÁNDO empieza y termina el flow
- Si quieres métricas generales (tiempo total, número de logs)
- Si NO necesitas ver el contenido de cada paso

### Nuestra Recomendación
**Usa múltiples Real-Time Loggers** (la estrategia de arriba) para tener visibilidad completa del contenido de cada paso.

---

## 🧪 SCRIPT DE REPLIT MEJORADO PARA VER TODOS LOS LOGS

```python
#!/usr/bin/env python3
"""
Cliente mejorado con visualización de logs por etapa
"""

import json
from datetime import datetime
from langflow_client import LangflowClient

def print_log_with_stage(event):
    """Imprime log con formato visual por etapa"""

    # Si es un error
    if "error" in event:
        print(f"\n❌ ERROR: {event['error']}")
        return

    # Extraer información del log
    prefix = event.get("prefix", "UNKNOWN")
    level = event.get("level", "INFO")
    timestamp = event.get("timestamp", datetime.now().isoformat())
    message = event.get("message", "")
    data = event.get("data", "")

    # Emojis por etapa
    stage_emojis = {
        "01_JWT_VALIDATED": "🔐",
        "02_VALIDACION_SEGURIDAD": "🛡️",
        "03_DECISION_PROCESO": "🧭",
        "04_TIPO_PREGUNTA": "❓",
        "05_PEDIDOS_GENERAL": "📦",
        "06_PEDIDOS_ESPECIALISTA": "🎯",
        "07_SUPRIMIENTOS_GENERAL": "🏭",
        "08_SUPR_REQUISICION": "📋",
        "09_SUPR_COMPRA": "💰",
        "10_SUPR_MATERIALES": "📦",
        "11_SUPR_CENTRO_COSTO": "💵",
        "12_ESTOQUE_GENERAL": "📊",
        "13_ESTOQUE_ESPECIALISTA": "🎯"
    }

    emoji = stage_emojis.get(prefix, "📝")

    # Imprimir con formato
    print(f"\n{emoji} [{prefix}] - {timestamp}")
    print(f"   {message}")

    if data:
        # Si data es un dict/objeto, mostrarlo formateado
        if isinstance(data, dict):
            data_str = json.dumps(data, indent=2, ensure_ascii=False)
            print(f"   Data:\n{data_str}")
        else:
            # Truncar si es muy largo
            data_str = str(data)[:200]
            print(f"   Data: {data_str}")

    print("   " + "-" * 60)


def main():
    print("🚀 Iniciando Monitoreo de Flujo Completo")
    print("=" * 70)

    client = LangflowClient()

    # Mensaje de prueba
    message = "¿Cuáles son los pedidos de venta pendientes del cliente ABC?"

    print(f"\n💬 Enviando mensaje: {message}")
    print("=" * 70)
    print("\n📡 Conectando a logs en tiempo real...\n")

    # Stream con visualización mejorada
    for event in client.stream_response(message, session_id="monitoring-session-001"):
        print_log_with_stage(event)

    print("\n✅ Flujo completado")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### En Langflow:
- [ ] Duplicar Real-Time Logger 12 veces (total 13 loggers)
- [ ] Configurar `log_prefix` único en cada uno
- [ ] Conectar Logger #1 después de JWT Validator
- [ ] Conectar Logger #2 después de Agente Validador
- [ ] Conectar Logger #3 después de Agente Interprete
- [ ] Conectar Logger #4 después de Agente detector
- [ ] Conectar Loggers #5-6 en rama de Pedidos de Venta
- [ ] Conectar Logger #7 en entrada de Suprimientos
- [ ] Conectar Loggers #8-11 en subramas de Suprimientos
- [ ] Conectar Loggers #12-13 en rama de Estoque
- [ ] Guardar el flow
- [ ] Probar en Playground con un mensaje

### En Replit:
- [ ] Copiar el script mejorado de arriba
- [ ] Ejecutar con streaming habilitado
- [ ] Verificar que los logs aparecen con los prefixes correctos
- [ ] Confirmar que se ven TODOS los pasos del flujo

---

## 🆘 TROUBLESHOOTING

### Problema: No veo logs de algún logger específico
**Causa:** El flujo no está pasando por ese componente
**Solución:** Verifica que el logger esté correctamente conectado en la cadena

### Problema: Veo logs duplicados
**Causa:** Dos loggers con el mismo `log_prefix`
**Solución:** Revisa que cada logger tenga un prefix único

### Problema: Los logs no tienen `data`
**Causa:** `log_input_data` está en `false`
**Solución:** Activa `log_input_data` en la configuración del logger

### Problema: No aparece ningún log
**Causa posible #1:** Real-Time Logger no está usando la salida correcta
**Solución:** Verifica que estés conectando desde la salida `output`, NO desde `logs`

**Causa posible #2:** El streaming no está habilitado en la request
**Solución:** Verifica que uses `stream=true` en la URL de la API

---

## 📚 DOCUMENTACIÓN TÉCNICA

### Cómo Funciona el Real-Time Logger

El componente usa el método `self.log()` de Langflow que:

1. Captura el log internamente
2. Lo envía al sistema de streaming de Langflow
3. Langflow lo transmite vía Server-Sent Events (SSE)
4. Tu cliente en Replit lo recibe en tiempo real

**Flujo de datos:**
```
Componente → Logger.log() → Langflow Stream → SSE → Replit
```

### Formato de Logs SSE

```json
{
  "event": "message",
  "data": {
    "prefix": "01_JWT_VALIDATED",
    "level": "INFO",
    "message": "Processing data in Real-Time Logger",
    "timestamp": "2025-11-13T10:30:00.123Z",
    "data": {
      "type": "Message",
      "text": "contenido del mensaje",
      "sender": "User"
    },
    "metadata": {
      "component_id": "CustomComponent-tKlcR",
      "component_name": "RealTimeLogger",
      "display_name": "Real-Time Logger",
      "vertex_id": "CustomComponent-xbkRa"
    }
  }
}
```

---

**Última actualización:** 2025-11-13
**Estado:** ✅ ESTRATEGIA COMPLETA LISTA PARA IMPLEMENTAR
