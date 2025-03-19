from typing import Optional
from pydantic import BaseModel

class Return(BaseModel):
    resultCode: str
    resultExtra: Optional[dict]
    resultText: str

class Response(BaseModel):
    output: Optional[str]
    return_: Return 
    