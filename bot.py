import telebot
import config
import telebot.types as types
import csv
from mosecom_parser import output_information_one
#Определяем функции для поиска по файлам
def findgeo(uid):
    with open('locations.csv', newline='') as base:
        data = csv.reader(base, delimiter = ';')
        geos = ''
        for row in data:
            if str(uid) in row[0]:
                geos += row[-1] + ': ' + row[1] + ' ' + row[2] + '\n'
    if geos == '':
        return 'У вас еще нет локаций'
    return geos

def findgeodata(uid, geoname):
    with open('locations.csv', newline='') as base:
        data = csv.reader(base, delimiter = ';')
        geos = []
        for row in data:
            if str(uid) in row[0] and str(geoname) in row[3]:
                geos += [row[1], row[2]] 
    if geos == []:
        return 'Ошибка! Нет такой локации!'
    return geos

def deviceadd(uid, name, did, dtype, lat, long):
    with open('devices.csv', 'a', newline='') as base:
        data = csv.writer(base, delimiter = ';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data.writerow([uid, did, dtype, name, lat, long])
        
        
def addgeo(uid, geoname, lat, long):
    with open('locations.csv', 'a', newline='') as base:
        data = csv.writer(base, delimiter = ';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data.writerow([uid, lat, long, geoname])

def finddevice(uid):
    with open('devices.csv', newline='') as base:
        data = csv.reader(base, delimiter = ';')
        devices = ''
        for row in data:
            if str(uid) in row[0]:
                devices += f'Устройство \"{row[3]}\", Тип: {row[2]}, Местоположение: {row[-2]} {row[-1]}\n\n'
    if devices == '':
        return 'У вас еще нет подключенных устройств... \n\nНу так добавьте!'
    return devices

def printgeos(uid, message):
    with open('locations.csv', newline='') as base:
        data = csv.reader(base, delimiter = ';')
        for row in data:
            if row[3] == 'MSU':
                bot.send_message(message.from_user.id, 
                                 'По вашей локации {0} обнаружены данные: \n\n{1}'.format(row[3], 
                                                                                          output_information_one(float(row[1]), float(row[2]))))


def adduser(uid, username):
    with open('users.csv', 'a', newline='') as base:
        data = csv.writer(base, delimiter = ';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data.writerow([uid, username])
        
def geosmarkup(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    with open('locations.csv', 'r') as base:
        data = csv.reader(base, delimiter = ';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            if row[0] == str(uid):
                markup.add(types.KeyboardButton(row[3]))
    markup.add(types.KeyboardButton('Текущая локация', request_location=True))
    markup.add(types.KeyboardButton('На главную'))
    return markup

# def notificationsend():
#     with open('users.csv', 'a', newline='') as base:
#         udata = csv.reader(base, delimiter = ';')
#         for row in udata:
#             with open()


#Переменные для клавиатур и кнопок
   
bot = telebot.TeleBot(config.TOKEN)


mainmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

tomainbutton = types.KeyboardButton('На главную')

mainGeo = types.KeyboardButton('🌍 Локации')
mainDevices = types.KeyboardButton('🖲 Устройства')
helpBut = types.KeyboardButton('Настройки')
notificBut = types.KeyboardButton('Оповещения')
bestButtonEver = types.KeyboardButton('Демонстрация')


mainmarkup.add(mainGeo, mainDevices, helpBut)
mainmarkup.add(bestButtonEver)
geomarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

addGeo = types.KeyboardButton('Добавить локацию')
# deleteGeo = types.KeyboardButton('Удалить локацию')
geomarkup.add(addGeo, tomainbutton)

devicesmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

addDevice = types.KeyboardButton('Добавить устройство')
# delDevice = types.KeyboardButton('Удалить устройство')
devicesmarkup.add(addDevice,tomainbutton)

notificationmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

notificTime = types.KeyboardButton('Время оповещений')
notificationmarkup.add(notificTime, tomainbutton)

settingsmarkup = types.InlineKeyboardMarkup(row_width=2)
item1 = types.InlineKeyboardButton("Ухудшился воздух", callback_data='bad')
item2 = types.InlineKeyboardButton("Исправился воздух", callback_data='good')
item3 = types.InlineKeyboardButton('Отключились станции МосЭкоМониторинга', callback_data='boot')

settingsmarkup.add(item1, item2, item3)

#Технические переменные для обновления информации или добавления
prev_message = ''
location_to_add = ''
prev_message = ''    
device_to_add = ''
device_type = ''
device_key = ''
device_location = ''

#Далее идет прием сообщений и функции по их обработке

@bot.message_handler(commands=['start', 'main'])
def welcome(message):
    global markup
    bot.send_message(message.chat.id, 
                     'Приветствую, друг! Я - бот, который поможет тебе определить загрязненность воздуха в Москве! \n\nИспользуй кнопки, чтобы получить данные о местности',
                     reply_markup = mainmarkup)
    # with open('Moscow.jpg', 'rb') as photo:  
    #     bot.send_photo(message.chat.id, photo)
    adduser(message.from_user.id, message.from_user.username)

# @bot.message_nandler(commands=['pdk'])
# def notification(message):
#     if message.from_user.id == 158011962 or message.from_user.id == 649697634:
        
        
        
@bot.message_handler(content_types=['location'])
def addloc(message):
    global addGeomarkup
    global prev_message
    global location_to_add 
    global device_to_add
    global device_type 
    global device_key 
    global device_location 
    if prev_message == 'Добавить локацию' and location_to_add:
        addgeo(message.from_user.id, location_to_add, message.location.latitude, message.location.longitude)
        bot.send_message(message.chat.id, 'Ваша локация успешно добавлена!')
        prev_message = ''
        location_to_add = ''
    elif prev_message == 'Добавить устройство' and device_type:
        deviceadd(message.from_user.id, 
                  device_to_add, 
                  device_key, 
                  device_type, 
                  message.location.latitude, 
                  message.location.longitude)
        bot.send_message(message.chat.id, 'Ваше устройство успешно добавлено!')
        prev_message = ''
        location_to_add = ''
        prev_message = ''    
        device_to_add = ''
        device_type = ''
        device_key = ''
        device_location = ''
    geodata = {'lat': message.location.latitude, 'lon': message.location.longitude}
    #bot.reply_to(message, 'Вы хотите добавить эту локацию в список ваших локаций?')
    print(geodata, message.from_user.username)
    

@bot.message_handler(content_types=['text'])
def lalala(message):
    global prev_message
    global location_to_add 
    global device_to_add
    global device_type 
    global device_key 
    global device_location 
    #Кнопки главного меню
    if message.text == '🌍 Локации':
        bot.send_message(message.chat.id, 'В этом меню ты можешь добавить или удалить локации. \nТекущие локации: \n\n' + findgeo(message.from_user.id), 
                         reply_markup=geomarkup) 
    elif message.text == '🖲 Устройства':
        bot.send_message(message.chat.id, 'Это меню создано для добавления и управления устройствами. \nВаши устройства:\n\n'+finddevice(message.from_user.id), 
                         reply_markup=devicesmarkup)
    elif message.text == 'Настройки':
        bot.send_message(message.chat.id, '(сейчас всё включено и не отключить)\n\nНастройте, когда вас уведомлять! \n\nОтключение или передача нулевых показателей станций мониторинга часто происходит во время выбросов вредных веществ...\n\nCообщать если в моих местах: ', 
                         reply_markup=settingsmarkup)
    
    #На главную
    elif message.text == 'На главную':
        bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=mainmarkup)
        location_to_add = ''
        device_to_add = ''
        device_type = ''
        device_key = ''
        device_location = ''
    #Демонстрационный костыль
    elif message.text == 'Демонстрация' :
        printgeos(message.from_user.id, message)
        with open('WINDOW.gif.mp4', 'rb') as doc:    
            bot.send_document(message.chat.id, doc)
        
    #Цепочка добавления локации
    elif message.text == 'Добавить локацию':
        prev_message = message.text
        bot.send_message(message.chat.id, 'Как назовем её?')
    elif prev_message == 'Добавить локацию' and not location_to_add:
        bot.send_message(message.chat.id, f'Хорошо, имя локации: \"{message.text}\"\nЕсли хочешь поменять название, напиши его перед отправкой сообщения')
        location_to_add = message.text
        bot.send_message(message.chat.id, 'Теперь отправь локацию в виде геометки')
    
    #Цепочка добавления устройства
    elif message.text == 'Добавить устройство':
        prev_message = 'Добавить устройство'
        bot.send_message(message.chat.id, 
                          f'Процедура добавления IoT устройства требует от куска мяса {message.from_user.username} данных о имени.\n\nКак назовем устройство?')
    elif prev_message == 'Добавить устройство' and not device_to_add and message.text:
         bot.send_message(message.chat.id, 
                          f'Принято, имя устройства: \"{message.text}\"')
         device_to_add = message.text
         bot.send_message(message.chat.id, 
                          'А теперь, кусок мяса, отправь мне HERE device ID, для интеграции своего устройства с платформой')
    elif prev_message == 'Добавить устройство' and not device_key and message.text:
         device_key = message.text
         typemarkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
         typemarkup.add(types.KeyboardButton('Датчик'), types.KeyboardButton('Роборука'),
                        types.KeyboardButton('На главную'))
         bot.send_message(message.chat.id, 
                          'Выбери тип устройства, нажав на клавишу ниже', 
                          reply_markup = typemarkup)
    elif prev_message == 'Добавить устройство' and not device_type and message.text:
         device_type = message.text
         bot.send_message(message.chat.id, 'Привяжите ваше устройство к одной из действующих геолокаций',
                          reply_markup = geosmarkup(message.from_user.id))
    elif prev_message == 'Добавить устройство' and device_type:
            if findgeodata(message.from_user.id, message.text) != 'Ошибка! Нет такой локации!':
                deviceadd(message.from_user.id, 
                          device_to_add, 
                          device_key, 
                          device_type,
                          findgeodata(message.from_user.id, message.text)[0],
                          findgeodata(message.from_user.id, message.text)[1])
                bot.send_message(message.chat.id, f'Ваше устройство \"{device_to_add}\" успешно добавлено', reply_markup = mainmarkup)
                location_to_add = ''
                prev_message = ''    
                device_to_add = ''
                device_type = ''
                device_key = ''
                device_location = ''
            else:
                bot.send_message(message.chat.id, 'Такая локация не найдена. \nПопробуйте добавить её или использовать текущую локацию', reply_markup = mainmarkup)
                location_to_add = ''
                prev_message = ''    
                device_to_add = ''
                device_type = ''
                device_key = ''
                device_location = ''
    #Стандартное сообщение
    else:
        bot.send_message(message.chat.id, 'Не понимаю... Я перевел тебя на главную страницу, используй кнопки.', reply_markup=mainmarkup)
        prev_message = ''
        location_to_add = ''
        prev_message = ''    
        device_to_add = ''
        device_type = ''
        device_key = ''
        device_location = ''
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Если в твоих локациях появятся улучшения, я сообщу!', reply_markup = mainmarkup)
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Если в твоих локациях ситуация ухудшится, я сообщу!', reply_markup = mainmarkup)
            elif call.data == 'boot':
                bot.send_message(call.message.chat.id, 'Если рядом с твоей локацией произойдет отключение станций, я сообщу!', reply_markup = mainmarkup)
    except Exception as e:
        print(repr(e))
                                 

def botwork():
    try:
        bot.polling(none_stop=True)
    except Exception as ex:
        bot.send_message(649697634, f'Bot disabled his work with {ex}. Reboot....')
        botwork()
bot.polling(none_stop=True)