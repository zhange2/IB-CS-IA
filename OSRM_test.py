import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.geoapify.com/v1/routematrix?apiKey=1981c018315840e1b4111d0e9ec78a6b"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"

data = '{"mode":"drive","sources":[{"location":[8.73784862216246,48.543061473317266]},{"location":[9.305536080205002,48.56743450655594]},{"location":[9.182792846033067,48.09414029055267]}],"targets":[{"location":[8.73784862216246,48.543061473317266]},{"location":[9.305536080205002,48.56743450655594]},{"location":[9.182792846033067,48.09414029055267]}]}'


resp = requests.post(url, headers=headers, data=data)

print(resp.status_code)