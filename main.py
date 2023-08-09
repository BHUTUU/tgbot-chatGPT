import openai
import time
import json,re, threading
import BhutuuTelebot
bot=BhutuuTelebot.BhutuuTelebot()
#<<<--------PARSE JSON CONFIG FILE------>>>
def parseJson(infile, tofind):
    f = open(infile, 'r')
    file = f.read()
    f.close()
    figures=json.loads(file)
    parsedData = figures[tofind]
    return parsedData
openaidata = parseJson('config.json', 'tgbot')
if not openaidata[0]['openai_token']:
    print("Add your OpenAI token in config.json file.")
    exit(1)
openaikey=openaidata[0]['openai_token']
openai.api_key = openaikey
listening = True
def chatGptPrompt(question):
    global listening
    listening = False
    while True:
        try:
            response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=question,
            temperature=0.5,
            max_tokens=100,
            n=1,
            stop=None,
            timeout=1
            )
            listening = True
            return response.choices[0].text
        except:
            continue
def helpMenu():
    toHelp="""
=========================
command             usage
--------------------------------------------------
/help       |- for this help menu.
/github    |- to get my github.
/id        |- to get my website.
/mean     |- to get meaning of the provided word.
/sed newMessage   |- edit my message to which its replied.
/dt    |- delete a particular message
/pd    |- to delete all messages from replied message.
search Replace any string in message:
s/wordToReplace/newWord
________________________________"""
    return toHelp
def main():
    while listening is True:
        try:
            updateJson=bot.getUpdates()
        except:
            continue
        updateid = updateJson['result'][0]['update_id']
        try:
            messagetext = updateJson['result'][0]['message']['text']
        except: 
            continue
        try:
            fromusrid = updateJson['result'][0]['message']['from']['username']
        except:
            fromusrid = "{No username}"
        messageid = updateJson['result'][0]['message']['message_id']
        fromid=updateJson['result'][0]['message']['from']['id']
        chatid=updateJson['result'][0]['message']['chat']['id']
        validity=bot.checkUpdates(updateid)
        if validity == "no":
            continue
        try:
            message_id2=updateJson['result'][0]['message']['reply_to_message']['message_id']
            message_got=updateJson['result'][0]['message']['reply_to_message']['text']
        except:
            pass
        bot.saveNewUpdateId(fromid, chatid, messageid, messagetext, updateid)
        cmd=str(messagetext).split()[0]
        if(str(cmd).find("@") != -1):
            pingcmd=cmd.replace("@", " ")
            cmd=pingcmd.split()[0]
        args=re.sub(r'.','',str(messagetext), count=(len(cmd) + 1))

        match cmd:
            case "/chatgpt":
                if not args:
                    bot.sendMessage(chatid, messageid, "/chatgpt your Question here")
                else:
                    response=chatGptPrompt(str(args))
                    bot.sendMessage(chatid, messageid, str(response))
            case "/help":
                        helpmsg=helpMenu()
                        bot.sendMessage(str(chatid), messageid, str(helpmsg))
            case "/github":
                bot.sendMessage(str(chatid), messageid,"https://github.com/BHUTUU")
            case "/website":
                bot.sendMessage(str(chatid), messageid, "bhutuu.github.io")
            case "/ping":
                bot.sendMessage(str(chatid), messageid, "<code>pong!</code>")
            case "/start":
                bot.sendMessage(str(chatid), messageid, "Hi! @"+str(fromusrid)+" . Status: Running..!")
            case "/id":
                bot.sendMessage(str(chatid), messageid, "This chatid's id is: <code>"+str(chatid)+"</code> and your chatid's id is: <code>"+str(fromid)+"</code>")
            case "/sed":
                if bot.adminVerify(fromid):
                    if not args:
                        bot.sendMessage(str(chatid), messageid, "provide the sentance to replace!")
                    else:
                        bot.editMessage(str(chatid), message_id2, str(args))
                else:
                    if not args:
                        bot.sendMessage(str(chatid), messageid, "you are not authotised to use this cmd")
                    else:
                        bot.authfailMessage("hey! you are not allowed to edit any message from me!", str(chatid), message_id2)
                        bot.editMessage(str(chatid), message_id2, str(message_got))
            case "/dt":
                if bot.adminVerify(fromid):
                    try:
                        bot.deleteMessage(chatid, message_id2)
                        bot.deleteMessage(chatid, messageid)
                    except:
                        bot.sendMessage(str(chatid), messageid, "reply to any message which you want to delete!")
                else:
                    bot.sendMessage(str(chatid), messageid, "you are not authotised to use this cmd")
            case "/pd":
                if bot.adminVerify(fromid):
                    try:
                        test = message_id2
                        try:
                            threads = [threading.Thread(target=bot.deleteMessage, args=(chatid,i))
                                    for i in list(range(int(test),int(messageid)+1,1))]
                            for thread in threads:
                                thread.start()
                            for thread in threads:
                                thread.joint()
                        except:
                            pass
                    except:
                        bot.sendMessage(str(chatid), messageid, "reply to any message from where u want to delete the chats!")
                else:
                    bot.sendMessage(str(chatid), messageid, "you are not authotised to use this cmd")

    #<<<-------MESSAGE REACTION------->>>#
        match messagetext.upper():
            case "GOOD MORNING":
                bot.sendMessage(str(chatid), messageid, "Good morning @"+str(fromusrid))
            case "HELLO":
                bot.sendMessage(str(chatid), messageid, "Hello @"+str(fromusrid))
            case "PLEASE HELP":
                bot.sendMessage(str(chatid), messageid, "Just explain your help/need and have patience @"+str(fromusrid))
            case "HELP ME":
                bot.sendMessage(str(chatid), messageid, "Just explain your help/need and have patience @"+str(fromusrid))
    #<<<-----SEARCH AND REPLACE------>>>#
        if (messagetext.find('s/', 0, 2) != -1):
            if (messagetext.find('\/') != -1):
                pref=messagetext.split('/')[1].removesuffix('\\')
                oldStr=pref+'/'+messagetext.split('/')[2]
                new1=messagetext.split('/')[3]
                if(new1.find('\\') != -1):
                    newStr=new1.split('\\')[0]+'/'
                else:
                    newStr=new1
                try:
                    newMess=message_got.replace(oldStr, newStr)
                    bot.sendMessage(str(chatid), message_id2, str(newMess))
                except:
                    pass
            else:
                text1 = messagetext.split('/')[1]
                text2 = messagetext.split('/')[2]
                try:
                    newMess = message_got.replace(text1, text2)
                    bot.sendMessage(str(chatid), message_id2, str(newMess))
                except:
                    pass



if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            continue