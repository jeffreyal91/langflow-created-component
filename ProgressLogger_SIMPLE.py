"""
Progress Logger - Logger Simple para Mostrar Progreso del Flow
Emite solo logs esenciales en tiempo real
"""

from langflow.custom import Component
from langflow.io import MessageTextInput, StrInput, Output
from langflow.schema.message import Message
import json
from datetime import datetime


class ProgressLogger(Component):
    """
    Logger simple que emite eventos de progreso del flow.

    Usa esto para mostrar en el frontend:
    - Cuando se recibe input
    - Cuando un agente se ejecuta
    - Cuando se completa una operación
    """

    display_name = "Progress Logger"
    description = "Emite logs simples de progreso en tiempo real"
    icon = "Activity"
    name = "ProgressLogger"

    inputs = [
        MessageTextInput(
            name="input_data",
            display_name="Input Data",
            info="Datos del componente anterior",
            required=False,
        ),
        StrInput(
            name="step_name",
            display_name="Nombre del Paso",
            info="Ej: 'Genera query SQL', 'Ejecuta query Oracle', 'Formatea resultado'",
            value="Procesando",
        ),
        StrInput(
            name="icon",
            display_name="Ícono",
            info="Emoji para mostrar en el frontend",
            value="⚙️",
        ),
    ]

    outputs = [
        Output(
            name="output",
            display_name="Output",
            method="emit_progress",
        )
    ]

    async def emit_progress(self) -> Message:
        """
        Emite UN SOLO log simple y pasa los datos al siguiente componente.
        """

        # Log simple
        log_data = {
            "step": self.step_name,
            "icon": self.icon,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }

        # Agregar preview de los datos (solo si existen y son cortos)
        if self.input_data:
            data_preview = str(self.input_data)[:150]
            if len(data_preview) > 100:
                data_preview = data_preview[:100] + "..."
            log_data["preview"] = data_preview

        # Crear mensaje con formato [LANGFLOW_LOG]
        log_msg = Message(
            text=f"[LANGFLOW_LOG] {json.dumps(log_data, ensure_ascii=False)}",
            sender="ProgressLogger"
        )

        # Enviar log
        try:
            await self.send_message(log_msg)
        except Exception as e:
            print(f"❌ ProgressLogger ERROR: {e}")

        # Pasar datos al siguiente componente sin modificar
        if isinstance(self.input_data, Message):
            return self.input_data
        elif self.input_data:
            if isinstance(self.input_data, str):
                return Message(text=self.input_data)
            else:
                return Message(text=str(self.input_data))
        else:
            return Message(text="")
