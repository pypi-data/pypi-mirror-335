# pybraads Readme 📜
Brainstorming package, manage http request.

# Installation ⚡
Opérating system :  Windows, MacOS & Linux :

# Available function/class 📑
## THttpType
    A collection of authentication types.
    BasicUsrPws = 0 #Basic user/password
    Token = 1 #Token
    ApiKey = 2 #API Keypy install get enum
    OAuth2 = 3 #OAuth2
## THttpMethode
    A collection af available methodes.
    GET = 0 #Get
    POST = 1 #Post
    PUT = 2 #Put
## Http(aAuthType)
    To create an http connection.
    aAuthType, the authentication type for the connection.    
### request(aHttpMethode : THttpMethode, aUrl : str, aBody : dict = {})
    To request an url.
    aHttpMethode, and http methode.
    aUrl, the url to communicate. 
    aBody : a dict with the body to send to the url.
    return a dict with the full answer.
    retValue ={
            'statusCode' : statusCode,
            'reason' : reason,
            'content' : value,
            'headers' : response.headers
            }
### userName
    To get or set the authentication user.
### passWord
    To get or set the authentication password.
### authType
    To get the authentication type.
### headers
    To get or set the http header.
### error
    To get the last error.
### url
    To get or set the url.

# Howto use 📰
    import pybrahttp
    
    try:
        http = pybrahttp.Http(pybrahttp.THttpType.BasicUsrPws)
        http.userName = aUser
        http.passWord = aPws
        headers ={
            'User-Agent' : 'Brainstorming 1.0', 
            'content-type' : 'application/json',
            'Accept' : '*/*',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Connection' : 'keep-alive'
            }
        http.headers = headers
        url = aurl
        #Exemple of XML body 
        body ={
            'Name' : 'Timesheet(s) ' + str(aParams[3]) + '- ' + str(aParams[0]),
            'Initiator' : aParams[1],
            "AutomaticReminder": {
                "IsSendAutomaticRemindersEnabled": True,
                "DaysBeforeFirstReminder": DaysBeforeFirstReminder,
                "IsRepeatRemindersEnabled": True,
                "RepeatReminders":RepeatReminders
                }
            }
        
        re = http.request(pybrahttp.THttpMethode.POST, url, body)
        if (re['statusCode'] >= 200) and (re['statusCode'] <= 250):
            #Do code if no error
        else:
            #Print the returned error
            print(str(re['content']))
            return False

## Meta 💬
Brainstorming – Support.erp@brainstorming.eu

Distributed under the MIT license. See ``LICENSE`` for more information.