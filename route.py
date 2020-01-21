import json
with open('data', 'r', encoding='UTF-8') as data_file:
    data = [json.loads(line.strip()) for line in data_file]

route = []
for signal in data:
    if 'geo' in signal:
        route.append(signal['geo'])
print(route)
