"""
Real-Time Logger - Versión Corregida para SSE
Copiar y pegar COMPLETO en Langflow
"""

from typing import Any
from datetime import datetime
import json

from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, BoolInput, Output, StrInput
from langflow.schema.message import Message
from langflow.schema import Data


class RealTimeLogger(Component):
    """
    Componente que captura y transmite logs en tiempo real.
    Los logs se envían como mensajes vía SSE.
    """

    display_name = "Real-Time Logger"
    description = "Captura y transmite logs en tiempo real vía Server-Sent Events (SSE)"
    icon = "Monitor"
    name = "RealTimeLogger"

    inputs = [
        MessageTextInput(
            name="input_data",
            display_name="Input Data",
            info="Datos que quieres loguear y pasar al siguiente nodo",
            required=False,
        ),
        StrInput(
            name="log_prefix",
            display_name="Log Prefix",
            info="Prefijo para identificar este logger en el flow (ej: 01_JWT_VALIDADO)",
            value="FLOW_LOG",
        ),
        DropdownInput(
            name="log_level",
            display_name="Log Level",
            info="Nivel de log",
            options=["INFO", "DEBUG", "WARNING", "ERROR"],
            value="INFO",
        ),
        BoolInput(
            name="include_timestamp",
            display_name="Include Timestamp",
            info="Incluir timestamp en cada log",
            value=True,
        ),
        BoolInput(
            name="include_metadata",
            display_name="Include Metadata",
            info="Incluir metadata del componente (ID, nombre, etc)",
            value=True,
        ),
        BoolInput(
            name="log_input_data",
            display_name="Log Input Data",
            info="Loguear el contenido de los datos de entrada",
            value=True,
        ),
    ]

    outputs = [
        Output(
            name="output",
            display_name="Output",
            method="process_and_log",
        ),
    ]

    async def process_and_log(self) -> Message:
        """
        Procesa los datos de entrada, genera logs en tiempo real y retorna el output.

        IMPORTANTE: Los logs se envían como mensajes con formato [LANGFLOW_LOG]
        para que se transmitan vía SSE.
        """

        # ============================================================
        # LOG 1: Inicio del procesamiento
        # ============================================================
        log_entry = self._build_log_entry()

        log_message_1 = Message(
            text=f"[LANGFLOW_LOG] {json.dumps(log_entry, ensure_ascii=False)}",
            sender="RealTimeLogger",
        )
        await self.send_message(log_message_1)

        # ============================================================
        # LOG 2: Datos de entrada (si está habilitado)
        # ============================================================
        if self.log_input_data and self.input_data:
            detail_log = {
                "prefix": self.log_prefix,
                "level": self.log_level,
                "message": "Input data received",
                "data": self._serialize_data(self.input_data),
            }

            if self.include_timestamp:
                detail_log["timestamp"] = datetime.now().isoformat()

            log_message_2 = Message(
                text=f"[LANGFLOW_LOG] {json.dumps(detail_log, ensure_ascii=False)}",
                sender="RealTimeLogger",
            )
            await self.send_message(log_message_2)

        # ============================================================
        # Crear mensaje de salida (pasar datos al siguiente nodo)
        # ============================================================
        if isinstance(self.input_data, Message):
            output_message = self.input_data
        elif self.input_data:
            # Si es string, mantener como string
            if isinstance(self.input_data, str):
                output_message = Message(text=self.input_data)
            else:
                output_message = Message(text=str(self.input_data))
        else:
            output_message = Message(text="No input data")

        # ============================================================
        # LOG 3: Finalización del procesamiento
        # ============================================================
        completion_log = {
            "prefix": self.log_prefix,
            "level": "INFO",
            "message": "Processing completed",
        }

        if self.include_timestamp:
            completion_log["timestamp"] = datetime.now().isoformat()

        log_message_3 = Message(
            text=f"[LANGFLOW_LOG] {json.dumps(completion_log, ensure_ascii=False)}",
            sender="RealTimeLogger",
        )
        await self.send_message(log_message_3)

        return output_message

    def _build_log_entry(self) -> dict[str, Any]:
        """Construye el entry de log con toda la información configurada."""
        log_entry: dict[str, Any] = {
            "prefix": self.log_prefix,
            "level": self.log_level,
            "message": f"Processing data in {self.display_name}",
        }

        if self.include_timestamp:
            log_entry["timestamp"] = datetime.now().isoformat()

        if self.include_metadata:
            log_entry["metadata"] = {
                "component_id": self._id,
                "component_name": self.name,
                "display_name": self.display_name,
                "vertex_id": self._vertex.id if self._vertex else None,
            }

        return log_entry

    def _serialize_data(self, data: Any) -> Any:
        """Serializa los datos para logging."""
        try:
            # Si es un Message, extraer el texto
            if isinstance(data, Message):
                return {
                    "type": "Message",
                    "text": str(data.text)[:500],  # Limitar longitud
                    "sender": data.sender,
                }

            # Si es un Data object
            if isinstance(data, Data):
                return {
                    "type": "Data",
                    "data": str(data.data)[:500],
                }

            # Si es serializable directamente
            if isinstance(data, (str, int, float, bool, list, dict)):
                return data

            # Fallback: convertir a string
            return str(data)[:500]

        except Exception as e:
            return f"Error serializing data: {str(e)}"
