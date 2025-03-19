import math
from xml.etree import ElementTree
from pydantic import BaseModel
from typing import List, Optional

class TaxScheme(BaseModel):
    name: str
    vergi_turu_kodu: str

    def xml(self) -> ElementTree.Element:
        parent = ElementTree.Element("cac:TaxScheme")
        ElementTree.SubElement(parent, "cbc:Name").text = self.name
        ElementTree.SubElement(parent, "cbc:TaxTypeCode").text = self.vergi_turu_kodu
        return parent
    
class TaxCategory(BaseModel):
    vergi_adi: str
    vergi_muafiyet_kodu: Optional[str]
    vergi_muafiyet_sebebi: Optional[str] 
    vergi_turu_bilgileri: TaxScheme

    def xml(self) -> ElementTree.Element:
        parent = ElementTree.Element("cac:TaxCategory")
        ElementTree.SubElement(parent, "cbc:Name").text = self.vergi_adi
        if self.vergi_muafiyet_kodu:
            
            ElementTree.SubElement(parent, "cbc:TaxExemptionReasonCode").text = self.vergi_muafiyet_kodu
        if self.vergi_muafiyet_sebebi:
            
            ElementTree.SubElement(parent, "cbc:TaxExemptionReason").text = self.vergi_muafiyet_sebebi
        parent.append(self.vergi_turu_bilgileri.xml())
        return parent
    
    
class TaxSubTotal(BaseModel):
    matrah: float
    vergi_sira_numarasi: Optional[int]
    vergi_orani: Optional[int]
    vergi_turu: TaxCategory
    para_birimi: str = "TRY"
    
    @property
    def hesaplanan_tutar(self):
        tax_amount = self.matrah * (self.vergi_orani / 100)
        return math.floor( tax_amount * 100) / 100   
    
    def xml(self):
        parent = ElementTree.Element("cac:TaxSubtotal")
        ElementTree.SubElement(parent, "cbc:TaxableAmount", attrib={"currencyID":self.para_birimi}).text = str(self.matrah)
        ElementTree.SubElement(parent, "cbc:TaxAmount", attrib={"currencyID":self.para_birimi}).text = str(self.hesaplanan_tutar)
        if self.vergi_sira_numarasi is not None:
            ElementTree.SubElement(parent, "cbc:CalculationSequenceNumeric").text = str(self.vergi_sira_numarasi)
        if self.vergi_orani is not None:
            ElementTree.SubElement(parent, "cbc:Percent").text = str(self.vergi_orani)
        parent.append(self.vergi_turu.xml())
        return parent
        
class TaxTotal(BaseModel):
    vergi_miktari: float
    vergiler: List[TaxSubTotal] = []
    para_birimi: str = "TRY"
    
    @property
    def format_vergi_miktari(self):
        return math.floor(self.vergi_miktari * 100) / 100
    
    def xml(self) -> ElementTree.Element:
        parent = ElementTree.Element("cac:TaxTotal")
        ElementTree.SubElement(parent, "cbc:TaxAmount", attrib={"currencyID":self.para_birimi}).text = str(self.format_vergi_miktari)
        for vergi in self.vergiler:
            parent.append(vergi.xml())
        return parent