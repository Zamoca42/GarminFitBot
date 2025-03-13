from typing import List, Optional

from pydantic import BaseModel


class SimpleText(BaseModel):
    text: str


class Button(BaseModel):
    action: str
    label: str
    webLinkUrl: str


class TextCard(BaseModel):
    title: str
    description: str
    buttons: List[Button]


class Output(BaseModel):
    simpleText: Optional[SimpleText] = None
    textCard: Optional[TextCard] = None


class Template(BaseModel):
    outputs: List[Output]


class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: Template
