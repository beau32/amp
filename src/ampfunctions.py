# references can be found here https://ampscript.guide/

import re, json, random, urllib.parse, uuid
from time import gmtime, strftime
from lib import utils
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64


class func:
    def __init__(self):
        self.locale='en_US'
        self.timezone = 'Pacific/Auckland'
        self.systemtimezone = 'America/Indianapolis'
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
    def RaiseError(self, e):
        raise RuntimeError(e)
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
    def TreatAsContent(self, e):
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
    def DateAdd(self, date_str, add, intervel):
        date = datetime.strptime(date_str, '%m/%d/%y H:MI')

        # Create a timedelta of one day
        if intervel == 'Y':
            years = add
            one_day = timedelta(years)
        elif intervel =='M':
            months = add
            one_day = timedelta(months)
        elif intervel == 'D':
            days = add
            one_day = timedelta(days)
        elif intervel == 'H':
            hours = add
            one_day = timedelta(hours)
        elif intervel == 'MI':
            minutes = add
            one_day = timedelta(minutes)
        
        return date + one_day
 
    def DateDiff():
        pass
    def DateParse():
        pass
    def DatePart():
        pass
    def GetSendTime():
        pass
    def LocalDateToSystemDate(self, date):
        return date.astimezone(self.systemtimezone)
    def Now(self):
        return datetime.datetime.now()
    def SystemDateToLocalDate(self,date):

        # Convert the datetime object to the target timezone
        return date.astimezone(self.timezone)
    def Base64Decode(self, ciphertext):
        return base64.b64decode(ciphertext).decode('utf-8')
    def Base64Encode(self, ciphertext):
        return base64.b64encode(ciphertext).decode('utf-8')
    def DecryptSymmetric(self, data, padding, extkey,pw, saltkey, saltval,vectorkey, vectorval):
        backend = default_backend()
        iv = b'\x00' * 16  # Initialization Vector (IV) for AES, should be random for real applications
        cipher = Cipher(algorithms.AES(saltval), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()

        # Decode the base64 encoded ciphertext
        ciphertext = base64.b64decode(data)

        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the decrypted data
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data
    def EncryptSymmetric(self, data, padding, extkey,pw, saltkey, saltval,vectorkey, vectorval ):
        backend = default_backend()
        if 'des' in padding:
            iv = b'\x00' * 16
            t = 16*8
        elif 'aes' in padding: 
            iv = b'\x00' * 16
            t = 8*8

        cipher = Cipher(algorithms.AES(saltval), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(t).padder()

        # Pad the data to be a multiple of 16 bytes (AES block size)
        padded_data = padder.update(data) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def GUID(self):
        return str(uuid.uuid4())
    def MD5(self, e):
        return utils.decrypt('md5',e)
    def SHA1(self, e):
        return utils.decrypt('sha1',e)
    def SHA256(self, e):
        return utils.decrypt('sha256',e)
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
    def URLEncode(self, e, space = '', prefix=''):
        return urllib.parse.quote_plus(e)
    def WrapLongURL():
        pass
    def Add(self, a,b):
        return a+b
    def Divide(self,a,b):
        return a/b
    def FormatCurrency(self, num, iso = 'en_US', deci = 2, sym = ''):
        
        i = iso.split('_')
        
        f = open('../lib/locale.json')
        currencies = json.loads(f.read())

        s = ''
        if deci:
            s = "{:,.%s}" % deci
        if sym:
            s = sym +s
        else:
            for x in currencies:
                if x['country']==i[1]:
                    s = x['symbol']+s

        return s.format(num)
    def FormatNumber():
        pass
    def Mod(self, a, b):
        return a % b
    def Multiply(self, a, b):
        return a*b
    def Random(self, a,b):
        return random.randint(a,b)
    def Subtract(self, a,b):
        return a-b
    def AddMscrmListMember(self,name, num, attrname,attrvalue,addattrname,addattrvalue):
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
    def LongSFID(self, e) -> str:
        return utils.sf15to18(e)
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
    def Char(self,e,n=1):
        return chr(e)*n
    def Concat(*a):
        s = ''
        for n in a:
            s = s + n
        return s

    def Format(str,format,identicator = 'Date',iso=''):

        if identicator =='Date':
            return datetime.strptime(str, utils.cnv_csharp_date_fmt(format),iso)
        else:
            return str.format(format)
        
    def IndexOf(var, search) -> int:
        return var.find(search)
    def Length(self,e):
        return len(e)
    def Lowercase(self,e) -> str:
        return e.lower()
    def ProperCase(self, e) -> str:
        return e.title()
    def RegExMatch(self, str, regex) -> str:
        return re.search(regex, str)
    def Replace(self, str, r,e):
        return str.replace(r,e)
    def ReplaceList(str, replacement, *f ) -> str:
        for x in f:
            str = str.replace(x,replacement)
        return str
    def StringToDate(self,e):
        return e.strptime()
    def StringToHex(value):
        convert_string = int(value, base=16)
        convert_hex = hex(convert_string)
        return convert_hex, convert_string
    def Substring(str, pos, len) -> str:
        return str[pos,len]
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