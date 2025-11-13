"""
Real-Time Logger Component for Langflow
Captura y transmite logs en tiempo real vía Server-Sent Events (SSE)
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
    Los logs se envían automáticamente vía SSE al frontend.
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
    ]

    outputs = [
        Output(
            name="output",
            display_name="Output",
            method="process_and_log",
        ),
        Output(
            name="logs",
            display_name="Logs",
            method="get_logs",
        ),
    ]

    async def process_and_log(self) -> Message:
        """
        Procesa los datos de entrada, genera logs en tiempo real y retorna el output.
        """
        # Construir el log entry
        log_entry = self._build_log_entry()

        # Enviar log (esto automáticamente se transmite vía SSE)
        self.log(message=log_entry, name=f"{self.log_prefix}")

        # Log adicional con información detallada
        if self.log_input_data and self.input_data:
            detail_log = {
                "prefix": self.log_prefix,
                "level": self.log_level,
                "message": "Input data received",
                "data": self._serialize_data(self.input_data),
            }
            self.log(message=detail_log, name=f"{self.log_prefix}_DETAIL")

        # Crear mensaje de salida
        output_text = self.input_data if self.input_data else "No input data"
        message = Message(text=output_text)

        # Enviar mensaje (también se transmite vía SSE)
        await self.send_message(message)

        # Log de finalización
        completion_log = {
            "prefix": self.log_prefix,
            "level": "INFO",
            "message": "Processing completed",
            "timestamp": datetime.now().isoformat() if self.include_timestamp else None,
        }
        self.log(message=completion_log, name=f"{self.log_prefix}_COMPLETE")

        return message

    def get_logs(self) -> Data:
        """
        Retorna todos los logs capturados hasta el momento.
        """
        logs_data = []
        for log in self._logs:
            logs_data.append({
                "name": log.name,
                "message": log.message,
                "type": log.type,
            })

        return Data(data={"logs": logs_data, "count": len(logs_data)})

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


class FlowMonitor(Component):
    """
    Monitor global que captura eventos de todo el flow.
    Este componente debe colocarse al inicio o al final del flow.
    """

    display_name = "Flow Monitor"
    description = "Monitor global que captura y reporta eventos de todo el flow"
    icon = "Activity"
    name = "FlowMonitor"

    inputs = [
        MessageTextInput(
            name="trigger",
            display_name="Trigger",
            info="Conecta esto para activar el monitor (puede ser cualquier dato)",
            required=False,
        ),
        BoolInput(
            name="log_flow_start",
            display_name="Log Flow Start",
            info="Loguear cuando el flow inicia",
            value=True,
        ),
        BoolInput(
            name="log_flow_end",
            display_name="Log Flow End",
            info="Loguear cuando el flow termina",
            value=True,
        ),
        BoolInput(
            name="capture_metrics",
            display_name="Capture Metrics",
            info="Capturar métricas de ejecución",
            value=True,
        ),
    ]

    outputs = [
        Output(
            name="monitor_output",
            display_name="Monitor Output",
            method="monitor_flow",
        ),
    ]

    async def monitor_flow(self) -> Data:
        """
        Monitorea el flow y captura eventos.
        """
        if self.log_flow_start:
            start_log = {
                "event": "FLOW_START",
                "timestamp": datetime.now().isoformat(),
                "flow_id": self._vertex.graph.flow_id if self._vertex and self._vertex.graph else None,
            }
            self.log(message=start_log, name="FLOW_START")

        # Capturar métricas si está habilitado
        metrics = {}
        if self.capture_metrics:
            metrics = {
                "total_logs": len(self._logs),
                "component_id": self._id,
                "execution_time": datetime.now().isoformat(),
            }
            self.log(message={"event": "METRICS", **metrics}, name="FLOW_METRICS")

        if self.log_flow_end:
            end_log = {
                "event": "FLOW_END",
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
            }
            self.log(message=end_log, name="FLOW_END")

        return Data(
            data={
                "status": "monitoring_complete",
                "metrics": metrics,
                "total_logs": len(self._logs),
            }
        )


class CustomEventLogger(Component):
    """
    Logger personalizado para eventos específicos con formato custom.
    """

    display_name = "Custom Event Logger"
    description = "Logger personalizado para eventos específicos con formato JSON"
    icon = "FileText"
    name = "CustomEventLogger"

    inputs = [
        MessageTextInput(
            name="event_name",
            display_name="Event Name",
            info="Nombre del evento",
            required=True,
        ),
        MessageTextInput(
            name="event_data",
            display_name="Event Data",
            info="Datos del evento (JSON string o texto)",
            required=False,
        ),
        StrInput(
            name="event_category",
            display_name="Event Category",
            info="Categoría del evento (ej: user_action, system, error)",
            value="custom",
        ),
        BoolInput(
            name="stream_to_frontend",
            display_name="Stream to Frontend",
            info="Enviar evento vía SSE al frontend",
            value=True,
        ),
    ]

    outputs = [
        Output(
            name="logged_event",
            display_name="Logged Event",
            method="log_custom_event",
        ),
    ]

    async def log_custom_event(self) -> Data:
        """
        Loguea un evento personalizado.
        """
        # Parsear event_data si es JSON
        parsed_data = self._parse_event_data()

        # Construir evento
        event = {
            "event_name": self.event_name,
            "category": self.event_category,
            "data": parsed_data,
            "timestamp": datetime.now().isoformat(),
            "component_id": self._id,
        }

        # Loguear (se envía automáticamente vía SSE)
        self.log(message=event, name=f"CUSTOM_EVENT_{self.event_name}")

        # Si queremos enviar también como mensaje
        if self.stream_to_frontend:
            message = Message(
                text=f"Event: {self.event_name}",
                sender="CustomEventLogger",
            )
            await self.send_message(message)

        return Data(data=event)

    def _parse_event_data(self) -> Any:
        """Intenta parsear event_data como JSON, si falla retorna como string."""
        if not self.event_data:
            return None

        try:
            return json.loads(self.event_data)
        except (json.JSONDecodeError, TypeError):
            return self.event_data
