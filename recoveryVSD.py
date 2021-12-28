# -*- coding: utf-8 -*-
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import xmltodict

jsonFile = open("settings.json", encoding="utf-8")
settingsMercury = (json.load(jsonFile))


# CREATE TRANSACTION
def createTransaction(url, headers, begin_date):
    xmlCreate = """<SOAP-ENV:Envelope xmlns:dt="http://api.vetrf.ru/schema/cdm/dictionary/v2" 
    xmlns:bs="http://api.vetrf.ru/schema/cdm/base" 
    xmlns:merc="http://api.vetrf.ru/schema/cdm/mercury/g2b/applications/v2" 
    xmlns:apldef="http://api.vetrf.ru/schema/cdm/application/ws-definitions" 
    xmlns:apl="http://api.vetrf.ru/schema/cdm/application" 
    xmlns:vd="http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2" 
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
        <SOAP-ENV:Header />
        <SOAP-ENV:Body>
        <apldef:submitApplicationRequest>
                <apldef:apiKey>""" + settingsMercury["API_KEY"] + """</apldef:apiKey>
                <apl:application>
                    <apl:serviceId>""" + settingsMercury["SERVICE_ID"] + """</apl:serviceId>
                    <apl:issuerId>""" + settingsMercury["ISSUER_ID"] + """</apl:issuerId>
                    <apl:issueDate>""" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + """</apl:issueDate>
                    <apl:data>
                        <merc:getVetDocumentListRequest>
                            <merc:localTransactionId>a""" + datetime.now().strftime("%Y%m%dT%H%M%S") + """
                            </merc:localTransactionId>
                            <merc:initiator>
                                <vd:login>""" + settingsMercury["LOGIN"] + """</vd:login>
                            </merc:initiator>
                            <bs:listOptions>
                                <bs:count>1000</bs:count>
                                <bs:offset>0</bs:offset>
                            </bs:listOptions>
                            <vd:vetDocumentType>RETURNABLE</vd:vetDocumentType>
                                <vd:issueDateInterval>
                                    <bs:beginDate>""" + begin_date + "T00:00:00" + """</bs:beginDate>
                                    <bs:endDate>""" + begin_date + "T23:59:00" + """</bs:endDate>
                                </vd:issueDateInterval>
                            <dt:enterpriseGuid>""" + settingsMercury["ENTERPRISE_GUID"] + """</dt:enterpriseGuid>
                            </merc:getVetDocumentListRequest>
                            </apl:data>
                </apl:application>
                </apldef:submitApplicationRequest>
        </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>"""
    resp = requests.post(url, headers=headers, data=xmlCreate)
    if resp.status_code == 200:
        application_id = \
            xmltodict.parse(resp.text)["soap:Envelope"]["soap:Body"]["ws:submitApplicationResponse"]["application"][
                "applicationId"]
        print(application_id)
        time.sleep(30)
        get_transaction_result(url, headers, application_id)
    else:
        print(resp.status_code)
        time.sleep(30)
        createTransaction(url, headers, begin_date)


# GET TRANSACTION RESULT
def get_transaction_result(url, headers, application_id):
    xmlGetResult = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:ws="http://api.vetrf.ru/schema/cdm/application/ws-definitions">
        <soapenv:Header/>
        <soapenv:Body>
            <ws:receiveApplicationResultRequest>
                <ws:apiKey>""" + settingsMercury["API_KEY"] + """</ws:apiKey>
                <ws:issuerId>""" + settingsMercury["ISSUER_ID"] + """</ws:issuerId>
                <ws:applicationId>""" + application_id + """</ws:applicationId >
            </ws:receiveApplicationResultRequest>
        </soapenv:Body>
    </soapenv:Envelope>"""
    resp = requests.post(url, headers=headers, data=xmlGetResult)
    statusMercury = \
        xmltodict.parse(resp.text)["soap:Envelope"]["soap:Body"]["receiveApplicationResultResponse"]["application"][
            "status"]
    if resp.status_code == 200 and statusMercury == 'COMPLETED':
        f = open("recovery.xml", "w", encoding="utf=8")
        f.write(resp.text)
        f.close()
        time.sleep(5)
        parseVetDocumentList()
    else:
        print(resp.status_code)
        print(statusMercury)
        time.sleep(60)
        get_transaction_result(url, headers, application_id)


# PARSE RESULT
def parseVetDocumentList():
    xml = r"C:\PYTHON\Servers\recovery.xml"
    context = ET.iterparse(xml, events=("end", "start"))
    jsonRecovery = {}
    jsonRecovery["recovery"] = []
    counter_vsd = 0
    for event, elem in context:
        # VET DOCUMENT MAIN INFO
        if event == "end" and elem.tag == "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}vetDocument":
            for vetDocument in elem:
                if event == "end" and vetDocument.tag == "{http://api.vetrf.ru/schema/cdm/base}uuid":
                    jsonRecovery["recovery"].append({counter_vsd: "VSD"})
                    jsonRecovery["recovery"][counter_vsd]["uuid"] = vetDocument.text
                if event == "end" and vetDocument.tag == \
                        "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}vetDStatus" and vetDocument.text == "UTILIZED":
                    jsonRecovery["recovery"][counter_vsd]["vetDStatus"] = "Погашен"
                if event == "end" and vetDocument.tag == \
                        "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}vetDStatus" and vetDocument.text == "WITHDRAWN":
                    jsonRecovery["recovery"][counter_vsd]["vetDStatus"] = "Аннулирован"
                if event == "end" and vetDocument.tag == \
                        "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}vetDStatus" and vetDocument.text == "CONFIRMED":
                    jsonRecovery["recovery"][counter_vsd]["vetDStatus"] = "Оформлен"
                    jsonRecovery["recovery"][counter_vsd]["tick"] = "true"
                if event == "end" and vetDocument.tag == \
                        "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}lastUpdateDate":
                    jsonRecovery["recovery"][counter_vsd]["dateReturn"] = vetDocument.text
                # PRODUCT INFO
                for certifiedConsignment in vetDocument:
                    for bath in certifiedConsignment:
                        if event == "end" and bath.tag == \
                                "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}volume":
                            jsonRecovery["recovery"][counter_vsd]["volume"] = float(bath.text)
                        if event == "end" and bath.tag == \
                                "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}productItem":
                            for productItem in bath:
                                if event == "end" and productItem.tag == \
                                        "{http://api.vetrf.ru/schema/cdm/dictionary/v2}code":
                                    jsonRecovery["recovery"][counter_vsd]["code_gp"] = productItem.text
                                if event == "end" and productItem.tag == \
                                        "{http://api.vetrf.ru/schema/cdm/dictionary/v2}name":
                                    jsonRecovery["recovery"][counter_vsd]["name"] = productItem.text
                                if event == "end" and productItem.tag == \
                                        "{http://api.vetrf.ru/schema/cdm/dictionary/v2}globalID":
                                    jsonRecovery["recovery"][counter_vsd]["gtin"] = productItem.text
                # NUMBER TTN
                for referencedDocument in vetDocument:
                    if event == "end" and referencedDocument.tag == \
                            "{http://api.vetrf.ru/schema/cdm/mercury/vet-document/v2}issueNumber":
                        jsonRecovery["recovery"][counter_vsd]["ttn"] = referencedDocument.text
            counter_vsd += 1
    f = open("recovery.json", "w", encoding="utf=8")
    json_dump = json.dumps(jsonRecovery)
    f.write(str(json_dump))
    f.close()
    print("Recovery: ", counter_vsd)
