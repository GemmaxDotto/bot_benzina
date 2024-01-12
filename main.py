import requests
from time import sleep
from bot import Bot
from db import Database
import json

db = Database("localhost", "root", "", "db_Gbenz")

ENDPOINT = f'https://api.telegram.org/bot/6855019928:AAEwiBxbXooXcCHReh2NvEmgMXma7bjwpUI/'
bot = Bot("6855019928:AAEwiBxbXooXcCHReh2NvEmgMXma7bjwpUI")

last_update_id = 0

user_info = ["","","","","",""]  # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm

def main():
    print("STARTING...")

    text = ""
    find_executed = False
    start_executed = False
    
    while True:
        global last_update_id
        
        text=""
        
        response = bot.get_updates(last_update_id)
        print(response)
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1
            try:
                text = response['result'][0]['message']['text']
            except:
                text = ""
            user_info[0] = response['result'][0]['message']['chat']['id']
            user_info[1] = response['result'][0]['message']['from']['id']
            
        if text == '/start' and not start_executed:
            startBotChat()
            start_executed = True
        elif text == '/modify' and start_executed:
            ChangeInfo()
        elif text == '/find' and start_executed and not find_executed:
            findGasolineStat()
            find_executed = True
            
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1

        sleep(5)


def startBotChat():
    global last_update_id
    global user_info
    query = "SELECT ChatID,UserID FROM user WHERE ChatID = " + str(user_info[0])
    result = db.esegui_query(query)

    if(len(result)==0):
        bot.send_message(user_info[0], 'HI IM YOUR BOT FOR GAS STATION! TYPE /find AFTER ENTERING YOUR DATA TO FIND THE BEST GAS STATION FOR YOU')
        getInfo()
        
        query = "INSERT INTO user (ChatID,UserID, nome, tipocarburante, capacita, maxkm) VALUES ("+str(user_info[0]) +", " +  str(user_info[1]) + ", '" + str(user_info[2]) + "', '" + str(user_info[3]) + "', " + str(user_info[4]) + ", " + str(user_info[5]) + ")"
        db.esegui_query(query)
    else:
        bot.send_message(user_info[0], 'HI IM YOUR BOT FOR GAS STATION! TYPE /modify TO MODIFY YOUR DATA /find TO FIND THE BEST GAS STATION FOR YOU')
        userid = result[0][1]
        query = "SELECT * FROM user WHERE UserID = " + str(userid)
        result = db.esegui_query(query) # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm
        print (result)
        user_info[1] = result[0][0]
        user_info[2] = result[0][1]
        user_info[3] = result[0][2]
        user_info[4] = result[0][3]
        user_info[5] = result[0][4]
        bot.send_message(user_info[0], 'Welcome Back, ' + str(user_info[2]))
        print(user_info)   

def ChangeInfo():
    global user_info
    global last_update_id
    
    getInfo()
    
    query = "UPDATE user SET Nome = '" + str(user_info[2]) + "', TipoCarburante = '" + str(user_info[3]) + "', Capacita = " + str(user_info[4]) + ", MaxKM = " + str(user_info[5]) + " WHERE ChatID = " + str(user_info[1])
    db.esegui_query(query)
    


