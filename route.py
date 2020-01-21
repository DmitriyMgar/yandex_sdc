import json
from math import sin, cos, sqrt, atan2, radians


def get_distance_between_two_points(point1, point2):
    R = 6372795

    lat1 = radians(point1['lat'])
    lon1 = radians(point1['lon'])
    lat2 = radians(point2['lat'])
    lon2 = radians(point2['lon'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1q

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_distance_by_route(route):
    distance = 0
    start_point = route.pop(0)
    for point in route:
        d = get_distance_between_two_points(start_point, point)
        if d > 10:  # подозрительно большое расстояние
            if point['lat'] == 0 and point['lon'] == 0:  # ошибочная точка
                continue  # пропускаем её
        distance += d
        start_point = point
    return distance


with open('data', 'r', encoding='UTF-8') as data_file:
    data = [json.loads(line.strip()) for line in data_file]
data = sorted(data, key=lambda signal: signal["ts"])


autopilot = None
autopilot_changed = None
autopilot_route = []
manual_route = []
current_route = []
for signal in data:
    if 'control_switch_on' in signal:
        autopilot_changed = autopilot != signal['control_switch_on']
        if autopilot_changed:
            print("autopilot {0}".format(['off', 'on'][signal['control_switch_on']]))
            if autopilot:
                autopilot_route.append(current_route)
            else:
                manual_route.append(current_route)
            current_route = []
            autopilot = signal['control_switch_on']
    elif 'geo' in signal:
        current_route.append(signal['geo'])

print("manual control:")
for route in manual_route:
    get_distance_by_route(route)
    print("route consist of {0} points".format(len(route)))
    print(get_distance_by_route(route))

print("autopilot:")
for route in autopilot_route:
    print("route consist of {0} points".format(len(route)))
    print(get_distance_by_route(route))

