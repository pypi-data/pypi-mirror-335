from enum import Enum
from typing import Optional, Dict, Union, List

from openmodule.models.base import ZMQMessage, OpenModuleModel


class SignalType(str, Enum):
    permanently_closed = "permanently_closed"
    shortterm_full = "shortterm_full"
    open = "open"
    present_raw = "present_raw"
    present_decision = "present_decision"
    traffic_light_green = "traffic_light_green"
    traffic_light_red = "traffic_light_red"
    area_full = "area_full"
    parkinglot_full = "parkinglot_full"
    custom = "custom"


class SignalMessage(ZMQMessage):
    signal: str
    type: Union[SignalType, str]  # union so we can add new types without updating all services using signals
    gate: Optional[str] = None
    parking_area_id: Optional[str] = None
    value: bool
    additional_data: Optional[Dict] = None


class GetSignalValueRequest(OpenModuleModel):
    signal: str


class GetSignalValueResponse(OpenModuleModel):
    value: bool
    additional_data: Optional[Dict] = None


class TriggerSignalsRequest(OpenModuleModel):
    signals: List[str]  # list of signals which current value should be sent


class TriggerSignalsResponse(OpenModuleModel):
    success: bool
