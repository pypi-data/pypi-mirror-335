
# type: ignore
from ast import Dict
from calendar import c
from typing import Any
from .schema import  IConfigProtocollo, IProtocolloResult, IDataProtocollo
import base64
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
import httpx
from bs4 import BeautifulSoup
import base64
import logging
import xmltodict

_logger = logging.getLogger('gisweb-iride')

env = Environment(
    loader=PackageLoader("gisweb_iride"),
    autoescape=select_autoescape()
)

class Protocollo:
    
    config: IConfigProtocollo
    
    def __init__(self, config:IConfigProtocollo):
        self.config = config
        
 
    def protocollaDocumento(self, data:IDataProtocollo, testXml:bool=True) -> str | IProtocolloResult:
        template = env.get_template("protoIn.xml")
        
        allAllegati = [data.Principale] + data.Allegati
        for all in allAllegati:
            all.content=base64.b64encode(all.content).decode("utf-8")
        
        context = data.model_copy(update=dict(
            Allegati = allAllegati,
            Today = datetime.today().strftime('%d/%m/%Y'),
            totAllegati = len(allAllegati),
        ))
                
        protoIn =  template.render(context)
        if testXml:
            return protoIn

        result = self.serviceCall(Operazione="InserisciProtocolloEAnagraficheString",xml=protoIn)
        #result = {'ProtocolloOut': {'IdDocumento': '2252594', 'AnnoProtocollo': '2024', 'NumeroProtocollo': '105588', 'DataProtocollo': '2024-07-25T10:30:42.337+0200', 'Messaggio': 'Inserimento Protocollo eseguito con successo, senza Avvio Iter', 'Errore': None, 'Allegati': {'Allegato': {'Serial': '4097726', 'IDBase': '4097726', 'Versione': '0'}}}}
        
        if result.get('ProtocolloOut'):
            ret = result.get('ProtocolloOut')
            if ret.get('NumeroProtocollo'):
                return IProtocolloResult(lngNumPG=int(ret.get('NumeroProtocollo')), lngAnnoPG=int(ret.get('AnnoProtocollo')), lngDocID=int(ret.get('IdDocumento')))
            else:
                return IProtocolloResult(strErrString="Manca numero protocollo nella risposta", lngErrNumber=9999)
        else:
            return IProtocolloResult(strErrString=result.get("errore"), lngErrNumber=999)

  
    def serviceCall(self, Operazione:str, xml:str):
        """
        chiamata base al servizio SOAP JPPA
        """

        config = self.config
        data_richiesta =  datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 

        template = env.get_template("serviceCall.xml")
        xml = template.render(
            operazione = Operazione,
            content=xml, 
            codice_amministrazione = self.config.amministrazione.CodiceEnte, 
            codice_aoo = self.config.amministrazione.CodiceAOO,
            data = data_richiesta, 
        )
        
        headers={'Content-type': 'text/plain; charset=utf-8', 'SOAPAction': Operazione}
        
        with httpx.Client() as client:         
            url = f"{config.wsUrl}&CID={config.wsUser}"
            response = client.post(url, content=xml, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'xml')
            
            if soup.find(f"{Operazione}Response") and soup.find(f"{Operazione}Result"):
                try:
                    return xmltodict.parse(soup.find(f"{Operazione}Result").string)
                except:
                    with open("./error_resp.xml", "a") as f:
                        f.write(response.text)
            
            elif soup.find("faultstring"):
                return {"errore":soup.find("faultstring").string}

            else:
                with open("./error_resp.xml", "a") as f:
                    f.write(response.text)
   
        return {"errore":"ERRORE NON GESTITO"}
    
    
    def inviaComunicazione(self, protocollo_id: int, testXml:bool=True) -> str | IProtocolloResult:
        pass
    























    def provaResponse(self):
        resp = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soapenv:Body>
        <InserisciProtocolloEAnagraficheStringResponse xmlns="http://tempuri.org/">
            <InserisciProtocolloEAnagraficheStringResult><![CDATA[<ProtoOut>
    <idDocumento>151</idDocumento>
    <annoProtocollo>2013</annoProtocollo>
    <numeroProtocollo>609</numeroProtocollo>
    <dataProtocollo>11/12/2013</dataProtocollo>
    <messaggio/>
    <Registri>
        <Registro>
            <TipoRegistro>LETTERA</TipoRegistro>
            <AnnoRegistro>2016</AnnoRegistro>
            <NumeroRegistro>583</NumeroRegistro>
        </Registro>
    </Registri>
    <errore/>
    <Allegati>
        <Allegato>
            <Serial>11958</Serial>
            <IDBase>11958</IDBase>
            <Versione>0</Versione>
        </Allegato>
        <Allegato>
            <Serial>11959</Serial>
            <IDBase>11959</IDBase>
            <Versione>0</Versione>
        </Allegato>
    </Allegati>
</ProtoOut>]]></InserisciProtocolloEAnagraficheStringResult>
        </InserisciProtocolloEAnagraficheStringResponse>
    </soapenv:Body>
</soapenv:Envelope>
        '''
        import pdb;pdb.set_trace()
        soup = BeautifulSoup(resp, 'xml')
        if soup.find('faultstring'):
            return 'sssssssssss'
        
        if soup.find('InserisciProtocolloEAnagraficheStringResponse') and soup.find('InserisciProtocolloEAnagraficheStringResult'):
            xml = soup.find('InserisciProtocolloEAnagraficheStringResult').string
            
            soup2 = BeautifulSoup(xml, 'xml')
            print(xmltodict.parse(xml))            
        

        
         
  




