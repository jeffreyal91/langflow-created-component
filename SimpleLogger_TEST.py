"""
Simple Logger - Componente de Prueba Mínimo
Usa esto para verificar si send_message() funciona en tu instalación de Langflow
"""

from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message
import json
from datetime import datetime


class SimpleLogger(Component):
    """
    Componente de logging MÍNIMO para pruebas.

    Si este componente NO emite logs, el problema es de Langflow.
    Si este componente SÍ emite logs, el problema es el código del logger complejo.
    """

    display_name = "Simple Logger Test"
    description = "Logger mínimo para probar send_message()"
    icon = "Bug"
    name = "SimpleLogger"

    inputs = [
        MessageTextInput(
            name="input_data",
            display_name="Input Data",
            info="Datos para pasar al siguiente componente",
            required=False,
        )
    ]

    outputs = [
        Output(
            name="output",
            display_name="Output",
            method="log_test",
        )
    ]

    async def log_test(self) -> Message:
        """
        Genera UN SOLO log simple y pasa los datos al siguiente componente.
        """

        print("=" * 60)
        print("🟢 SIMPLE LOGGER: Iniciando ejecución")
        print(f"🟢 SIMPLE LOGGER: Input type: {type(self.input_data)}")
        print(f"🟢 SIMPLE LOGGER: Input value: {self.input_data}")
        print("=" * 60)

        # Crear log simple
        log_data = {
            "test": "SIMPLE_LOG_TEST",
            "timestamp": datetime.now().isoformat(),
            "component": "SimpleLogger",
            "input_received": str(self.input_data)[:200] if self.input_data else "None"
        }

        log_msg = Message(
            text=f"[LANGFLOW_LOG] {json.dumps(log_data, ensure_ascii=False)}",
            sender="SimpleLogger"
        )

        print(f"🟢 SIMPLE LOGGER: Mensaje creado:")
        print(f"   Text: {log_msg.text[:150]}...")
        print(f"   Sender: {log_msg.sender}")

        # Intentar enviar mensaje
        try:
            await self.send_message(log_msg)
            print("✅ SIMPLE LOGGER: send_message() ejecutado SIN ERRORES")
        except Exception as e:
            print(f"❌ SIMPLE LOGGER ERROR en send_message(): {e}")
            print("❌ TIPO DE ERROR:", type(e).__name__)
            import traceback
            traceback.print_exc()

        # Crear mensaje de salida (pasar datos al siguiente componente)
        if isinstance(self.input_data, Message):
            output_message = self.input_data
        elif self.input_data:
            if isinstance(self.input_data, str):
                output_message = Message(text=self.input_data)
            else:
                output_message = Message(text=str(self.input_data))
        else:
            output_message = Message(text="No input data received by SimpleLogger")

        print(f"🟢 SIMPLE LOGGER: Output message: {output_message.text[:100]}")
        print("🟢 SIMPLE LOGGER: Finalizando ejecución")
        print("=" * 60)

        return output_message
