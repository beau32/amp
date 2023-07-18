import datetime, re



def AddObjectArrayItem():
    pass
def CreateObject():
    pass
def InvokeCreate():
    pass
def InvokeDelete():
    pass
def InvokeExecute():
    pass
def InvokePerform():
    pass
def InvokeRetrieve():
    pass
def InvokeUpdate():
    pass
def RaiseError():
    pass
def SetObjectProperty():
    pass
def Contacts():
    pass
def UpsertContact():
    pass
def Content():
    pass
def AttachFile():
    pass
def BarCodeURL():
    pass
def BeginImpressionRegion():
    pass
def BuildOptionList():
    pass
def BuildRowSetFromString():
    pass
def BuildRowSetFromXML():
    pass
def ContentArea():
    pass
def ContentAreaByName():
    pass
def ContentBlockbyId():
    pass
def ContentBlockbyKey():
    pass
def ContentBlockbyName():
    pass
def ContentImagebyID():
    pass
def ContentImagebyKey():
    pass
def CreateSmsConversation():
    pass
def EndImpressionRegion():
    pass
def EndSmsConversation():
    pass
def GetPortfolioItem():
    pass
def _messageContext():
    pass
def SetSmsConversationNextKeyword():
    pass
def TransformXML():
    pass
def TreatAsContent():
    pass
def TreatAsContentArea():
    pass
def WAT():
    pass
def WATP():
    pass
def ClaimRow():
    pass
def ClaimRowValue():
    pass
def DataExtensionRowCount():
    pass
def DeleteData():
    pass
def DeleteDE():
    pass
def ExecuteFilter():
    pass
def ExecuteFilterOrderedRows():
    pass
def Field():
    pass
def InsertData():
    pass
def InsertDE():
    pass
def Lookup():
    pass
def LookupOrderedRows():
    pass
def LookupOrderedRowsCS():
    pass
def LookupRows():
    pass
def LookupRowsCS():
    pass
def Row():
    pass
def RowCount():
    pass
def UpdateData():
    pass
def UpdateDE():
    pass
def UpsertData():
    pass
def UpsertDE():
    pass
def DateAdd():
    pass
def DateDiff():
    pass
def DateParse():
    pass
def DatePart():
    pass
def GetSendTime():
    pass
def LocalDateToSystemDate():
    pass
def Now():
    return datetime.datetime.now()
def SystemDateToLocalDate():
    pass
def Encryption():
    pass
def Base64Decode():
    pass
def Base64Encode():
    pass
def DecryptSymmetric():
    pass
def EncryptSymmetric():
    pass
def GUID():
    pass
def MD5():
    pass
def SHA1():
    pass
def SHA256():
    pass
def HTTP():
    pass
def HTTPGet():
    pass
def HTTPPost():
    pass
def HTTPPost2():
    pass
def HTTPRequestHeader():
    pass
def IsCHTMLBrowser():
    pass
def RedirectTo():
    pass
def URLEncode():
    pass
def WrapLongURL():
    pass
def Math():
    pass
def Add():
    pass
def Divide():
    pass
def FormatCurrency():
    pass
def FormatNumber():
    pass
def Mod():
    pass
def Multiply():
    pass
def Random():
    pass
def Subtract():
    pass
def AddMscrmListMember():
    pass
def CreateMscrmRecord():
    pass
def DescribeMscrmEntities():
    pass
def DescribeMscrmEntityAttributes():
    pass
def RetrieveMscrmRecords():
    pass
def RetrieveMscrmRecordsFetchXML():
    pass
def SetStateMscrmRecord():
    pass
def UpdateMscrmRecords():
    pass
def UpsertMscrmRecord():
    pass
def CreateSalesforceObject():
    pass
def LongSFID():
    pass
def RetrieveSalesforceJobSources():
    pass
def RetrieveSalesforceObjects():
    pass
def UpdateSingleSalesforceObject():
    pass
def AuthenticatedEmployeeID():
    pass
def AuthenticatedEmployeeNotificationAddress():
    pass
def AuthenticatedEmployeeUserName():
    pass
def AuthenticatedEnterpriseID():
    pass
def AuthenticatedMemberID():
    pass
def AuthenticatedMemberName():
    pass
def CloudPagesURL():
    pass
def IsNullDefault():
    pass
def LiveContentMicrositeURL():
    pass
def MicrositeURL():
    pass
def QueryParameter():
    pass
def Redirect():
    pass
def RequestParameter():
    pass
def Social():
    pass
def GetPublishedSocialContent():
    pass
def GetSocialPublishURL():
    pass
def GetSocialPublishURLByName():
    pass
def String(self,e):
    return str(self,e)
def Char(self,e):
    return chr(self,e)
def Concat(a,b):
    return a+b
def Format(a,b,c,d):
    pass
def IndexOf(var, search):
    return var.find(search)
def Length(self,e):
    return len(self,e)
def Lowercase(self,e) -> str:
    return e.lower()
def ProperCase():
    pass
def RegExMatch(str, regex):
    return re.search(regex, str)
def Replace(str, r,e):
    return str.replace(r,e)
def ReplaceList():
    pass
def StringToDate(self,e):
    return e.strptime()
def StringToHex(value):
    convert_string = int(value, base=16)
    convert_hex = hex(convert_string)
    return convert_hex, convert_string
def Substring():
    pass
def Trim(self,e) -> str:
    return e.strip()
def Uppercase(self,e) -> str:
    return e.upper()
def AttributeValue():
    pass
def Domain():
    pass
def Empty(self,e):
    return True if len(self,e)>0 else False
def IsEmailAddress(self,e):
    return True if re.search('^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$',e) else False
def IsNull(self,e):
    return True if e==None else False
def IsPhoneNumber(self,e):
    return True if re.search('^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',e) else False
def Output(self,e)  -> str:
    print(e)        
def OutputLine(self,e) -> str:
    print(e+"\n")
def V(self, e) -> str:
    print(e)