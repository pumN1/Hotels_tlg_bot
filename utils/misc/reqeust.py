import json
import requests
from config_data import config


headers = {
	"content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}
#
#
def api_request(method_endswith, params, method_type):
	"""
	Args:
		method_endswith: Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
		params: Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
		method_type: Метод\тип запроса GET\POST

	Returns:

	"""
	try:
		url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
	#
		# В зависимости от типа запроса вызываем соответствующую функцию
		if method_type == 'GET':
			return get_request(url=url, params=params)
		else:
			return post_request(url=url, params=params)
	except:
		api_request(method_endswith, params, method_type)
#
#
def get_request(url, params):
	try:
		response = requests.get(url=url, headers=headers, params=params, timeout=15)
		if response.status_code == requests.codes.ok:
			return response.text
	except:
		raise TimeoutError()
#
#
def post_request(url, params):
	"""
	Args:
		url:
		params:

	Returns:

	"""
	try:
		response = requests.post(url=url,  json=params, headers=headers, timeout=15)
		if response.status_code == requests.codes.ok:
			return response.text
	except:
		raise TimeoutError()


def city_request(city):
	"""
	Функция для поиска id города
	Returns:

	"""
	try:
		res = api_request('locations/v3/search', {'q': city, 'locale': 'ru_RU'}, 'GET')
		data = json.loads(res)
		city_id = data['sr'][0]['gaiaId']
		return city_id
	except:
		city_request(city)


# Отели
def city_detail_request(city):
	payload = {
		"currency": "USD",
		"eapid": 1,
		"locale": "ru_RU",
		"siteId": 300000001,
		"destination": {"regionId": f"{city_request(city)}"},
		"checkInDate": {
			"day": 10,
			"month": 10,
			"year": 2022
		},
		"checkOutDate": {
			"day": 15,
			"month": 10,
			"year": 2022
		},
		"rooms": [
			{
				"adults": 2,
				"children": [{"age": 5}, {"age": 7}]
			}
		],
		"resultsStartingIndex": 0,
		"resultsSize": 200,
		"sort": "PRICE_LOW_TO_HIGH",
		"filters": {"price": {
			"max": 150,
			"min": 100
		}}
	}

	res = api_request(method_endswith='properties/v2/list', params=payload, method_type='POST')
	if res:
		data = json.loads(res)
		return data
	else:
		city_detail_request(city)


def get_hotels_info(payload):
	res = api_request(method_endswith='properties/v2/detail', params=payload, method_type='POST')
	data = json.loads(res)
	hotel_info = data['data']['propertyInfo']
	return hotel_info


def get_hotels(data):
	hotel_info_list = []
	sort_order = ''
	if data.get('command') == 'lowprice':
		sort_order = 'PRICE_LOW_TO_HIGH'
	elif data.get('command') == 'highprice':
		sort_order ='PRICE_HIGHEST_FIRST'
	elif data.get('command') == 'bestdeal':
		sort_order = 'DISTANCE_FROM_LANDMARK'
	payload = {
		"currency": "USD",
		"eapid": 1,
		"locale": "ru_RU",
		"siteId": 300000001,
		"destination": {"regionId": f"{data['local_city']}"},
		"checkInDate": {
			"day": data['date_in'].day,
			"month": data['date_in'].month,
			"year": data['date_in'].year
		},
		"checkOutDate": {
			"day": data['date_out'].day,
			"month": data['date_out'].month,
			"year": data['date_out'].year
		},
		"rooms": [
			{
				"adults": 2,
				"children": []
			}
		],
		"resultsStartingIndex": 0,
		"resultsSize": int(data['num_hotels']),
		"sort": sort_order,
		"filters": {"price": {
			"max": 150,
			"min": 40
		}}
	}
	res = api_request(method_endswith='properties/v2/list', params=payload, method_type='POST')
	if res:
		data = json.loads(res)
		hotels_list = data['data']['propertySearch']['properties']
		for hotel in hotels_list:
			payload_hotel = {
				"currency": "USD",
				"eapid": 1,
				"locale": "ru_Ru",
				"siteId": 300000001,
				"propertyId": f"{hotel['id']}"
			}
			hotel_info = get_hotels_info(payload_hotel)
			hotel_info_dict = {}
			star = hotel_info['summary']['overview'].get('propertyRating', {})
			price = hotel['price'].get('strikeOut', {})
			hotel_dict = {
					'Название:': hotel['name'],
					'Описание:': hotel_info['summary'].get('tagline', None),
					'Звезды:': f"{star.get('rating', {})} ⭐" if star else 'нет данных',
					'Рейтинг:': hotel_info['reviewInfo']['summary']['overallScoreWithDescriptionA11y'].get('value', None).split('/')[0],
					'Расстояние до центра, км:': hotel['destinationInfo']['distanceFromDestination'].get('value', None),
					'Цена за 1 ночь, $:': round(price.get('amount', {}), 2) if price else 'нет данных',
					'Цена за 1 ночь со скидкой, $:': round(hotel['price']['lead'].get('amount', None), 2),
					'Цена за все время, включая налоги и сборы:':
						hotel['price']['displayMessages'][1]['lineItems'][0].get('value', None).split()[0],
					'Адрес:': hotel_info['summary']['location']['address'].get('addressLine', None),
				}

			for key, value in hotel_dict.items():
				if value:
					hotel_info_dict.update({key: value})
			hotel_info_list.append([hotel['propertyImage']['image'].get('url', None),
									hotel_info_dict, hotel['id']])
		return hotel_info_list
	else:
		get_hotels(payload)
