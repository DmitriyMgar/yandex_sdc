import json
import requests
from math import sin, cos, sqrt, atan2, radians
import numpy as np


def get_distance_between_two_points(point1, point2):
    r = 6372795  # радиус Земли в метрах

    lat1 = radians(point1['lat'])
    lon1 = radians(point1['lon'])
    lat2 = radians(point2['lat'])
    lon2 = radians(point2['lon'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return r * c


def calculate_distance(url):
    # читаем полученные данные
    r = requests.get(url, stream=True)
    with open("data", "wb") as data_file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                data_file.write(chunk)

    with open('data', 'r') as data_file:
        data = [json.loads(line.strip()) for line in data_file]

    # отсортируем масссив по времени
    data = sorted(data, key=lambda s: s["ts"])

    # теперь "почистим" данные: уберем точки где машина неподвижна (они нас не интересуют) и выбросы
    # для этого дополним гео-данные расстоянием до предыдущей точки
    start_point = next(s['geo'] for s in data if 'geo' in s)
    for signal in data:
        if 'geo' in signal:
            signal['distance'] = get_distance_between_two_points(start_point, signal['geo'])
            start_point = signal['geo']

    # убираем точки где машина неподвижна (+/- 1 см)
    data = list(filter(lambda a: ('distance' in a and a['distance'] > 0.01) or 'control_switch_on' in a, data))

    # теперь "почистим" данные от выбросов
    # для этого найдем 1ю и 3ю квартили и межквартильное расстояние
    distance = [a['distance'] for a in data if 'distance' in a]
    q1 = np.percentile(distance, 25, interpolation='midpoint')
    q3 = np.percentile(distance, 75, interpolation='midpoint')
    iqr = q3 - q1
    # все что не попадает в диапазон [(q1 - 1.5 * iqr),(q3 + 1.5 * iqr)] считаем выбросами
    data = list(
        filter(
            lambda a: ('distance' in a and (q1 - 1.5 * iqr) < a['distance'] < (q3 + 1.5 * iqr)) or 'control_switch_on' in a,
            data
        )
    )

    # избавившись от лишних данных, переходим к подсчету расстояния пройденного на автопилоте и в ручном режиме
    autopilot = None  # флаг работы автопилота (в начале нет данных)
    autopilot_distance = 0  # расстояние пройденное на автопилоте
    manual_distance = 0  # расстояине пройденное в ручном режиме
    for signal in data:
        if 'control_switch_on' in signal:
            if autopilot != signal['control_switch_on']:  # изменился режим управления
                autopilot = signal['control_switch_on']
        elif 'geo' in signal and autopilot is not None:
            if autopilot:
                autopilot_distance += signal['distance']
            else:
                manual_distance += signal['distance']

    # выводим результат
    print('autopilot distance: {0}m'.format(round(autopilot_distance, 1)))
    print('manual control distance: {0}m'.format(round(manual_distance, 1)))


# calculate_distance("https://sdcimages.s3.yandex.net/test_task/data")
# autopilot distance: 2577.4m
# manual control distance: 264.5m
