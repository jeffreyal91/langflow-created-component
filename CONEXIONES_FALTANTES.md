# ⚠️ CONEXIONES FALTANTES EN EL FLOW "Main pra Samara"

## 🔴 PROBLEMAS CRÍTICOS - REQUIEREN ACCIÓN INMEDIATA

### 1. **ProgramaSearchTool NO está conectado a ningún agente**

#### ❌ Problema
El componente `ProgramaSQLComponent-e0mn5` (herramienta de búsqueda SQL) NO tiene conexiones a los agentes que deberían usarlo.

#### ✅ Solución Requerida
Debes conectar la salida `component_as_tool` de **ProgramaSQLComponent-e0mn5** al input `tools` de los siguientes agentes:

| Agente | ID | Necesita Conexión |
|--------|-----|-------------------|
| Agente Validador | Agent-w8SIt | ✅ SÍ |
| Agente Interprete decisor | Agent-qjORE | ✅ SÍ |
| Agente detector perguntas amplas | Agent-SJ5lh | ✅ SÍ |
| Agente Geral Pedidos de Venda | Agent-wXhHc | ✅ SÍ |
| Agente especialista Pedidos de Venda | Agent-BRFbE | ✅ SÍ |
| Agente Geral Estoque | Agent-cIqmG | ✅ SÍ |
| Agente especialista estoque geral | Agent-6tNY5 | ✅ SÍ |
| Agente geral suprimentos | Agent-xF3zE | ✅ SÍ |
| Esp. solicitacao compra | Agent-??? | ✅ SÍ |
| Esp. solicitacao requisicao | Agent-??? | ✅ SÍ |
| Esp. cadastro materiais | Agent-??? | ✅ SÍ |
| Esp suprimentos centro de custo | Agent-??? | ✅ SÍ |

#### 🔧 Cómo Conectar en Langflow UI

1. Abre el flow en Langflow
2. Localiza el componente **ProgramaSQLComponent** (es el cuadro azul con la herramienta de búsqueda)
3. Busca el punto de salida llamado **"component_as_tool"** (es un círculo verde en el lado derecho del componente)
4. Para CADA agente de la lista:
   - Arrastra una línea desde el punto **"component_as_tool"** del ProgramaSQLComponent
   - Conéctala al punto de entrada **"tools"** del agente (círculo en el lado izquierdo)
   - Verifica que la conexión se muestre como una línea continua

#### 📝 Impacto si NO se conecta
- ❌ Los agentes NO podrán buscar información en la base de datos Oracle
- ❌ Las consultas sobre programas, reglas de negocio, etc. fallarán
- ❌ Los agentes solo podrán responder con información general, sin datos reales

---

### 2. **Real-Time Logger NO está conectado al flujo**

#### ❌ Problema
El componente **Real-Time Logger** existe en el flow pero NO tiene conexiones de entrada ni salida, por lo que no está capturando logs.

**ID actual:** `CustomComponent-tKlcR`
**Estado:** ⚠️ Aislado (0 conexiones)

#### ✅ Solución Requerida: DUPLICAR y conectar en múltiples puntos

Para tener logs de **CADA paso del flujo**, necesitas:

1. **Duplicar el Real-Time Logger 12 veces** (total 13 loggers)
2. **Conectar cada uno después de un componente importante**
3. **Dar a cada uno un `log_prefix` único** para identificar la etapa

#### 🗺️ Puntos de Conexión Recomendados

| # | Después de... | log_prefix | Propósito |
|---|---------------|------------|-----------|
| 1 | JWT Validator + Message | `01_JWT_VALIDATED` | Entrada validada |
| 2 | Agente Validador | `02_VALIDACION_SEGURIDAD` | Resultado validación |
| 3 | Agente Interprete decisor | `03_DECISION_PROCESO` | Proceso identificado |
| 4 | Agente detector perguntas | `04_TIPO_PREGUNTA` | Tipo de pregunta |
| 5 | Agente Geral Pedidos | `05_PEDIDOS_GENERAL` | Entrada pedidos |
| 6 | Agente especialista Pedidos | `06_PEDIDOS_ESPECIALISTA` | Respuesta pedidos |
| 7 | Agente geral suprimentos | `07_SUPRIMIENTOS_GENERAL` | Entrada suprimentos |
| 8 | Esp. requisicao | `08_SUPR_REQUISICION` | Requisiciones |
| 9 | Esp. compra | `09_SUPR_COMPRA` | Compras |
| 10 | Esp. materiales | `10_SUPR_MATERIALES` | Materiales |
| 11 | Esp. centro de custo | `11_SUPR_CENTRO_COSTO` | Centros costo |
| 12 | Agente Geral Estoque | `12_ESTOQUE_GENERAL` | Entrada estoque |
| 13 | Agente especialista estoque | `13_ESTOQUE_ESPECIALISTA` | Respuesta estoque |

#### 🔧 Cómo Conectar (Para cada logger)

1. **Duplicar componente:**
   - Selecciona Real-Time Logger existente
   - `Ctrl+C` → `Ctrl+V` (copiar/pegar)
   - Repite 12 veces

2. **Configurar cada logger:**
   - Cambia `log_prefix` según tabla arriba
   - Mantén: `log_input_data = true`, `include_timestamp = true`

3. **Insertar en la cadena:**
   - Rompe conexión existente (ej: `Agente A` → `Agente B`)
   - Inserta logger: `Agente A` → `Logger (input_data)` → `Logger (output)` → `Agente B`

