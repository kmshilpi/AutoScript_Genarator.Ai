from pydantic import BaseModel
from typing import Optional, List

class Step(BaseModel):
    action: str
    value: Optional[str] = None
    selector: Optional[str] = None
    selector_type: Optional[str] = "css"
    element_id: Optional[str] = None
    element_name: Optional[str] = None
    data_testid: Optional[str] = None
    tag_name: Optional[str] = None
    placeholder: Optional[str] = None
    inner_text: Optional[str] = None
    timestamp: float

class ActionRequest(BaseModel):
    selector: str
    value: Optional[str] = None
    selector_type: Optional[str] = "css"
    element_id: Optional[str] = None
    element_name: Optional[str] = None
    data_testid: Optional[str] = None
    tag_name: Optional[str] = None
    placeholder: Optional[str] = None
    inner_text: Optional[str] = None

class RecordRequest(BaseModel):
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    selector_type: Optional[str] = "css"
    element_id: Optional[str] = None
    element_name: Optional[str] = None
    data_testid: Optional[str] = None
    tag_name: Optional[str] = None
    placeholder: Optional[str] = None
    inner_text: Optional[str] = None

class NavigationRequest(BaseModel):
    url: str
