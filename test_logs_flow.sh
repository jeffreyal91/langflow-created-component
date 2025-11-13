#!/bin/bash

# 🧪 Script de Prueba para Logs en Langflow
# Flow ID: 1c1866c5-0c5a-4b47-884d-f3f4545b80f1

# ⚠️ IMPORTANTE: Reemplaza con tu API key real
API_KEY="YOUR_API_KEY_HERE"

FLOW_ID="1c1866c5-0c5a-4b47-884d-f3f4545b80f1"
LANGFLOW_URL="http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"

echo "=================================================="
echo "🔍 TEST 1: Sin Streaming (stream=false)"
echo "=================================================="
echo ""

curl --request POST \
  --url "${LANGFLOW_URL}/api/v1/run/${FLOW_ID}?stream=false" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: ${API_KEY}" \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    },
    "session_id": "test-session-001"
  }' 2>&1 | python3 -m json.tool

echo ""
echo ""
echo "=================================================="
echo "🔍 TEST 2: Con Streaming (stream=true) - Ver Logs"
echo "=================================================="
echo ""

timeout 30 curl --request POST \
  --url "${LANGFLOW_URL}/api/v1/run/${FLOW_ID}?stream=true" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: ${API_KEY}" \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    },
    "session_id": "test-session-002"
  }' -N 2>&1

echo ""
echo ""
echo "=================================================="
echo "🔍 TEST 3: Buscar [LANGFLOW_LOG] en el Stream"
echo "=================================================="
echo ""

timeout 30 curl --request POST \
  --url "${LANGFLOW_URL}/api/v1/run/${FLOW_ID}?stream=true" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: ${API_KEY}" \
  --data '{
    "output_type": "chat",
    "input_type": "text",
    "tweaks": {
      "TextInput-ghNJt": {
        "input_value": "SELECT 1 FROM DUAL"
      }
    },
    "session_id": "test-session-003"
  }' -N 2>&1 | grep -E "\[LANGFLOW_LOG\]|logs|output" | head -20

echo ""
echo "=================================================="
echo "✅ Tests Completados"
echo "=================================================="
