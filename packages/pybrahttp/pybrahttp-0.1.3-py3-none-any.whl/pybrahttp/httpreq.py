from enum import Enum
import requests
import time
#from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import base64
import orjson


class THttpType(Enum):
    """THttpType Liste of Authentication type for Http
    """
    BasicUsrPws = 0 #Basic user/password
    Token = 1 #Token
    Tokenpermanent = 2 #Tokenpermanent
    ApiKey = 3 #API Keypy install get enum
    OAuth2 = 4 #OAuth2

class THttpMethode(Enum):
    """THttpMethode Liste of methode available for request Http
    """
    GET = 0 #Get
    POST = 1 #Post
    PUT = 2 #Put

class Http :
    """ To commincate with web and webmethode
    """
    def __init__(self, aAuthType : THttpType):
        """__init__ 
            Cretae and manage QHttp request
            
        Parameters
        ----------
        DataConnection : pyodbc.Cursor
            The ADS database connection cursor
        """
        self._AuthType     = THttpType.BasicUsrPws
        self._AuthType     = aAuthType
        self._userName     = ''
        self._passWord     = ''
        self._Url          = ''
        self._headers      = {}
        self._methode      = '' 
        self._headers      = ''
        self._body         = ''
        self._tokenRefresh = '' #Url for thoken request/refresh
        self._tokenType    = 'Bearer'
        self._tokenAccess  = ''
        self._tokendelais  = 3600 #ms
        self._tokendata    = {}
        self._tokenendpoint = '' 
        self._tokenclient_id = ''
        self._tokenclient_secret = ''
        self._tokenresource = ''
        
        match self._AuthType:
            case THttpType.Token, THttpType.Tokenpermanent:
                #Token, Tokenpermanent
                self._userName = 'Bearer'

            case THttpType.ApiKey:
               #ApiKey
                self._userName = 'ApiKey'

    def request(self, aHttpMethode : THttpMethode, aUrl : str, aBody : dict = {})->dict:
        self._Url = aUrl
        value = ''
        statusCode = 200
        reason = ''
        
        token = {
            'access_token': 'eswfld123kjhn1v5423',
            'refresh_token': 'asdfkljh23490sdf',
            'token_type': {self._tokenType},
            'expires_in': {self._tokendelais},     # initially 3600, need to be updated by you
            }
          
        extra = {
            'client_id': {self._userName},
            'client_secret': r''.join(self._passWord),
            }
        
        self.__testAuthMode()
        
        if self._AuthType == THttpType.OAuth2:
            #OAuth2
            #implémentation not finished
            oauth = OAuth2Session(self._userName, token=token, auto_refresh_url=self._tokenRefresh,
                                  auto_refresh_kwargs=extra, token_updater=self._token_saver)                  
            response = oauth.get(self._Url)
        else:
            match self._AuthType:
                case THttpType.Token:                      
                    #Token
                    auth_header = self._get_authorization_header()
                    self._headers['Authorization'] = auth_header

                case THttpType.Tokenpermanent:
                    #Tokenpermanent
                    self._headers['Authorization'] = f"{self._userName} {self._passWord}"
                
                case THttpType.ApiKey:
                    #APIKEY
                    self._userName = 'ApiKey'
                    self._headers['Authorization'] = f"{self._userName} {self._passWord}"
              
                case _:
                    #BasicUsrPws:
                    credentials = f"{self._userName}:{self._passWord}"
                    #encode credentials in base 64
                    encoded_cred = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                    #creating Authorisation header value
                    self._headers['Authorization'] = f"Basic {encoded_cred}"
                                            
            if (len(aBody) == 0):
                match aHttpMethode:
                    case  THttpMethode.GET:
                        response = requests.get(self._Url, headers=self._headers)
                    case THttpMethode.POST:
                        response = requests.post(self._Url, headers=self._headers)
                    case THttpMethode.PUT:
                        response = requests.put(self._Url, headers=self._headers)
            else:
                match aHttpMethode:
                    case  THttpMethode.GET:
                        response = requests.get(self._Url, headers=self._headers, json=aBody)
                    case THttpMethode.POST:
                        response = requests.post(self._Url, headers=self._headers, json=aBody)
                    case THttpMethode.PUT:
                        response = requests.put(self._Url, headers=self._headers, json=aBody)

        statusCode = response.status_code
        reason = response.reason
        
        if len(response.content) != 0:
            if 'application/json' in response.headers.get('content-type'):
                value = orjson.loads(response.content)
            else:
                value = response.content
          
        while (type(value) == list):
            value = value[0]
        
        retValue ={
            'statusCode' : statusCode,
            'reason' : reason,
            'content' : value,
            'headers' : response.headers
            }    
              
        return retValue
     
    #private functions
    def _token_is_valid(self, buffer_seconds=300):
        """
        Vérifie si le token est valide avec une marge de sécurité
        
        Args:
            buffer_seconds (int): Marge de sécurité en secondes avant expiration
            
        Returns:
            bool: True si le token est valide, False sinon
        """
        if not self._tokendata:
            return False
        
        # Vérifier si expires_on est présent et est un nombre
        try:
            expires_on = int(self._tokendata.get('expires_on', 0))
            current_time = int(time.time())
            
            # Le token est valide si le temps d'expiration moins la marge est supérieur au temps actuel
            return expires_on - buffer_seconds > current_time
        except (ValueError, TypeError):
            return False
    
    def _refresh_token(self):
        """
        Rafraîchit le token OAuth
        
        Returns:
            bool: True si le rafraîchissement a réussi, False sinon
        """
        if not self._tokenendpoint or not self._tokenclient_id or not self._tokenclient_secret or not self._tokenresource:
            raise ValueError("Token renewal information is incomplete")
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': self.resource
        }
        
        try:
            response = requests.post(self._tokenendpoint, data=data)
            response.raise_for_status()
            
            self._tokendata = response.json()
            #self.save_token_to_file()
            return True
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            return False
        
    def _ensure_valid_token(self):
        """
        S'assure que le token est valide, le rafraîchit si nécessaire
        
        Returns:
            bool: True si le token est valide, False sinon
        """
        if not self._token_is_valid():
            return self._refresh_token()
        return True
    
    def _get_authorization_header(self):
        """
        Récupère l'en-tête d'autorisation avec le token Bearer
        
        Returns:
            dict: En-tête d'autorisation
        """
        if not self._ensure_valid_token():
            raise ValueError('Impossible to get a valid token!!')
        
        return f"{self._tokendata.get('token_type', 'Bearer')} {self._tokendata.get('access_token')}"
        #return {
        #    Authorization': f"{self._tokendata.get('token_type', 'Bearer')} {self._tokendata.get('access_token')}"
        #}

    def _token_saver(self, token):
        self._tokenAccess = token

    def __testAuthMode(self)->bool:
        """__testAuthMode Contole if informations needed 
        by authentication mode are available

        Returns
        -------
        bool
            True if all corract
        """
        authModeallowed = False

        match self._AuthType:
            case THttpType.Token:
                #Token
                if ((self._tokenendpoint == "") or (self._tokenclient_id == "") or 
                    (self._tokenclient_secret == "") or (self._tokenresource == '')):
                    raise ValueError('Token mode, the Acces user, password must be filled.')

            case THttpType.ApiKey:
                #ApiKey
                if (self._passWord == ''):
                    raise ValueError('API ket mode, the password must be filled.')
                        
            case THttpType.OAuth2:
                #OAuth2
                if ((self._userName == '') or (self._passWord == '') or 
                    (self._tokenRefresh == '')):
                    raise ValueError('OAuth2 mode, the user, password and Token refresh must be filled.')

            case _:
                #BasicUsrPws:
                if ((self._userName == '') or (self._passWord == '')):
                    raise ValueError('Basic mode, the user and password must be filled.')
        
        authModeallowed

        return authModeallowed

    #property function
    def __getUserName(self)->str:
        return self._userName

    def __setUserName(self, aUsrName : str):
        if self._AuthType == THttpType.Token:
                #Token
                raise ValueError('Http Token mode, impossible to set username.')
        elif self._AuthType == THttpType.ApiKey:
                #ApiKey
                raise ValueError('Http API key mode, impossible to set username.')
        else:
            self._userName = aUsrName

    def __getpassWord(self)->str:
        return self._passWord
    
    def __setpassWord(self, aPassWord : str):
        self._passWord = aPassWord

    def __getAuthType(self)->THttpType:
        return self._AuthType

    def __getHeaders(self)->dict:
        return self._headers
    
    def __setHeaders(self, aHeaders : dict):
        self._headers = aHeaders

    def __getUrl(self)->str:
        return self._Url
    
    def __setUrl(self, aUrl : str):
        self._Url = aUrl

    def __getEndpoint(self)->str:
        return self._tokenendpoint

    def __setEndpoint(self, aEndpoint : str):
        self._tokenendpoint = aEndpoint
    
    def __getClientid(self)->str:
        return self._tokenclient_id

    def __setClientid(self, aClientid : str):
        self._tokenclient_id = aClientid
    
    def __getClientsecret(self)->str:
        return self._tokenclient_secret

    def __setClientsecret(self, aClientsecret : str):
        self._tokenclient_secret = aClientsecret
    
    def __getResource(self)->str:
        return self._tokenresource

    def __setResource(self, aResource : str):
        self._tokenresource = aResource

    # Set property() to use get_name, set_name and del_name methods
    userName = property(__getUserName, __setUserName)
    passWord = property(__getpassWord, __setpassWord)
    authType = property(__getAuthType)
    headers = property(__getHeaders, __setHeaders)
    url = property(__getUrl,__setUrl)
    endpoint = property(__getEndpoint,__setEndpoint)
    client_id = property(__getClientid,__setClientid)
    client_secret = property(__getClientsecret,__setClientsecret)
    resource = property(__getResource,__setResource)