# 🔍 Como Ver os Logs em Tempo Real - Guia Completo

## ❓ O Problema

Você está vendo os logs, mas **só no final da execução**, não em tempo real. Por quê?

### 🔴 Com `stream=false` (O que você está usando agora)

```bash
URL: /api/v1/run/input?stream=false
```

**O que acontece:**
1. Você envia a mensagem
2. O flow executa TUDO
3. Só no FINAL você recebe um JSON com:
   - A resposta
   - **TODOS** os logs juntos no campo `"logs"`

**Saída:**
```json
{
  "logs": {
    "output": [
      {
        "name": "03_DECISAO_PROCESSO",
        "message": {...}
      },
      {
        "name": "03_DECISAO_PROCESSO_DETAIL",
        "message": {...}
      },
      {
        "name": "03_DECISAO_PROCESSO_COMPLETE",
        "message": {...}
      }
    ]
  }
}
```

✅ **Os logs estão aí**, mas só aparecem quando tudo termina.

---

### 🟢 Com `stream=true` (O que você precisa usar)

```bash
URL: /api/v1/run/input?stream=true
```

**O que acontece:**
1. Você envia a mensagem
2. A conexão fica **ABERTA** (Server-Sent Events)
3. **Cada log aparece em tempo real** enquanto o flow executa
4. Você vê o processo acontecendo ao vivo

**Saída (em tempo real):**
```
evento 1: {"log": {"name": "01_JWT_VALIDADO", "message": {...}}}
evento 2: {"log": {"name": "02_VALIDACAO_SEGURANCA", "message": {...}}}
evento 3: {"log": {"name": "03_DECISAO_PROCESSO", "message": {...}}}
...
```

✅ **Você VÊ cada etapa em tempo real**

---

## ✅ Como Usar Stream=True no Replit

### Opção 1: Script Python Completo (Recomendado)

Copiei um script completo em: **`replit_client_completo.py`**

**Como usar:**

1. **Edita a linha 14:**
   ```python
   API_KEY = "SUA_API_KEY_AQUI"  # ⚠️ TROCAR
   ```

2. **Executa:**
   ```bash
   python replit_client_completo.py
   ```

3. **Escolhe a opção 2:** "Con streaming"

4. **Verás os logs assim:**
   ```
   🔐 [01_JWT_VALIDADO] - INFO
      ⏰ 2025-11-13T14:01:05.700434
      💬 Processing data in Real-Time Logger
      📄 Data: ola
      ------------------------------------------------------------

   🛡️ [02_VALIDACAO_SEGURANCA] - INFO
      ⏰ 2025-11-13T14:01:07.123456
      💬 Processing data in Real-Time Logger
      📄 Data: Usuario validado
      ------------------------------------------------------------

   🧭 [03_DECISAO_PROCESSO] - INFO
      ⏰ 2025-11-13T14:01:09.456789
      💬 Input data received
      📄 Data: {"processo": "outros", "tipo": "outros"}
      ------------------------------------------------------------
   ```

---

### Opção 2: Script Simples

Se você quiser algo mais simples:

```python
import requests

LANGFLOW_URL = "http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"
API_KEY = "SUA_API_KEY"

def ver_logs_tempo_real(mensagem):
    url = f"{LANGFLOW_URL}/api/v1/run/TextInput-Kw2w4?stream=true"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "TextInput-Kw2w4": {
                "input_value": mensagem
            }
        },
        "session_id": "test-session"
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)

    # Ler eventos SSE
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                print(line_str[6:])  # Imprimir sem "data: "

# Usar
ver_logs_tempo_real("ola")
```

---

## 🎯 Diferença Visual

### ❌ SEM Streaming (stream=false)
```
Enviando mensagem...
⏳ Esperando...
⏳ Esperando...
⏳ Esperando...
✅ Resposta recebida!

Logs:
- 01_JWT_VALIDADO
- 02_VALIDACAO_SEGURANCA
- 03_DECISAO_PROCESSO
- ...todos juntos no final
```

### ✅ COM Streaming (stream=true)
```
Enviando mensagem...
📝 01_JWT_VALIDADO - Validando entrada...
📝 02_VALIDACAO_SEGURANCA - Usuario autorizado
📝 03_DECISAO_PROCESSO - Processo identificado: outros
📝 04_TIPO_PERGUNTA - Pergunta detectada
✅ Resposta completa!
```

---

## 🔧 Estrutura dos Eventos SSE

Quando você usa `stream=true`, os eventos chegam assim:

### Evento de Log
```json
{
  "log": {
    "name": "03_DECISAO_PROCESSO",
    "message": {
      "prefix": "03_DECISAO_PROCESSO",
      "level": "INFO",
      "message": "Processing data in Real-Time Logger",
      "timestamp": "2025-11-13T14:01:05.700434",
      "data": "conteúdo aqui"
    },
    "type": "object"
  }
}
```

