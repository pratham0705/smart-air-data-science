import requests
import urllib3
import base64
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://airquality.cpcb.gov.in/aqi_dashboard/aqi_all_Parameters"

ACCESS_TOKEN = "eyJ0aW1lIjoxNzc3MzExNTk1NTIyLCJ0aW1lWm9uZU9mZnNldCI6LTMzMH0="
COOKIE = '_xsrf=ae4761d948724c9ba8a6b3239eb6e9eb; _ga=GA1.3.1915118830.1777311562; _gid=GA1.3.1972303896.1777311562; _gat=1; ccr_captcha="UHf7xnLUyY4w9SdCo6xftNXQcMn+5t5x/Yh5mk/eykiYC9+31kYZXjJieJykdBmTqfaVH9e8Duk7YJc19afTDzzZGbGshpWovyhNNlq2OEfrGhSf9k1XZt6akcwqDv4fpneJ58e+iEjL/jNNiSxXH+Xh1n6iv0uQ0vggckK72dITFc191EOjYFRkzY+F7GN/IEfvCayGeaZnciFXolAqhP4HovhEbh01eZ16O/sHIiPH+kiavzw8SoMNNCOISPP3UyPmWRb0Y+PHYhWsoJOt1A=="; _ga_40XB5TDTEW=GS2.3.s1777311562$o1$g1$t1777311585$j37$l0$h0; ccr_public="C3j1D0NeRjCAGRx+VJ8MurIgblXatUvwbapio0CtrNju0YShm1G1FWfWS2M5HDugSGRmQbKknJpcpwK83aASbG+I4wohvtF8fkl/+F1qilYqDQt7OvlreANI9uCb5xxlOMQFa+Z3rSYXtTEwcb617SzG35LhzElLGDe0a+1cDdJscqR/OU0wTB9rFWzrU9u9itGNyHaQB7J4GeXwrbD1PvHXQ+HspZ+cxONT4PRPB13iaidBSWTIO+RxVGpFUAwRVZVrfbvSBSKA0RQH/JxcNStiGy8f+239+nG3d4eaendVWsWS4P0SelR/MDQpSPPC0+uvCCMj/6oprx4wK9Cr3Un/hu9VOolJUGwB4IrkZFE="'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "text/plain, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://airquality.cpcb.gov.in",
    "Referer": "https://airquality.cpcb.gov.in/AQI_India/",
    "accesstoken": ACCESS_TOKEN,
    "Cookie": COOKIE
}

payload_dict = {
    "station_id": "site_301",
    "date": "2026-04-27T23:00:00Z"
}

payload_json = json.dumps(payload_dict, separators=(",", ":"))
encoded_payload = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")

response = requests.post(
    URL,
    data=encoded_payload,
    headers=HEADERS,
    verify=False
)

print("Status:", response.status_code)
print("Response:")
print(response.text[:3000])