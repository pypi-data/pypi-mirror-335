
from typing import Optional
from xml.etree import ElementTree
import pydantic


class Contact(pydantic.BaseModel):
    phone: Optional[str]
    telefax: Optional[str]
    email: Optional[str]
    
    def xml(self) -> ElementTree.Element:
        parent = ElementTree.Element("cac:Contact")
        if self.phone:
            ElementTree.SubElement(parent, "cbc:Telephone").text = self.phone
        if self.telefax:
            ElementTree.SubElement(parent, "cbc:Telefax").text = self.telefax
        if self.email:
            ElementTree.SubElement(parent, "cbc:ElectronicMail").text = self.email
        return parent