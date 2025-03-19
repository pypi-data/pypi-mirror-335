from enum import Enum
import math
from typing import Optional
from xml.etree import ElementTree
import pydantic
from QNBHelper.models.Tax import TaxTotal

class LineUnitCode(Enum):
    ADET: str = "NIU"


class AllowanceCharge(pydantic.BaseModel):
    ChargeIndicator: bool = False
    MultiplierFactorNumeric: float = 1
    Amount: float = 0
    BaseAmount: float = 0
    Currency: str = "TRY"
    
    def xml(self):
        parent = ElementTree.Element("cac:AllowanceCharge")
        ElementTree.SubElement(parent, "cbc:ChargeIndicator").text = str(self.ChargeIndicator).lower()
        ElementTree.SubElement(parent, "cbc:MultiplierFactorNumeric").text = str(self.MultiplierFactorNumeric / 100)
        ElementTree.SubElement(parent, "cbc:Amount", attrib={"currencyID": self.Currency}).text = str(self.Amount)
        ElementTree.SubElement(parent, "cbc:BaseAmount", attrib={"currencyID": self.Currency}).text = str(self.BaseAmount)
        return parent
    
class InvoiceLine(pydantic.BaseModel):
    sira_no: str
    hizmet_adi: str
    miktar_turu: LineUnitCode
    
    miktar: float
    birim_fiyat: float
    tax_total: Optional[TaxTotal] = None
    para_birimi: str = "TRY"
    
    iskonto_orani: float = 0
    iskonto_tutari: float = 0
    
    
    @property
    def mal_hizmet_tutari(self) -> float:
        return self.miktar * self.birim_fiyat
    
    
    @property
    def toplam_iskonto_tutari(self):
        if self.iskonto_orani > 0:
            return self.mal_hizmet_tutari * (self.iskonto_orani / 100)
        return self.iskonto_tutari
    
    @property
    def mal_hizmet_tutari_iskontolu(self) -> float:
        if self.iskonto_orani > 0:
            return math.floor((self.mal_hizmet_tutari - (self.mal_hizmet_tutari * (self.iskonto_orani / 100))) * 100) / 100
        else:
            return math.floor((self.mal_hizmet_tutari - self.iskonto_tutari) * 100) / 100
    
    def create_allowance_charge(self) -> AllowanceCharge:
        if self.iskonto_orani > 0:
            return AllowanceCharge(
                ChargeIndicator=False,
                MultiplierFactorNumeric=self.iskonto_orani,
                Amount=self.mal_hizmet_tutari * (self.iskonto_orani / 100),
                BaseAmount=self.mal_hizmet_tutari
            ).xml()
        elif self.iskonto_tutari > 0:
            return AllowanceCharge(
                ChargeIndicator=False,
                MultiplierFactorNumeric=1,
                Amount=self.iskonto_tutari,
                BaseAmount=self.mal_hizmet_tutari
            ).xml()
        else:
            return AllowanceCharge(
                ChargeIndicator=False,
                MultiplierFactorNumeric=0,
                Amount=0,
                BaseAmount=self.mal_hizmet_tutari
            ).xml()
    
    def xml(self) -> ElementTree.Element:
        parent = ElementTree.Element("cac:InvoiceLine")
        ElementTree.SubElement(parent, "cbc:ID").text = self.sira_no
        ElementTree.SubElement(parent, "cbc:InvoicedQuantity", attrib={"unitCode": self.miktar_turu.value}).text = str(self.miktar)
        ElementTree.SubElement(parent, "cbc:LineExtensionAmount", attrib={"currencyID": self.para_birimi}).text = str(self.mal_hizmet_tutari_iskontolu)
        parent.append(self.tax_total.xml())
        
        item_element = ElementTree.SubElement(parent, "cac:Item")
        ElementTree.SubElement(item_element, "cbc:Name").text = self.hizmet_adi
        
        price_element = ElementTree.SubElement(parent, "cac:Price")
        ElementTree.SubElement(price_element, "cbc:PriceAmount", attrib={"currencyID":self.para_birimi}).text = str(self.birim_fiyat)
        allowance_charge = self.create_allowance_charge()
        if allowance_charge is not None:
            parent.append(allowance_charge)
        return parent
    
    """def xml(self):
        with open("./xml_templates/invoice_line.xml") as f:
            template = f.read()
        new_xml_string = replace_all(
            template,
            {
                "__SIRA_NO__": self.sira_no,
                "__MIKTAR_TURU__": self.miktar_turu,
                "__MIKTAR__": self.miktar,
                "__PARA_BIRIMI__": self.para_birimi,
                "__MAL_HIZMET_TUTARI__": self.mal_hizmet_tutari,
                "__HIZMET_ADI__": self.hizmet_adi,
                "__BIRIM__FIYAT__": self.birim_fiyat
            }
        )
        return new_xml_string"""