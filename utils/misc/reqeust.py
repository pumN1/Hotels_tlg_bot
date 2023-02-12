import json
import requests
from typing import List, Dict
from config_data import config
from handlers.custom_heandlers.bestdeal import get_hotels_list
from loguru import logger


headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def api_request(method_endswith, params, method_type):
    """
    Args:
        method_endswith: Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
        params: Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
        method_type: Метод\тип запроса GET\POST

    Returns:
        функцию GET или POST запроса
    """
    try:
        url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

        # В зависимости от типа запроса вызываем соответствующую функцию
        if method_type == 'GET':
            return get_request(url=url, params=params)
        else:
            return post_request(url=url, params=params)
    except:
        logger.debug('Ошибка запроса api_request')
#
#
def get_request(url, params):
    """
    Args:
        url: url-адрес
        params: json-файл с необходимым набором данных для запроса
    Returns:
        response: тело ответа на get-запрос
    """
    try:
        response = requests.get(url=url, headers=headers, params=params, timeout=15)
        if response.status_code == requests.codes.ok:
            return response.text
    except:
        raise TimeoutError()
#
#
def post_request(url: str, params: Dict) -> str:
    """
    Args:
        url: url-адрес
        params: json-файл с необходимым набором данных для запроса
    Returns:
        response: тело ответа на post-запрос
    """
    try:
        response = requests.post(url=url,  json=params, headers=headers, timeout=15)
        if response.status_code == requests.codes.ok:
            return response.text
    except:
        raise TimeoutError()


def city_request(city: str) -> int:
    """
    Функция для получения id города
     Args:
        city: название города из сообщения пользователя
    Returns:
        city_id: id города
    """
    try:
        res = api_request('locations/v3/search', {'q': city, 'locale': 'ru_RU'}, 'GET')
        for i_data in json.loads(res)['sr']:
            if i_data['type'] == "CITY":
                city_id = i_data['gaiaId']
                return city_id
    except:
        logger.debug('Ошибка запроса id города city_request')


# Отели
def city_detail_request(city: str) -> Dict:
    """
    Функция для уточнения местности для поиска отелей
    Args:
        city: название города из сообщения пользователя
    Returns:
        data: dict: словарь окрестностей города для поиска отелей
    """
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
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 1,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 150,
            "min": 100
        }}
    }
    try:
        res = api_request(method_endswith='properties/v2/list', params=payload, method_type='POST')
        if res:
            data = json.loads(res)['data']['propertySearch']['filterMetadata'].get('neighborhoods')
            return data
    except:
        logger.debug('Ошибка запроса окрестностей города city_detail_request')


def get_hotels_info(payload: Dict) -> Dict:
    """
    Функция получения информации по отелям
    Args:
        payload:

    Returns:
        hotel_info: dict: словарь с данными по отелю
    """
    try:
        res = api_request(method_endswith='properties/v2/detail', params=payload, method_type='POST')
        data = json.loads(res)
        hotel_info = data['data']['propertyInfo']
        return hotel_info
    except:
        logger.debug('Ошибка запроса информации об отеле get_hotels_info')


def get_hotels(data_states: Dict) -> List:
    """
    Функция получения описания отелей
    Args:
        data_states: данные, вводимые пользователем
    Returns:
        hotel_info_list: список данных для карточек отелей
    """
    try:
        hotel_info_list = []
        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_RU",
            "siteId": 300000001,
            "destination": {"regionId": f"{data_states['local_city']}"},
            "checkInDate": {
                "day": data_states['date_in'].day,
                "month": data_states['date_in'].month,
                "year": data_states['date_in'].year
            },
            "checkOutDate": {
                "day": data_states['date_out'].day,
                "month": data_states['date_out'].month,
                "year": data_states['date_out'].year
            },
            "rooms": [
                {
                    "adults": data_states['num_adults'],
                    "children": data_states['num_children']
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": 'PRICE_LOW_TO_HIGH',
            "filters": {"price": {
                "max": 2000,
                "min": 1
            }}
        }
        if data_states.get('command') == 'lowprice':
            payload["resultsSize"] = int(data_states['num_hotels'])
        elif data_states.get('command') == 'bestdeal':
            payload['filters']["price"]["max"] = int(data_states['price_range'].split('-')[1])
            payload['filters']["price"]["min"] = int(data_states['price_range'].split('-')[0])
        res = api_request(method_endswith='properties/v2/list', params=payload, method_type='POST')
        if res:
            data = json.loads(res)
            hotels_list = data['data']['propertySearch']['properties']
            if data_states.get('command') == 'highprice':
                hotels_list = hotels_list[-1:-(int(data_states['num_hotels'])+1):-1]
            if data_states.get('command') == 'bestdeal':
                hotels_list = get_hotels_list(
                    hotels_list=json.loads(res)['data']['propertySearch']['properties'],
                    dist_range=data_states.get('dist_range'),
                    num_hotels=int(data_states['num_hotels'])
                )
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
                        'Описание:': hotel_info['summary'].get('tagline'),
                        'Звезды:': f"{star.get('rating', {})} ⭐" if star else 'нет звезд',
                        'Рейтинг:': hotel_info['reviewInfo']['summary']['overallScoreWithDescriptionA11y'].get('value').split('/')[0],
                        'Расстояние до центра, км:': hotel['destinationInfo']['distanceFromDestination'].get('value'),
                        'Цена за 1 ночь, $:': round(price.get('amount', {}), 2) if price else None,
                        'Цена за 1 ночь со скидкой, $:': round(hotel['price']['lead'].get('amount'), 2),
                        'Цена за все время, включая налоги и сборы:':
                            hotel['price']['displayMessages'][1]['lineItems'][0].get('value').split()[0],
                        'Адрес:': hotel_info['summary']['location']['address'].get('addressLine'),
                    }

                for key, value in hotel_dict.items():
                    if value:
                        hotel_info_dict.update({key: value})
                hotel_info_list.append([hotel['propertyImage']['image'].get('url', None),
                                        hotel_info_dict, hotel['id']])
            return hotel_info_list
    except Exception as ex:
        logger.debug('Ошибка запроса информации об отелях get_hotels')
        logger.error(ex.__repr__())
