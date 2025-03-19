from enum import Enum
from typing import Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import pydantic
from QNBHelper.models.Address import Address
from QNBHelper.models.Contact import Contact


class AccountingType(Enum):
    Supplier: str = "Supplier"
    Customer: str = "Customer"

class Accounting(pydantic.BaseModel):
    address: Address
    contact: Contact
    type: AccountingType
    vkn: Optional[str]
    tckn: Optional[str]
    vergi_dairesi: Optional[str]
    firma_adi: Optional[str]
    ad: Optional[str]
    soyad: Optional[str]
    
    
    @pydantic.model_validator(mode="before")
    def check_valid_tckn_or_vkn(cls, data):
        
        if data["vkn"] is None and data["tckn"] is None:
            raise ValueError("Bir VKN Veya TCKN Girmelisiniz!")
        
        elif data["vkn"] is not None and data["tckn"] is not None:
            raise ValueError("VKN Ve TCKN Aynı Anda Girilemez!")
        
        if data["vkn"] is not None:
            if data["firma_adi"] == None or data["vergi_dairesi"] == None:
                raise ValueError("VKN Girildiğinde Firma Adı Boş Bırakılamaz!")
        
        if data["tckn"] is not None and (data["ad"] is None or data["soyad"] is None):
            raise ValueError("TCKN Girildiğinde Satici Adi Ve Soy Adı Boş Bırakılamaz!")
        
        elif data["tckn"] is None and (data["ad"] is not None or data["soyad"] is not None):
            raise ValueError("Satıcı Adı Veya Soy Adı Girildiğinde TCKN Boş Bırakılamaz")
        return data
    
    
    @property
    def identification_type(self):
        if self.vkn is not None:
            return "VKN"
        return "TCKN"
    
    @property
    def identification_val(self):
        return self.vkn or self.tckn

    @property
    def party_identification_element(self) -> Element:
        

        parent = ElementTree.Element("cac:PartyIdentification")
        id_element = ElementTree.SubElement(parent, "cbc:ID", {"schemeID":self.identification_type})
        id_element.text = self.identification_val
        return parent
    
    def xml(self) -> ElementTree.Element:
        if self.type == AccountingType.Supplier:
            
            parent = ElementTree.Element("cac:AccountingSupplierParty")
        elif self.type == AccountingType.Customer:
            parent = ElementTree.Element("cac:AccountingCustomerParty")
            
        party_element = ElementTree.Element("cac:Party")
        party_element.append(self.party_identification_element)
        
        party_tax_scheme = ElementTree.SubElement(party_element, "cac:PartyTaxScheme")
        tax_scheme = ElementTree.SubElement(party_tax_scheme, "cac:TaxScheme")
        if self.firma_adi is not None:
            party_name = ElementTree.SubElement(party_element, "cac:PartyName")

            ElementTree.SubElement(party_name, "cbc:Name").text = self.firma_adi
        if self.vergi_dairesi is not None:
            
            ElementTree.SubElement(tax_scheme, "cbc:Name").text = self.vergi_dairesi
            
        if self.identification_type == "TCKN":
            person_element = ElementTree.SubElement(party_element, "cac:Person")
            ElementTree.SubElement(person_element, "cbc:FirstName").text = self.ad
            ElementTree.SubElement(person_element, "cbc:FamilyName").text = self.soyad
            
        party_element.append(self.address.xml())
        party_element.append(self.contact.xml())
        parent.append(party_element)
        return parent
    """
        
    def xml(self):
        identification_type, identification_val = self.get_identification_type_and_val
            
        _xml = self.__xml_template.format(
            vkn_or_tckn=identification_type,
            vkn_or_tckn_value=identification_val,
            vergi_dairesi=self.vergi_dairesi,
            firma_adi=self.firma_adi or "",
            street_name=self.address.street_name,
            building_number=self.address.building_number,
            city_subdivision_name=self.address.city_subdivision_name,
            city_name=self.address.city_name,
            postal_zone=self.address.postal_zone,
            country=self.address.country,
            phone=self.contact.phone,
            fax=self.contact.telefax
        )
        
        with open("./xml_templates/accounting_supplier.xml") as f:
            template = f.read()
        replaced_template = replace_all(
            template,
            {
                "__VKN__": self.vkn,
                "__VERGI_DAIRESI__": self.vergi_dairesi,
                "__FIRMA_ADI__": self.firma_adi,
                "__STREET_NAME__": self.address.street_name,
                "__BUILDING_NUMBER__": self.address.building_number,
                "__CITY_SUBDIVISION_NAME__": self.address.city_subdivision_name,
                "__CITY_NAME__": self.address.city_name,
                "__POSTAL_ZONE__": self.address.postal_zone,
                "__COUNTRY__": self.address.country,
                "__PHONE__": self.contact.phone,
                "__FAX__": self.contact.telefax
            }
        )
        return _xml
"""