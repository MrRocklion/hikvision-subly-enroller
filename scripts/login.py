import requests
request_url='http://192.168.88.253:80/ISAPI/System/deviceInfo'
#Settheauthenticationinformation
auth=requests.auth.HTTPDigestAuth('admin','Hik12345')
#Sendtherequestandreceiveresponse
response=requests.get(request_url,auth=auth)
#Outputresponsecontent
print(response.text)