import uuid
from zeep.client import Client
from zeep.wsse.username import UsernameToken
from zeep.wsse.utils import WSU
import datetime
from QNBHelper.models import Request, Response, Return
from utils import edm_action_date

class QNBEarsivHelper:
    WSDL_URL: str = "https://earsivconnector.efinans.com.tr/earsiv/ws/EarsivWebService?wsdl"
    
    @classmethod
    def create_username_token(cls, username: str, password: str) -> UsernameToken:
        timestamp_token = WSU.Timestamp()
        today_datetime = datetime.datetime.today()
        expires_datetime = today_datetime + datetime.timedelta(minutes=10)
        timestamp_elements = [
        WSU.Created(today_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")),
        WSU.Expires(expires_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"))]
        timestamp_token.extend(timestamp_elements)
        username_token = UsernameToken(username, password, timestamp_token=timestamp_token)
        return username_token
    
    @classmethod
    def create_client(cls, username_token: UsernameToken) -> Client:
        if not isinstance(username_token, UsernameToken):
            raise TypeError("username_token must be a UsernameToken object")
        client = Client(cls.WSDL_URL, wsse=username_token)
        return client
    
    @classmethod
    def fatura_olustur(cls, client: Client, request: Request) -> Response:
        if not isinstance(client, Client):
            raise TypeError("client must be a Client Object")
        
        if not isinstance(request, Request):
            raise TypeError("request must be a Request Object")
        
        node = client.service.faturaOlustur(input=request.input_str, fatura={"belgeFormati":request.belgeFormati, "belgeIcerigi":request.belgeIcerigi})
        output = node.output
        return_ = node["return"]
        return Response(
            output=output,
            return_=Return(
                resultCode=return_.resultCode, resultExtra=None,
                resultText=return_.resultText
            )
        )
    
        



class EDMEArsivHelper:
    WSDL_URL = "https://test.edmbilisim.com.tr/EFaturaEDM21ea/EFaturaEDM.svc?singleWsdl"
    
    
    def __init__(self) -> None:
        self.headers = self.get_request_header()
        
    @staticmethod
    def get_request_header():
        return {
                "SESSION_ID": "",
                "CLIENT_TXN_ID": str(uuid.uuid4()).upper(),
                "ACTION_DATE": edm_action_date(datetime.datetime.now()),
                "REASON": "EFATURA UYGULAMA",
                "APPLICATION_NAME": "Netesnaf",
                "HOSTNAME": "netesnaf.com.tr",
                "CHANNEL_NAME": "HTTP",
                "SIMULATION_FLAG": "N",
                "COMPRESSED": "N"
        }
    
    
    def login(self, username: str, password: str):
        client = Client(self.WSDL_URL)
        client.service.Login([
            {
                "USER_NAME": username,
                "PASSWORD": password,
                **self.headers
            }
        ])
        
EDMEArsivHelper().login("31534346920", "3120")



