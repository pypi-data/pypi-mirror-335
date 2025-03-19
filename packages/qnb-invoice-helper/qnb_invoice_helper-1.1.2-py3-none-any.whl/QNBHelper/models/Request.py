import json
from xml.etree import ElementTree
import pydantic
from QNBHelper.models.Invoice import Invoice
from QNBHelper.models.Input import Input

class Request(pydantic.BaseModel):
    input: Input
    invoice: Invoice
    
    @property
    def input_str(self) -> str:
        return json.dumps(self.input.dict())
    
    @property
    def belgeIcerigi(self) -> str:
        return ElementTree.tostring(self.invoice.xml())
    
    @property
    def belgeFormati(self) -> str:
        return self.invoice._belgeFormati