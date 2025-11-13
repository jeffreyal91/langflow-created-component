#!/usr/bin/env python3
"""
Cliente Completo para Langflow - Ver Logs en Tiempo Real
"""

import requests
import json
import time
from typing import Dict, Any, Generator

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

LANGFLOW_URL = "http://syssa-main-lb-1018751800.sa-east-1.elb.amazonaws.com:7860"
API_KEY = "TU_API_KEY_AQUI"  # ⚠️ CAMBIAR POR TU API KEY
TEXT_INPUT_ID = "TextInput-Kw2w4"

# ============================================================================
# CLIENTE LANGFLOW
# ============================================================================

class LangflowClient:
    """Cliente para interactuar con Langflow y ver logs en tiempo real"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        """Headers para las requests"""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    def _build_payload(self, message: str, session_id: str) -> Dict[str, Any]:
        """Construye el payload para la request"""
        return {
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                TEXT_INPUT_ID: {
                    "input_value": message
                }
            },
            "session_id": session_id
        }

    def send_message_no_stream(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Envía mensaje SIN streaming (stream=false)
        Los logs aparecen al final en el JSON completo
        """
        url = f"{self.base_url}/api/v1/run/{TEXT_INPUT_ID}?stream=false"
        headers = self._get_headers()
        payload = self._build_payload(message, session_id)

        print(f"📤 Enviando request a: {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    def send_message_with_stream(
        self,
        message: str,
        session_id: str = "default"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Envía mensaje CON streaming (stream=true)
        Los logs aparecen en tiempo real como eventos SSE
        """
        url = f"{self.base_url}/api/v1/run/{TEXT_INPUT_ID}?stream=true"
        headers = self._get_headers()
        payload = self._build_payload(message, session_id)

        print(f"📤 Enviando request streaming a: {url}")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            # Leer eventos SSE línea por línea
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')

                    # Los eventos SSE tienen formato: "event: XXX" y "data: {...}"
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remover "data: "

                        try:
                            event_data = json.loads(data_str)
                            yield event_data
                        except json.JSONDecodeError:
                            # A veces vienen strings simples
                            yield {"raw_data": data_str}

        except requests.exceptions.RequestException as e:
            yield {"error": str(e), "status": "failed"}


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def print_separator(char="=", length=70):
    """Imprime una línea separadora"""
    print(char * length)


def print_log_event(event: Dict[str, Any]):
    """
    Imprime un evento de log con formato visual
    """
    # Emojis por tipo de log
    emoji_map = {
        "01_JWT_VALIDADO": "🔐",
        "02_VALIDACAO_SEGURANCA": "🛡️",
        "03_DECISAO_PROCESSO": "🧭",
        "04_TIPO_PERGUNTA": "❓",
        "05_PEDIDOS_GERAL": "📦",
        "06_PEDIDOS_ESPECIALISTA": "🎯",
        "07_SUPRIMENTOS_GERAL": "🏭",
        "08_SUPR_REQUISICAO": "📋",
        "09_SUPR_COMPRA": "💰",
        "10_SUPR_MATERIAIS": "📦",
        "11_SUPR_CENTRO_CUSTO": "💵",
        "12_ESTOQUE_GERAL": "📊",
        "13_ESTOQUE_ESPECIALISTA": "🎯"
    }

    # Verificar si es un evento de log
    if "log" in event:
        log_data = event["log"]

        # Extraer información del log
        if isinstance(log_data, dict):
            name = log_data.get("name", "UNKNOWN")
            message_data = log_data.get("message", {})

            if isinstance(message_data, dict):
                prefix = message_data.get("prefix", "UNKNOWN")
                level = message_data.get("level", "INFO")
                message = message_data.get("message", "")
                timestamp = message_data.get("timestamp", "")
                data = message_data.get("data", None)

                # Seleccionar emoji
                emoji = emoji_map.get(prefix, "📝")

                print(f"\n{emoji} [{prefix}] - {level}")
                if timestamp:
                    print(f"   ⏰ {timestamp}")
                print(f"   💬 {message}")

                if data:
                    # Truncar data si es muy largo
                    data_str = str(data)
                    if len(data_str) > 200:
                        data_str = data_str[:200] + "..."
                    print(f"   📄 Data: {data_str}")

                print("   " + "-" * 60)
            else:
                print(f"\n📝 Log: {message_data}")

    # Si es un evento de mensaje final
    elif "message" in event:
        print(f"\n💬 MENSAJE FINAL:")
        print(f"   {event['message']}")

    # Si es otro tipo de evento
    elif "chunk" in event:
        print(".", end="", flush=True)  # Mostrar progreso

    # Evento desconocido
    else:
        print(f"\n🔍 Evento: {json.dumps(event, indent=2)[:200]}")


def extract_logs_from_response(response: Dict[str, Any]) -> list:
    """
    Extrae logs del JSON de respuesta (cuando stream=false)
    """
    logs = []

    # Los logs pueden estar en varios lugares según la estructura
    if "logs" in response:
        logs_data = response["logs"]

        # Si logs es un dict con "output"
        if isinstance(logs_data, dict) and "output" in logs_data:
            for log_entry in logs_data["output"]:
                logs.append(log_entry)

        # Si logs es una lista directamente
        elif isinstance(logs_data, list):
            logs = logs_data

    return logs


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_sin_streaming():
    """
    Ejemplo 1: Sin streaming (stream=false)
    Los logs aparecen al final
    """
    print_separator()
    print("EJEMPLO 1: SIN STREAMING (stream=false)")
    print_separator()

    client = LangflowClient(LANGFLOW_URL, API_KEY)

    message = "ola"
    print(f"\n💬 Mensaje: {message}\n")

    # Enviar sin streaming
    result = client.send_message_no_stream(message, session_id="test-001")

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    # Extraer y mostrar logs
    logs = extract_logs_from_response(result)

    print(f"\n📊 Se encontraron {len(logs)} logs:\n")

    for log_entry in logs:
        name = log_entry.get("name", "UNKNOWN")
        message_data = log_entry.get("message", {})

        if isinstance(message_data, dict):
            prefix = message_data.get("prefix", "")
            level = message_data.get("level", "INFO")
            msg = message_data.get("message", "")
            timestamp = message_data.get("timestamp", "")
            data = message_data.get("data", None)

            print(f"📝 [{name}]")
            print(f"   Prefix: {prefix}")
            print(f"   Level: {level}")
            print(f"   Message: {msg}")
            if timestamp:
                print(f"   Timestamp: {timestamp}")
            if data:
                data_str = str(data)
                if len(data_str) > 150:
                    data_str = data_str[:150] + "..."
                print(f"   Data: {data_str}")
            print()

    # Mostrar respuesta final
    print("\n💬 RESPUESTA FINAL:")
    if "outputs" in result:
        for output_key, output_value in result["outputs"].items():
            if isinstance(output_value, dict) and "message" in output_value:
                print(f"   {output_value['message']}")

    print_separator()


def ejemplo_con_streaming():
    """
    Ejemplo 2: Con streaming (stream=true)
    Los logs aparecen en tiempo real mientras el flow se ejecuta
    """
    print_separator()
    print("EJEMPLO 2: CON STREAMING (stream=true)")
    print_separator()

    client = LangflowClient(LANGFLOW_URL, API_KEY)

    message = "ola"
    print(f"\n💬 Mensaje: {message}")
    print("\n📡 Conectando a logs en tiempo real...\n")

    # Enviar con streaming
    for event in client.send_message_with_stream(message, session_id="test-002"):
        if "error" in event:
            print(f"\n❌ Error: {event['error']}")
            break
        else:
            print_log_event(event)

    print("\n✅ Flujo completado")
    print_separator()


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    print("\n" + "="*70)
    print("🚀 CLIENTE LANGFLOW - VER LOGS EN TIEMPO REAL")
    print("="*70)

    # Verificar configuración
    if API_KEY == "TU_API_KEY_AQUI":
        print("\n⚠️  ERROR: Debes configurar tu API_KEY en la línea 14")
        print("    Edita: API_KEY = 'tu_api_key_real'\n")
        return

    print("\n¿Qué ejemplo quieres ejecutar?")
    print("1. Sin streaming (stream=false) - Logs al final")
    print("2. Con streaming (stream=true) - Logs en tiempo real")
    print("3. Ambos")

    opcion = input("\nSelecciona (1/2/3): ").strip()

    if opcion == "1":
        ejemplo_sin_streaming()
    elif opcion == "2":
        ejemplo_con_streaming()
    elif opcion == "3":
        ejemplo_sin_streaming()
        print("\n")
        time.sleep(2)
        ejemplo_con_streaming()
    else:
        print("❌ Opción inválida")

    print("\n✅ Script finalizado\n")


if __name__ == "__main__":
    main()
