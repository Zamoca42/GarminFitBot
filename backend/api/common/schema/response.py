from typing import Any, Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    message: str
    data: Optional[Any] = None
