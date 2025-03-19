from xml.dom.minidom import Element
from xml.etree import ElementTree
import pydantic


class Address(pydantic.BaseModel):
    street_name: str
    building_number: str
    city_subdivision_name: str
    city_name: str
    postal_zone: str
    country: str
    
    def xml(self) -> Element:
        parent = ElementTree.Element("cac:PostalAddress")
        ElementTree.SubElement(parent, "cbc:StreetName").text = self.street_name
        ElementTree.SubElement(parent, "cbc:BuildingNumber").text = self.building_number
        ElementTree.SubElement(parent, "cbc:CitySubdivisionName").text = self.city_subdivision_name
        ElementTree.SubElement(parent, "cbc:CityName").text = self.city_name
        ElementTree.SubElement(parent, "cbc:PostalZone").text = self.postal_zone
        country = ElementTree.SubElement(parent, "cac:Country")
        ElementTree.SubElement(country, "cbc:Name").text = self.country
        return parent

    