
from typing import Optional
from xml.etree import ElementTree
from pydantic import BaseModel
import math

class LegalMonetaryTotal(BaseModel):
    toplam_mal_hizmet_tutari: float
    vergiler_haric_toplam_tutar: float
    vergiler_dahil_toplam_tutar: float
    odenecek_toplam_tutar: float
    toplam_iskonto: Optional[float]
    toplam_artirim: Optional[float]
    yuvarlama_tutari: Optional[float]
    para_birimi: str = "TRY"
    
    
    def format_float_to_two_decimal(self, data: float):
        return math.floor(data * 100) / 100
    
    def xml(self):
        attrib = {"currencyID":self.para_birimi}
        parent = ElementTree.Element("cac:LegalMonetaryTotal")
        ElementTree.SubElement(parent, "cbc:LineExtensionAmount", attrib).text = str(self.format_float_to_two_decimal(self.toplam_mal_hizmet_tutari))
        ElementTree.SubElement(parent, "cbc:TaxExclusiveAmount", attrib).text = str(self.format_float_to_two_decimal(self.vergiler_haric_toplam_tutar))
        ElementTree.SubElement(parent, "cbc:TaxInclusiveAmount", attrib).text = str(self.format_float_to_two_decimal(self.vergiler_dahil_toplam_tutar))
        ElementTree.SubElement(parent, "cbc:PayableAmount", attrib).text = str(self.format_float_to_two_decimal(self.odenecek_toplam_tutar))
        
        if self.toplam_iskonto:
            ElementTree.SubElement(parent, "cbc:AllowanceTotalAmount", attrib).text = str(self.format_float_to_two_decimal(self.toplam_iskonto))
        if self.toplam_artirim:
            ElementTree.SubElement(parent, "cbc:ChargeTotalAmount", attrib).text = str(self.format_float_to_two_decimal(self.toplam_artirim))
        if self.yuvarlama_tutari:
            ElementTree.SubElement(parent, "cbc:PayableRoundingAmount", attrib).text = str(self.format_float_to_two_decimal(self.yuvarlama_tutari))
            
        return parent
    