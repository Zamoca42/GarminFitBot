from typing import Dict, List, Union

from pydantic import BaseModel


class SimpleText(BaseModel):
    text: str


class Button(BaseModel):
    action: str
    label: str
    webLinkUrl: str
    messageText: str


class TextCard(BaseModel):
    title: str
    description: str
    buttons: List[Button]


class Template(BaseModel):
    outputs: List[Dict[str, Union[SimpleText, TextCard]]]


class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: Template