def findGasolineStat():
    global user_info
    global last_update_id
    
    bot.send_message(user_info[0], 'Insert your location: ')

    data = getResponse()
    Lat = data['result'][0]['message']['location']['latitude']
    Lon = data['result'][0]['message']['location']['longitude']

    bot.send_message(user_info[0], 'Nearest gas station or cheapest gas station?')
    sendKeyboard(user_info[0], ['nearest', 'cheapest'])
    data = getResponse()
    typeStation = data['result'][0]['message']['text'].lower()
    
    bot.send_message(user_info[0], 'How much fuel do you have?')
    sendKeyboard(user_info[0], ['only 1/4', 'half', '3/4', 'full'])
    data = getResponse()
    quantita = data['result'][0]['message']['text']
    
    if typeStation == 'nearest':
        query = "SELECT * FROM anagrafica ORDER BY SQRT(POW(Latitudine - " + str(Lat) + ", 2) + POW(Longitudine - " + str(Lon) + ", 2)) ASC LIMIT 10"
        result = db.esegui_query(query)
        bot.send_message(user_info[0], 'The nearest gas stations are: ')
        for i in range(9):
            bot.send_message(user_info[0], '/n/r' + str(result[i][4]) + ' ' + str(result[i][5]) + ', ' + str(result[i][6]) + ', ' + str(result[i][7]) + ', ' + str(result[i][8]))
            
    elif typeStation == 'cheapest':
        #TODO: calcolo del prezzo migliore
        query = f"SELECT a.nome, a.indirizzo, a.comune, a.latitudine, a.longitudine, p.TipoCarburante, p.prezzo FROM anagrafica as a JOIN prezzi as p ON a.ID = p.IDImpianto WHERE p.TipoCarburante = '"+ user_info[3] + "' AND p.isSelf = 1 ORDER BY SQRT(POW(a.Latitudine - " + str(Lat) + ", 2) + POW(a.Longitudine - " + str(Lon) + ", 2)) ASC ";
        result = db.esegui_query(query)

        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        }        
        bestPrezzo = result[0][6]
        indexBestPrezzo = 0
        count = 0
        api_key = open("./docs/token_directions.txt", "r").read()
        for i in range(len(result)):
            if result[i][6] < bestPrezzo:
                latStation = result[i][3]
                lonStation = result[i][4]
                bestPrezzo = result[i][6]
                indexBestPrezzo = i
                count+=1

        
        
        bot.send_message(user_info[0], "Station Name: " + str(result[indexBestPrezzo][0]) + "\nAddress: " + str(result[indexBestPrezzo][1]) + "\nCity: " + str(result[indexBestPrezzo][2]) + "\nPrice: " + str(result[indexBestPrezzo][6]) + "\nFuel Type: " + str(result[indexBestPrezzo][5]))
    
        
def getInfo():
    global user_info
    global last_update_id
    
    bot.send_message(user_info[0], 'I need some data to work, please answer the following questions:')
    bot.send_message(user_info[0], 'Insert your name: ')
    data = getResponse()
    user_info[2] = data['result'][0]['message']['text']
    
    bot.send_message(user_info[0], 'Insert the type of fuel you use(Benzina/Metano/GPL/Gasolio/Blue Super/Blue Diesel...): ')
    data = getResponse()
    user_info[3] = data['result'][0]['message']['text'].tolower()
    
    bot.send_message(user_info[0], 'Insert the capacity of your tank: ')
    data = getResponse()
    user_info[4] = data['result'][0]['message']['text']
    
    bot.send_message(user_info[0], 'Insert the maximum distance you would travel: ')
    data = getResponse()
    user_info[5] = data['result'][0]['message']['text']
    bot.send_message(user_info[0], 'Thank you! Now you can type /find to find the best gas station for you!')

def loadPrices():
    
    db.esegui_query("DELETE FROM prezzi")
    #TODO: aggiornare i prezzi
    
    prezzi = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
    r = requests.get(prezzi)
    with open("./docs/Csv/prezzi.csv", "wb") as f:
        f.write(r.content)
    prezzi = r.content.decode("utf-8").split("\n")
    prezzi.pop(0)
    prezzi.pop(0)
    prezzi.pop(len(prezzi)-1)
    
    for i in range(len(prezzi)):
        prezzi[i] = prezzi[i].replace('NULL','').replace("'","").split(";")
        query = "INSERT INTO prezzi (IDImpianto, TipoCarburante, Prezzo, IsSelf, DtComu) VALUES (" + str(prezzi[i][0]) + ", '" + str(prezzi[i][1]) + "', " + str(prezzi[i][2]) + ", " + str(prezzi[i][3]) + ", '" + str(prezzi[i][4]) + "')"
        db.esegui_query(query)
    
    print("Prices loaded!")
    
def getResponse():
    global last_update_id
    while True:
        sleep(5)
        data = bot.get_updates(last_update_id)
        if len(data['result']) > 0:
            last_update_id = last_update_id + 1
            return data


def sendKeyboard(chat_id, options):
        url = f"{ENDPOINT}sendMessage"
        keyboard = {
            "keyboard": [[{"text": option} for option in options]],
            "resize_keyboard": True, 
            "one_time_keyboard": True
        }
        payload = {
            "chat_id": chat_id,
            "text": "Seleziona un opzione",
            "reply_markup": json.dumps(keyboard)
        }
        requests.post(url, data=payload)


if __name__ == '__main__':
    main()