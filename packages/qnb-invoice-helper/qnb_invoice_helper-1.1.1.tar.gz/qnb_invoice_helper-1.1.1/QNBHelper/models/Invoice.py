import datetime
from enum import Enum
import math
from typing import List, Optional
import uuid
from xml.etree import ElementTree
import pydantic
from QNBHelper.models.Accounting import Accounting, AccountingType
from QNBHelper.models.InvoiceLine import InvoiceLine
from QNBHelper.models.Note import Note
from QNBHelper.models.Tax import TaxCategory, TaxScheme, TaxSubTotal, TaxTotal
from QNBHelper.models.LegalMonetaryTotal import LegalMonetaryTotal

class InvoiceType(Enum):
    SATIS: str = "SATIS"
    IHRAC_KAYITLI: str = "IHRACKAYITLI"
    TEVKIFAT: str = "TEVKIFAT"
    IADE: str = "IADE"
    ISTISNA: str = "ISTISNA"
    
class InvoiceSendingType(Enum):
    KAGIT: str = "KAGIT"
    ELEKTRONIK: str = "ELEKTRONIK"
    
class Invoice(pydantic.BaseModel):
    accounting_supplier: Accounting
    accounting_customer: Accounting
    legal_monetary_total: LegalMonetaryTotal
    lines: List[InvoiceLine]
    notlar: List[Note]
    para_birimi: str
    doviz_kuru: float = 0
    
    fatura_turu: InvoiceType = InvoiceType.SATIS
    gonderim_sekli: InvoiceSendingType = InvoiceSendingType.ELEKTRONIK
    
    asil_veya_suret: bool = False
    
    fatura_no: Optional[str]
    uuid4: str = str(uuid.uuid4())
    _belgeFormati: str = "UBL"
    _date_now: datetime.datetime = datetime.datetime.now()
    

    @pydantic.model_validator(mode="wrap")
    def check_valid_accounting_types(cls, data):
        if data["accounting_supplier"].type != AccountingType.Supplier:
            raise ValueError("accounting_supplier type'ı Supplier Olan Accounting Class'ı Olmak Zorunda!")
        
        if data["accounting_customer"].type != AccountingType.Customer:
            raise ValueError("accounting_customer type'ı Customer Olan Accounting Class'ı Olmak Zorunda!")
        return data
    
    @property
    def xml_namespaces(self) -> dict:
        namespaces={
            "xmlns":"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "xmlns:cac":"urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "xmlns:cbc":"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "xmlns:ccts":"urn:un:unece:uncefact:documentation:2",
            "xmlns:ds":"http://www.w3.org/2000/09/xmldsig#",
            "xmlns:ext":"urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "xmlns:qdt":"urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
            "xmlns:ubltr":"urn:oasis:names:specification:ubl:schema:xsd:TurkishCustomizationExtensionComponents", 
            "xmlns:udt":"urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
            "xmlns:xades":"http://uri.etsi.org/01903/v1.3.2#",
            "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation":"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 UBL-Invoice-2.1.xsd"
        }
        return namespaces
    
    @property
    def duzenleme_tarihi(self):
        duzenleme_tarihi = self._date_now.strftime("%Y-%m-%d")
        return duzenleme_tarihi
    
    @property
    def duzenleme_zamani(self):
        duzenleme_zamani = self._date_now.strftime("%H:%M:%S")
        return duzenleme_zamani
    

    def create_tax_total_from_invoice_lines(self) -> TaxTotal:
        taxes: dict[str, dict] = {}
        tax_amount = 0
    
        for line in self.lines:
            for tax in line.tax_total.vergiler:
                tax_key = f"{tax.vergi_turu.vergi_adi}_{tax.vergi_orani}"
                
                if tax_key not in taxes:
                    taxes[tax_key] = {
                        "matrah": 0,
                        "hesaplanan_tutar": 0,
                        "vergi_turu": tax.vergi_turu,
                        "vergi_orani": tax.vergi_orani
                    }
                    
                taxes[tax_key]["matrah"] += float(tax.matrah)
                taxes[tax_key]["hesaplanan_tutar"] += float(tax.hesaplanan_tutar)
                tax_amount += float(tax.hesaplanan_tutar)
        
        # Her bir gruplama için TaxSubTotal oluştur
        all_subtotal_taxes = [
            TaxSubTotal(
                matrah=values["matrah"],
                vergi_orani=int(values["vergi_orani"]),
                vergi_turu=TaxCategory(
                    vergi_adi=values["vergi_turu"].vergi_adi,
                    vergi_muafiyet_kodu=values["vergi_turu"].vergi_muafiyet_kodu,
                    vergi_muafiyet_sebebi=values["vergi_turu"].vergi_muafiyet_sebebi,
                    vergi_turu_bilgileri=TaxScheme(
                        name=values["vergi_turu"].vergi_adi,
                        vergi_turu_kodu=values["vergi_turu"].vergi_turu_bilgileri.vergi_turu_kodu
                    )
                ),
                para_birimi=self.para_birimi
            ) for values in taxes.values()
        ]
    
        # TaxTotal oluştur
        tax_total = TaxTotal(
            vergi_miktari=tax_amount, vergiler=all_subtotal_taxes, para_birimi=self.para_birimi
        )
        
        return tax_total

    
    def create_legal_monetary_total_from_invoice_lines(self) -> LegalMonetaryTotal:
        total_amount = (
            math.floor(
                sum([
                    line.mal_hizmet_tutari_iskontolu +
                    sum([tax.hesaplanan_tutar for tax in line.tax_total.vergiler])
                    for line in self.lines
                ] 
            * 100)) / 100
        )
        legal_monetary_total = LegalMonetaryTotal(
            toplam_mal_hizmet_tutari=sum([line.mal_hizmet_tutari_iskontolu for line in self.lines]),
            vergiler_dahil_toplam_tutar=total_amount,
            vergiler_haric_toplam_tutar=sum([line.mal_hizmet_tutari_iskontolu for line in self.lines]),
            odenecek_toplam_tutar=total_amount,
            toplam_iskonto=sum([line.toplam_iskonto_tutari for line in self.lines]),
            para_birimi=self.para_birimi
        )
        
        return legal_monetary_total
    
    def xml(self):
        namespaces = self.xml_namespaces
        root = ElementTree.Element("Invoice", attrib=namespaces)
        ElementTree.SubElement(root, "cbc:UBLVersionID").text = "2.1"
        ElementTree.SubElement(root, "cbc:CustomizationID").text = "TR1.2"
        ElementTree.SubElement(root, "cbc:ProfileID").text = "EARSIVFATURA"
        ElementTree.SubElement(root, "cbc:UUID").text = self.uuid4
        ElementTree.SubElement(root, "cbc:IssueDate").text = self.duzenleme_tarihi
        ElementTree.SubElement(root, "cbc:IssueTime").text = self.duzenleme_zamani
        ElementTree.SubElement(root, "cbc:InvoiceTypeCode").text = self.fatura_turu.value
        ElementTree.SubElement(root, "cbc:DocumentCurrencyCode").text = self.para_birimi
        
        
        if self.para_birimi != "TRY":
            if self.doviz_kuru == 0:
                raise ValueError("Döviz Kuru 0 olamaz!")
            
            root_element = ElementTree.SubElement(root, "cac:PricingExchangeRate")
            ElementTree.SubElement(root_element, "cbc:SourceCurrencyCode").text = self.para_birimi
            ElementTree.SubElement(root_element, "cbc:TargetCurrencyCode").text = "TRY"
            
            ElementTree.SubElement(root_element, "cbc:CalculationRate").text = str(self.doviz_kuru)
        
        ElementTree.SubElement(root, "cbc:LineCountNumeric").text = str(len(self.lines))
        ElementTree.SubElement(root, "cbc:Note").text = f"Gönderim Şekli: {self.gonderim_sekli.value}"
        ElementTree.SubElement(root, "cbc:CopyIndicator").text = str(self.asil_veya_suret).lower()
        ElementTree.SubElement(root, "cbc:ID").text = self.fatura_no
        for note in self.notlar:
            root.append(note.xml())
        
    
        
        root.append(self.accounting_supplier.xml())
        root.append(self.accounting_customer.xml())    
        root.append(self.create_legal_monetary_total_from_invoice_lines().xml())
        tax_total = self.create_tax_total_from_invoice_lines()
        
        root.append(tax_total.xml())
        
        for line in self.lines:
            root.append(line.xml())

        
                
                
                
        return root
