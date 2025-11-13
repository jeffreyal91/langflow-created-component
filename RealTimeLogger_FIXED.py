"""
Real-Time Logger Component for Langflow - VERSIÓN CORREGIDA
Envía logs como mensajes para que aparezcan en SSE
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
            info="Prefijo para identificar este logger en el flow",
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
        BoolInput(
            name="send_as_messages",
            display_name="Send Logs as Messages",
            info="Enviar logs como mensajes (recomendado para SSE)",
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
        Procesa los datos de entrada, genera logs y retorna el output.
        """
        # Construir el log entry principal
        log_entry = self._build_log_entry()

        # Enviar log principal
        await self._send_log(log_entry, f"{self.log_prefix}")

        # Log detallado con los datos de entrada
        if self.log_input_data and self.input_data:
            detail_log = {
                "prefix": self.log_prefix,
                "level": self.log_level,
                "message": "Input data received",
                "data": self._serialize_data(self.input_data),
            }
            await self._send_log(detail_log, f"{self.log_prefix}_DETAIL")

        # Crear mensaje de salida (pasar los datos al siguiente nodo)
        if isinstance(self.input_data, Message):
            output_message = self.input_data
        elif self.input_data:
            output_message = Message(text=str(self.input_data))
        else:
            output_message = Message(text="No input data")

        # Log de finalización
        completion_log = {
            "prefix": self.log_prefix,
            "level": "INFO",
            "message": "Processing completed",
            "timestamp": datetime.now().isoformat() if self.include_timestamp else None,
        }
        await self._send_log(completion_log, f"{self.log_prefix}_COMPLETE")

        return output_message

    async def _send_log(self, log_data: dict, log_name: str):
        """
        Envía un log, ya sea como mensaje o usando self.log()
        """
        if self.send_as_messages:
            # Enviar como mensaje para que aparezca en SSE
            log_message = Message(
                text=f"[LANGFLOW_LOG] {json.dumps(log_data, ensure_ascii=False)}",
                sender="RealTimeLogger",
            )
            await self.send_message(log_message)
        else:
            # Usar el método tradicional (no aparece en SSE)
            self.log(message=log_data, name=log_name)

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
