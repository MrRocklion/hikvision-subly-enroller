import requests
from requests.auth import HTTPDigestAuth
url = "https://192.168.88.253/ISAPI/Intelligent/FDLib/FDSetUp?format=json"

payload = {'FaceDataRecord': '{"faceLibType":"blackFD","FDID":"1","FPID":"35"}'}
files=[
  ('img',('WhatsApp Image 2025-04-18 at 16.21.51_f6cdce2b.jpg',open('C:/Users/Admin/Desktop/WhatsApp Image 2025-04-18 at 16.21.51_f6cdce2b.jpg','rb'),'image/jpeg'))
]
headers = {}
response = requests.put( url, headers=headers, data=payload, files=files ,auth=HTTPDigestAuth('admin','Hik12345'),verify=False)
print(response.text)
