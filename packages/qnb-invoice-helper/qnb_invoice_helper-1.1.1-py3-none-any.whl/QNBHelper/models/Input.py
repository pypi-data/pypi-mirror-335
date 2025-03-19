import json
import uuid
import pydantic


class Input(pydantic.BaseModel):
    vkn: str
    sube: str
    kasa: str
    erpKodu: str
    islemId: str = str(uuid.uuid4())
    donenBelgeFormati: str = "9"
    
    def json(self) -> str:
        dict_ = self.dict()
        return json.dumps(dict_, ensure_ascii=False)