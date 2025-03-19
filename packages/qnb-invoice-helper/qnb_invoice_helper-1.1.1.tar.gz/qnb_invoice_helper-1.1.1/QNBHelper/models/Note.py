from xml.etree import ElementTree
import pydantic

class Note(pydantic.BaseModel):
    msg: str
    
    def xml(self) -> ElementTree.Element:
        el = ElementTree.Element("cbc:Note")
        el.text = self.msg
        return el 