import requests

url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"

querystring = {
    "namePrefix":"luxemb",
    "limit":"10", 
    "sort":"-population"
}

headers = {
	"X-RapidAPI-Key": "c0c2759532msh8d152b57f44bf8ep1ac8c4jsn74b8c5e82525",
	"X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()
city_names = [city['name'] for city in data['data']]
country_names = [city['country'] for city in data['data']]
for i in range(len(city_names)):
    print(city_names[i] + ",", country_names[i])