#### 📝 Impacto si NO se conecta
- ❌ No podrás ver logs en tiempo real desde Replit
- ❌ No sabrás qué está procesando cada agente
- ❌ Imposible debuguear dónde falla el flujo
- ❌ La función de streaming (SSE) no mostrará información útil

📖 **Ver guía completa:** `ESTRATEGIA_LOGS_COMPLETOS.md`

---

## 🟡 PROBLEMAS IMPORTANTES - RECOMENDADO ARREGLAR

### 3. **If-Else #2 (Producción) sin destino**

#### ❌ Problema
El componente **If-Else #2** busca `"processo": "producao"` pero NO tiene agentes conectados en la rama TRUE.

#### ✅ Solución
**Opción A:** Crear agentes de producción
```
If-Else #2 (TRUE) → Agente Geral Producción → Agente Especialista Producción → Output
```

**Opción B:** Eliminar el If-Else si no se usa producción
- Si el sistema no maneja procesos de producción, elimina este componente

#### 📝 Impacto
- ⚠️ Consultas sobre producción no serán procesadas
- ⚠️ Usuarios verán error o respuesta vacía

---

### 4. **API Request sin conexión clara**

#### ❌ Problema
Hay un componente **API Request** que no está conectado al flujo principal.

#### ✅ Solución
Debes definir:
1. ¿Qué API se debe llamar?
2. ¿Cuándo debe llamarse? (¿después de qué componente?)
3. ¿Qué se hace con la respuesta?

Luego conectar apropiadamente.

---

## 🟢 VERIFICACIONES OPCIONALES - MEJORAS

### 5. **Múltiples Chat Outputs (7)**

#### ℹ️ Observación
Tienes 7 componentes **Chat Output**, lo cual puede ser intencional pero es inusual.

#### ✅ Recomendación
Verifica que cada ruta del flow tenga su propio output o considera consolidar en un único output.

---

### 6. **Agentes sin System Message personalizado**

#### ℹ️ Observación
Algunos agentes podrían beneficiarse de instrucciones de sistema más específicas.

#### ✅ Recomendación
Para cada agente especializado, agrega un **System Message** detallado con:
- Rol específico
- Formato de respuesta esperado
- Ejemplos de consultas que debe manejar
- Restricciones (qué NO debe hacer)

---

## 📊 RESUMEN DE ACCIONES REQUERIDAS

### Prioridad ALTA (Hacer HOY)
- [ ] Conectar **ProgramaSQLComponent** a TODOS los agentes (12 conexiones)
- [ ] Conectar **Real-Time Logger** al flujo principal

### Prioridad MEDIA (Hacer esta semana)
- [ ] Resolver rama de producción en **If-Else #2**
- [ ] Definir y conectar **API Request**

### Prioridad BAJA (Mejoras futuras)
- [ ] Revisar necesidad de 7 Chat Outputs
- [ ] Mejorar System Messages de agentes
- [ ] Agregar manejo de errores global

---

## 🎯 INSTRUCCIONES PASO A PASO PARA LANGFLOW UI

### Paso 1: Abrir el Flow
1. Accede a Langflow: `http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860`
2. Carga el flow "Main pra Samara (1).json"

### Paso 2: Localizar ProgramaSQLComponent
1. Busca en el canvas el componente llamado **"ProgramaSearchTool"**
2. Es un componente custom (probablemente azul/morado)
3. Verifica que tenga el ID: `ProgramaSQLComponent-e0mn5`

### Paso 3: Conectar a Primer Agente
1. Haz clic en el punto de salida **"component_as_tool"** (lado derecho del componente)
2. Arrastra hasta el **Agente Validador**
3. Suelta en el punto de entrada **"tools"** (lado izquierdo del agente)
4. Verifica que aparezca una línea conectando ambos

### Paso 4: Repetir para Todos los Agentes
1. Repite el Paso 3 para cada uno de los 12 agentes listados arriba
2. Cada agente debe tener una línea desde ProgramaSQLComponent

### Paso 5: Conectar Real-Time Logger
1. Localiza el componente **Real-Time Logger**
2. Decide dónde insertarlo (recomiendo después de JWT Validator)
3. Conecta: `JWT Validator → Real-Time Logger → Agente Validador`

### Paso 6: Guardar y Probar
1. Haz clic en **"Save"** en la esquina superior derecha
2. Haz clic en **"Run"** para probar el flow
3. Envía un mensaje de prueba: "Busca programas relacionados con ventas"
4. Verifica que el agente pueda acceder a la base de datos

---

## 🧪 PRUEBAS RECOMENDADAS DESPUÉS DE CONECTAR

### Test 1: Búsqueda en Base de Datos
```
Mensaje: "¿Qué programas tenemos para pedidos de venta?"
Resultado esperado: El agente debe buscar en la tabla PROGRAMA y retornar resultados
```

### Test 2: Enrutamiento a Suprimientos
```
Mensaje: "Necesito crear una requisición de compra"
Resultado esperado: Debe enrutar a agente de suprimientos y mostrar opciones
```

### Test 3: Logs en Tiempo Real
```
Usar el script de Replit con stream=true
Resultado esperado: Debes ver eventos SSE en la consola
```

---

## 📞 SOPORTE

Si tienes problemas:
1. Verifica los IDs de componentes en el JSON
2. Revisa la consola de Langflow para errores
3. Confirma que la base de datos Oracle esté accesible
4. Prueba primero sin streaming, luego con streaming

---

**Última actualización:** 2025-11-13
**Estado del flow:** ⚠️ REQUIERE CONEXIONES CRÍTICAS
