import json, time, re, sys, os, datetime
import importlib
import subprocess
from DatabaseManager import DatabaseManager
#<<<-------Loading external modules dynamically---------->>>
EXTERNAL_MODULES = ['requests']
loaded_modules = {}
for module_name in EXTERNAL_MODULES:
    try:
        loaded_modules[module_name] = importlib.import_module(module_name)
    except ImportError:
        subprocess.check_call(['pip', 'install', module_name])
        # loaded_modules[module_name] = importlib.import_module(module_name)
#<<<---------Objects of dynamically loaded modules------->>>
# requests = loaded_modules['requests']
import requests
#<<<--------PARSE JSON CONFIG FILE------>>>
def parseJson(infile, tofind):
    f = open(infile, 'r')
    file = f.read()
    f.close()
    figures=json.loads(file)
    parsedData = figures[tofind]
    return parsedData
#<<<--------INTERNAL VARIABLES--------->>>
tgbot=parseJson("./config.json", "tgbot")
tgurl="https://api.telegram.org/bot"
BOT_TOKEN=tgbot[0]['bot_token']
if not BOT_TOKEN:
    print("Add bot token in the config.json file")
    exit(1)
if not tgbot[0]['owner_id']:
    print("Add owner_id in the config.json file")
    exit(1)
if not tgbot[0]['admins']:
    print("Add any admin id in config.json file also include the owner_id in this list")
    exit(1)
SEND_MESSAGE='/sendMessage'
GET_UPDATES='/getUpdates'
EDIT_MESSAGE='/editMessageText'
DELETE_MESSAGE='/deleteMessage'
TEXT_MESSAGE='?&text='
#<<<------Configrue mysql databse to write update id and other informations --------->>>
parse_db_data = parseJson('config.json', 'mysql')
db_data = parse_db_data[0]
db = DatabaseManager(**db_data)
if not db.check_database_exists():
    db.create_database()
updateIdTable = 'update_id'
columns = [
    'id BIGINT AUTO_INCREMENT PRIMARY KEY',
    'from_id BIGINT',
    'chat_id BIGINT',
    'message_id BIGINT',
    'message_text LONGTEXT',
    'update_id BIGINT',
]
if not db.check_table_exists(updateIdTable):
    db.create_table(updateIdTable, columns)

class BhutuuTelebot:
    #<<<------UPDATE VERIFICATION -------->>>
    def checkUpdates(self, upId):
        validity = "yes"
        oldUpdateIds = db.get_value(updateIdTable, "update_id")
        if oldUpdateIds is None:
            return validity
        for id in oldUpdateIds:
            if(re.search(str(upId), str(id[0]))):
                validity="no"
            else:
                validity="yes"
        return validity
    #<<<------ADMIN VERIFICATION -------->>>
    def adminVerify(self, adminId):
        owner = tgbot[0]['owner_id']
        admins = tgbot[0]['admins']
        for admin in admins:
            if(str(admin)==str(adminId)):
                return True
            else:
                if(str(owner)==str(adminId)):
                    return True
                else:
                    return False
    def sendMessage(self, chatId, messageId, messageToSend):
        data = {
            'chat_id': int(chatId),
            'parse_mode': 'html',
            'disable_web_page_preview': True,
            'reply_to_message_id': int(messageId),
            'text': str(messageToSend)
        }
        response = requests.post(tgurl+BOT_TOKEN+SEND_MESSAGE, data=data)
        return response
    def editMessage(self, chatId, messageId, newMessage):
        data={
            'chat_id': int(chatId),
            'parse_mode': 'html',
            'disable_web_page_preview': 'true',
            'message_id': int(messageId),
            'text': str(newMessage)
        }
        response=requests.post(tgurl+BOT_TOKEN+EDIT_MESSAGE, data=data)
        return response
    def deleteMessage(self, chat_id, message_id):
        data = {
            'chat_id': int(chat_id),
            'message_id': int(message_id),
        }
        respDel = requests.post(tgurl+BOT_TOKEN+DELETE_MESSAGE, data=data)
    #    print(respDel.text)
        return respDel
    def getUpdates(self):
        data={
            'offset': '-1',
        }
        response = requests.post(tgurl+BOT_TOKEN+GET_UPDATES, data=data)
        return response.json()
    def getUids(self):
        uidraw=db.get_value(updateIdTable, "update_id")
        uid=[]
        for id in uidraw:
            uid.append(id[0])
        return uid
    def saveNewUpdateId(self, fromid, chatid, messageid, messagetext, updateid):
        columns=('from_id','chat_id','message_id','message_text','update_id')
        data=(fromid, chatid, messageid, messagetext, updateid)
        if db.add_data(updateIdTable, columns, data):
            return True
        else:
            return False
    def authfailMessage(self, warn_message, chatId, messageId):
        for i in warn_message.split():
            self.editMessage(str(chatId), messageId,i)
            time.sleep(0.01)
