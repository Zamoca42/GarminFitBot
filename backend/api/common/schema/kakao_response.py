from typing import Dict, List, Union

from pydantic import BaseModel


class SimpleText(BaseModel):
    text: str


class WebLinkButton(BaseModel):
    action: str = "webLink"
    label: str
    webLinkUrl: str


class MessageButton(BaseModel):
    action: str = "message"
    label: str
    messageText: str


class BlockButton(BaseModel):
    action: str = "block"
    label: str
    blockId: str


# 모든 버튼 타입의 통합 타입 힌트
ButtonType = Union[WebLinkButton, MessageButton, BlockButton]


class TextCard(BaseModel):
    title: str
    description: str
    buttons: List[ButtonType]


class Template(BaseModel):
    outputs: List[Dict[str, Union[SimpleText, TextCard]]]


class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: Template