### Evento de Chunk (pedaços da resposta)
```json
{
  "chunk": "parte da resposta..."
}
```

### Evento de Mensagem Final
```json
{
  "message": "resposta completa aqui"
}
```

---

## 📋 Lista de Prefixos dos Logs (em português)

Quando você conectar os 13 Real-Time Loggers, verá estes prefixos:

```
01_JWT_VALIDADO              🔐 Entrada validada
02_VALIDACAO_SEGURANCA       🛡️ Validação de segurança
03_DECISAO_PROCESSO          🧭 Decisão de processo
04_TIPO_PERGUNTA             ❓ Tipo de pergunta
05_PEDIDOS_GERAL             📦 Pedidos geral
06_PEDIDOS_ESPECIALISTA      🎯 Pedidos especialista
07_SUPRIMENTOS_GERAL         🏭 Suprimentos geral
08_SUPR_REQUISICAO           📋 Requisição
09_SUPR_COMPRA               💰 Compra
10_SUPR_MATERIAIS            📦 Materiais
11_SUPR_CENTRO_CUSTO         💵 Centro de custo
12_ESTOQUE_GERAL             📊 Estoque geral
13_ESTOQUE_ESPECIALISTA      🎯 Estoque especialista
```

---

## 🧪 Teste Rápido

### 1. No Terminal do Replit:

```bash
curl -X POST \
  'http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860/api/v1/run/TextInput-Kw2w4?stream=true' \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: SUA_API_KEY' \
  -d '{
    "output_type": "chat",
    "input_type": "chat",
    "tweaks": {
      "TextInput-Kw2w4": {
        "input_value": "ola"
      }
    },
    "session_id": "test"
  }'
```

Se funcionar, você verá linhas começando com `data: {...}` aparecendo em tempo real.

---

## 🆘 Troubleshooting

### Problema: Não vejo nenhum log mesmo com stream=true

**Causa 1:** O Real-Time Logger não está conectado no flow
**Solução:** Conecte os loggers conforme `RESUMEN_RAPIDO.md`

**Causa 2:** `log_input_data` está desativado
**Solução:** No logger, ative: `log_input_data = true`

**Causa 3:** Está usando a saída `logs` em vez de `output`
**Solução:** Conecte a saída **`output`** do logger, não `logs`

---

### Problema: Vejo logs mas não têm dados úteis

**Solução:** Ative no logger:
- ✅ `log_input_data = true`
- ✅ `include_timestamp = true`
- ✅ `include_metadata = true`

---

### Problema: Conexão SSE fecha antes de terminar

**Causa:** Timeout muito curto
**Solução:** Aumente o timeout:
```python
response = requests.post(url, stream=True, timeout=300)  # 5 minutos
```

---

## 📊 Exemplo de Saída Completa com 13 Loggers

Quando você tiver todos os loggers conectados e executar uma consulta de pedidos:

```
🚀 Monitoreando flow completo...

🔐 [01_JWT_VALIDADO]
   Processing data in Real-Time Logger
   Data: "Quais são os pedidos pendentes?"
   ------------------------------------------------------------

🛡️ [02_VALIDACAO_SEGURANCA]
   Input data received
   Data: Usuario autorizado para consulta de pedidos
   ------------------------------------------------------------

🧭 [03_DECISAO_PROCESSO]
   Input data received
   Data: {"processo": "pedido_venda", "tipo": "consulta"}
   ------------------------------------------------------------

❓ [04_TIPO_PERGUNTA]
   Input data received
   Data: Pergunta específica detectada
   ------------------------------------------------------------

📦 [05_PEDIDOS_GERAL]
   Input data received
   Data: Consultando base de dados de pedidos...
   ------------------------------------------------------------

🎯 [06_PEDIDOS_ESPECIALISTA]
   Input data received
   Data: Encontrados 5 pedidos pendentes: #123, #124, #125...
   ------------------------------------------------------------

✅ Completado
```

---

## 🎯 Resumo

| Aspecto | stream=false | stream=true |
|---------|--------------|-------------|
| **Logs** | Só no final | Em tempo real |
| **Conexão** | Fecha rápido | Fica aberta |
| **Visualização** | Tudo junto | Passo a passo |
| **Debugging** | Difícil | Fácil |
| **Recomendado para** | Testes rápidos | Produção/Monitoramento |

---

## ✅ Próximos Passos

1. ✅ Usa o script `replit_client_completo.py`
2. ✅ Testa com `stream=true`
3. ✅ Verifica que os logs aparecem em tempo real
4. ✅ Conecta os outros 12 loggers no flow
5. ✅ Testa novamente e vê o flow completo

---

**Última atualização:** 2025-11-13
**Status:** ✅ GUIA COMPLETO - PRONTO PARA USO
