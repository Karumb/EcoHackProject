import datetime, time
import requests, urllib, json
import pandas as pd, numpy as np
from tqdm import tqdm

stations = 'stations.txt'
some_stations = pd.read_excel('some_stations.xlsx')
delta_lat, delta_lon = 0.08, 0.08 # по желанию можно изменить, нужны для проверки попадания человека в радиус действия станции

def nearest_station(lat, lon):
    distances = []
    for i in range(len(list(some_stations['station']))):
        distance = abs(lat-some_stations['lat'][i])**2 + abs(lon-some_stations['lon'][i])**2
        distances.append(distance)
    index = distances.index(min(distances))
    return [some_stations['station'][index], some_stations['имя станции'][index]]

def check_radius(lat, lon):
    nearest_stations = []
    nearest_stations_names = []
    for i in range(len(list(some_stations['station']))):
        station_lat, station_lon = some_stations['lat'][i], some_stations['lon'][i]
        distance = (abs(lat-station_lat))**2 + (abs(lon-station_lon))**2
        radius = delta_lat**2 + delta_lon**2
        if distance <= radius:
            nearest_stations.append(list(some_stations['station'])[i])
            nearest_stations_names.append(list(some_stations['имя станции'])[i])
        else:
            pass
    if len(nearest_stations) == 0:
        print('Поблизости от вас нет никаких станций', '\n')
        return False
    else:
        print('Вы находитесь рядом со станциями:', ', '.join(nearest_stations_names), '\n')
        return [nearest_stations, nearest_stations_names]

def prepare_urls(stations, nearest):
    urls = []
    with open(stations, 'r') as f:
        for line in f:
            urls.append(line.split("'")[1])
    names = [urls[i].split('/')[-2] for i in range(len(urls))]
    urls_nearest = []
    for i in range(len(names)):
        if names[i] in nearest:
            urls_nearest.append(urls[i])
        else:
            pass
    return urls_nearest

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')

def format_date(file):
    for elem in file.keys():
        data = file[elem]
        for elem in data.keys():
            time_data = data[elem]
            for elem in time_data.keys():
                values = time_data[elem]['data']
                for i in range(len(values)):
                    values[i][0] = (datetime.datetime(1970, 1, 1)+datetime.timedelta(seconds=values[i][0]/1000)).isoformat()
    return file

def form_json(url):
    massive = get_html(url).split(' ')
    for elem in massive:
        if elem.split('.init')[0] == 'AirCharts':
            elem = json.loads(str(elem.replace('AirCharts.init(', '')[0:-1]))
            save_json(elem)
            format_date(elem)
            return elem

def form_data(stations):
    all_data = {}
    for i in tqdm(range(len(stations))):
        # print('Выгружается информация по станции:', stations[i].split('/')[-2])
        all_data[stations[i].split('/')[-2]] = form_json(stations[i])
    return all_data

def save_json(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def output_information_one(lat, lon):
    initial_data = nearest_station(lat, lon)
    s, names = initial_data[0], initial_data[1]
    data = form_data(prepare_urls(stations, s))
    time_data = data[s]['units']['h']  # выводим данные в мг/м^3
    blya = ''
    for chemical in list(time_data.keys()):
        values = time_data[chemical]['data'][-1]
        if 'OZ' in chemical and values[1]+0.03 > 0.07:
            blya += '\nОБНАРУЖЕНО ПРЕВЫШЕНИЕ 03 В ВАШЕЙ ЛОКАЦИИ! \n\nВаши устройства закрыли окно\n\n'
            blya += chemical + ' : {} мг/м^3\n'.format(values[1]+0.03)
        #if values[1] == None:
            #blya += chemical + ' : данные отсутствуют\n'
        #else:
             #blya += chemical + ' : {} мг/м^3\n'.format(values[1])
    blya += 'Данные выведены за {}'.format(values[0])
    return(blya)

def output_information_many(lat, lon):
    initial_data = check_radius(lat, lon)
    if initial_data == False:
        return None
    else:
        s, names = initial_data[0], initial_data[1]
        data = form_data(prepare_urls(stations, s))
        for i in range(len(s)):
            print('Данные на станции {}:'.format(names[i]))
            time_data = data[s[i]]['units']['h'] #выводим данные в мг/м^3
            for chemical in list(time_data.keys()):
                values = time_data[chemical]['data'][-1]
                if values[1] == None:
                    print(chemical, ': данные отсутствуют')
                else:
                    print(chemical, ': {} мг/м^3'.format(values[1]))
            print('\n')
        print('Данные выведены за {}'.format(values[0]), '\n')

def cycle():
    print('Пожалуйста, введите новые координаты:', '\n')
    lat, lon = float(input()), float(input())
    print('\n')
    print('Пожалуйста, введите количество станций (1 если одна станция и n если несколько):', '\n')
    number = input()
    print('\n')
    if number == str(1):
        output_information_one(lat, lon)
    else:
        output_information_many(lat, lon)
    cycle()

#if __name__ == '__main__':
   # cycle()