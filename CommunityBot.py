import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import datetime
import pickle
import os
from steem import Steem
from steem.converter import Converter
from steem.post import Post
import csv
import sqlite3
import math
import locale
from pytz import timezone
from steem.account import Account
import secrets
import logging
import logging.handlers as handlers


locale.setlocale(locale.LC_ALL,'')

logger = logging.getLogger("DachBot")
logger.setLevel(logging.INFO)

# Logging Format definitions

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler = logging.FileHandler("Dachbot.log")
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


db = sqlite3.connect("articles.db", detect_types=sqlite3.PARSE_DECLTYPES) # initializing the db that will hold the articles to be voted

c  = db.cursor()
# initial creation of the table for the articles, uncomment if necessary
#c.execute(''' CREATE TABLE articles
#              (kurator text, permlink text, votes real, voted text, title text, author text )''') 
#c.execute(''' CREATE TABLE meetup 
#              (planer text, ort text, permlink text, datum timestamp)''') 
#c.execute(''' CREATE TABLE users
#              (discordid text, discordname text, steemname text, token text, status text, datum timestamp)''') 
#c.execute(''' Alter table articles add column voted text''')
#c.execute(''' Alter table articles add column autor text''')
#c.execute(''' Alter table users add column has_voted text''')
#c.execute (''' Drop Table articles''')
#db.commit()

Client = discord.Client()
client = commands.Bot(command_prefix = "?") # currently not used
#fname = "save.txt" # Define the filename for the registered users data


#if os.path.isfile(fname): # routine to either open an existing file or create a new empty one
#    liste = pickle.load(open(fname,"rb")) 
#else: 
#    print ("File %s does not exist, creating a new one!" % fname)
#    liste={}




steemPostingKey = os.environ.get('steemPostingKey')
s = Steem(wif=steemPostingKey)
    
@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")
    logger.info("Discord Bot is online and connected to Discord")

@client.event
async def printhelp(message): #function to print out help and usage methods
        embed = discord.Embed(title="D-A-CH Support Help", description="Befehle und Hilfe", color=0x00ff00)        #embed.add_field(name="§register", value="Benutzung: §register gefolgt vom Steemnamen eingeben um die Verbindung DiscordID und SteemID zu schaffen", inline=False)
        embed.add_field(name="?status", value="Benutzung: ?status gibt die registrierten Benutzer und den Status des SteemBots zurück", inline=False)
        embed.add_field(name="?help oder ?hilfe", value="Benutzung: ?help gibt diese Hilfe zurück", inline=False)
        embed.add_field(name="?nextmeetup", value="Benutzung: ?nextmeetup gibt die nächsten Meetups mit allen Infos aus", inline=False)
        embed.add_field(name="?info", value="Benutzung: ?info + steemname gibt Infos zum Steem Account aus, Beispiel ?info dach-support", inline=False)
        embed.add_field(name="?longinfo", value="Benutzung: ?longinfo + steemname gibt VIELE Infos zum Steem Account aus", inline=False)
        embed.add_field(name="?register", value="Benutzung: ?register + steemname startet die Registrierung mit dem D-A-CH Support Bot. Bitte den Hinweisen in der PN folgen!", inline=False)
        embed.add_field(name="?upvote", value="Benutzung: ?upvote + linkzumartikel gibt die Stimme für den Artikel ab, das wird benutzt um den D-A-CH Bot voten zu lassen", inline=False)
        embed.add_field(name="?showarticles", value="Benutzung: ?showarticles zeigt eine Liste der bisher gevoteten Artikel an", inline=False)

        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)

@client.event
async def on_message(message):
    command_run=0
    if message.content.upper().startswith("?REGISTER"): # code to start the cross plattform registration process
        userID = message.author.id
        if (len(message.content.strip()) > 9):
            args = message.content.split(" ")
            if "@" in args[1]:
                args[1] = args[1].replace("@","")
                args[1] = args[1].lower()
                
            #check if either the discord or the steem name is already registerd
            c.execute("SELECT * FROM users where discordname = ? OR steemname = ?", (message.author.name,args[1]))
            #print("fetchall:")
            result = c.fetchall() 
            if len(result)==0:
                logger.info("Registrierung gestartet für User %s ")
                token = secrets.token_hex(32)
                #print (token)
                today = datetime.datetime.today()
                await client.send_message(message.author, "Registrierung von Discord ID <@%s> auf Steem ID @%s eingeleitet!\nToken wurde generiert!\nBitte schicke 0.001 SBD oder Steem an @dach-support mit untenstehender Memo um die Registrierung abzuschliessen!\nMemo: %s" % (userID,args[1],token) )
                datarow=(userID,message.author.name,args[1],token,"pending steem",today,"No")
                c.execute ("INSERT INTO users VALUES(?,?,?,?,?,?,?)", datarow )
                db.commit()
                command_run = 1
                logger.info("Registrierung gestartet für User %s mit Token %s" % (message.author.name,token))

            else: 
                await client.send_message(message.author,"Sorry der Discordname oder der Steemname werden bereits in einer Registrierung verwendet.\nBitte nimm Kontakt mit jedigeiss auf um die Situation zu klären.")
                command_run = 1
                logger.info("Doppelte Registrierung versucht von User %s " % (message.author.name))
#            else:    
#                command_run = 1
#                if userID not in liste and args[1] not in liste :    
#                    liste[userID] = args[1] # append the userid and the steem handle to the dict
#                    await client.send_message(message.channel, "Für die Discord ID <@%s> wurde die Steem ID %s registriert !" % (userID,liste[userID]) )
#                    f = open(fname,"wb") #write the dict into a file
#                    pickle.dump(liste,f)
#                    f.close()
#
#                else:
#                    await client.send_message(message.channel, "Die Discord ID <@%s> ist bereits mit der Steem ID %s verknüpft!" % (userID,liste[userID]) )
#                    print (liste)           
#                          
#    if message.content.upper().startswith("?KILLALLUSERS"): # Function to empty the table, only admins can do that, handle with care
#        executed = 0
#        for role in message.author.roles:
#            if role.name == "Admin":
#                c.execute("DELETE FROM users")
#                db.commit()
#                executed = 1
#                command_run = 1
#                await client.send_message(message.channel, "Tabelle users wurde geleert!" )
#        if executed == 0:
#            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
#            command_run = 1
    
    if message.content.upper().startswith("?ADDUSER"): # Adduser manually to the users table
        executed = 0
        if (len(message.content.strip()) > 8):
            args = message.content.split(" ")
        for role in message.author.roles:
            executed = 1
            if role.name == "Admin":
                c.execute("SELECT * FROM users where discordname = ? OR steemname = ?", (args[2],args[3]))
                result = c.fetchall()
                if len(result) == 0:
                    userID = args[1]
                    discordname = args[2]
                    steemname = args[3]
                    token = args[4]
                    today = datetime.datetime.today()
                    datarow=(userID,discordname,steemname,token,"registered",today,"No")
                    c.execute ("INSERT INTO users VALUES(?,?,?,?,?,?,?)", datarow )
                    db.commit()
                    await client.send_message(message.channel, "User %s wurde gespeichert!" % steemname )
                    logger.info("Admin %s hat manuell User %s hinzugefügt" % (message.author.name,discordname))
                    command_run = 1
                else:
                    await client.send_message(message.channel, "User existiert schon in der DB!" )
                    logger.info("Adduser von Admin %s ist fehlgeschlagen - User existiert schon in der DB %s" % (message.author.name,discordname))
                    command_run = 1
                        
        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )    
            logger.info("Adduser von %s ist fehlgeschlagen - keine Adminrechte" % (message.author.name))
                    
    
    
    if message.content.upper().startswith("?KILLUSER"): # Function to delete a single line, either by the discord handle or the steem handle
        executed = 0   
        for role in message.author.roles:
            if role.name == "Admin":
                if (len(message.content.strip()) > 9):
                    args = message.content.split(" ")
                    if "@" in args[1]:
                        args[1] = args[1].replace("@","")
                    c.execute("SELECT * FROM users where discordname = ? OR steemname = ?", (args[1],args[1]))
                    result = c.fetchall() 
                    if len(result)>0:
                        c.execute("DELETE FROM users where steemname = ? OR discordname = ?",(args[1],args[1]))
                        db.commit()
                        executed = 1
                        command_run = 1
                        await client.send_message(message.channel, "User %s wurde gelöscht!" %args[1] )
                        logger.info("Killuser von Admin %s ausgeführt User %s gelöscht" % (message.author.name,args[1]))
                    
                    if len(result)==0:
                        await client.send_message(message.channel, "Kein User %s gefunden!" %args[1] )
                        executed = 1
        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
            logger.info("Killuser von %s ist fehlgeschlagen - keine Adminrechte" % (message.author.name))

            command_run = 1
            
    if message.content.upper().startswith("?SHOWUSERS"): # shows all users and their status in the registration process
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                if (len(message.content.strip()) > 11):
                    args = message.content.split(" ")
                    if args[1] == "all":
                        c.execute("SELECT * FROM users")
                    else:
                        users = str(args[1])
                        c.execute("SELECT * FROM users where steemname = ?", (users,))
                
                    result =c.fetchall()
                    for r in result:
                        await client.send_message(message.channel, "DiscordID: %s, DName: %s, SteemName: %s, Status: %s Voted: %s" % (r[0],r[1],r[2],r[4],r[6] )) 
                    command_run = 1    
                    executed = 1
                    logger.info("Showusers von %s ist ausgeführt - Anzeige von %s" % (message.author.name,args[1]))

                if message.content.upper() =="?SHOWUSERS":
                     c.execute("SELECT count(status) FROM users where status = ?", ("registered",))
                     result=c.fetchone()
                   
                     await client.send_message(message.channel, "%s registrierte Benutzer" % (result)) 
                     c.execute("SELECT count(status) FROM users where status = ?", ("pending steem",))
                     result=c.fetchone()
                     await client.send_message(message.channel, "%s Benutzer im Status pending steem" % (result)) 
                     logger.info("Showuser Übersicht ausgeführt von %s" % (message.author.name))
                     command_run = 1    
                     executed = 1


        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )

#    if message.content.upper().startswith("?BACK"): # function to set back the status of the registrations to pendings steem, merely for test purposes
#        executed = 0
#        for role in message.author.roles:
#            if role.name == "Admin":
#                c.execute("UPDATE users set STATUS = ? where steemname = ?", ("pending steem","jedigeiss",))
#                db.commit()
#                await client.send_message(message.channel, "jedigeiss zurückgesetzt" )
#                command_run = 1    
#                executed = 1
#                logger.info("Zurpcksetzen des Accounts von" % (message.author.name))
#
#        if executed == 0:
#            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )

            
    if message.content.upper().startswith("?CHECKREG"): # Function to manually check incoming registrations, needs to be automatized in next version
            executed = 0
            for role in message.author.roles:
                if role.name == "Admin":
                    account = Account("dach-support")
                    count = 0
                    c.execute("SELECT * FROM users WHERE status = ?", ("pending steem",))
                    result = c.fetchall()
                    if len(result)==0:
                        await client.send_message(message.channel, "Keine Registrierungen zum Überprüfen vorhanden!")
                    elif len(result)>0:
                        found = 0
                        for r in result:
                            discorduser= r[1]
                            reguser = r[2]
                            regtoken =r[3] 
                            #print (reguser)
                            
                            
                            for x in account.history(filter_by=["transfer"]):
                                steemuser = x["from"]
                                steemtoken = x["memo"]
                                if reguser == steemuser and regtoken == steemtoken:
                                    await client.send_message(message.channel, "Token Match!\nDiscordUser: %s ist jetzt mit Steemname: %s registriert" %(discorduser, steemuser))
                                    c.execute("UPDATE users SET status = ? where discordname = ?", ("registered",discorduser,))
                                    u=discord.User(id=r[0])
                                    await client.send_message(u, "Registrierung mit dem D-A-CH Support Bot abgeschlossen!\nDiscordUser: %s ist jetzt mit Steemname: %s registriert" %(discorduser, steemuser))
                                    found = 1
                                    db.commit()
                                    logger.info("Checkreg von %s ist ausgeführt - User %s registriert" % (message.author.name,discorduser))

                                #print (steemuser)
                            #print(x)
                        #await client.send_message(message.channel, "folgende infos vorhanden" % str(count))
                    if found == 0:
                        await client.send_message(message.channel, "Keine passenden Token in den eingehenden Transaktionen gefunden!")
                        logger.info("Checkreg von %s ist ausgeführt - keine passenden Tokens" % (message.author.name))

                    executed = 1
                    command_run =1
            if executed == 0:
                await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
                logger.info("Checkreg von %s ist fehlgeschlagen - keine Adminrechte" % (message.author.name))

               
    if message.content.upper().startswith("?STATUS"): # code for the status command, will list users and basic data about the bot
        account_name="dach-support"
        acc_data = s.get_account(account_name)
        votingpower=float(acc_data["voting_power"])
        votingpower = votingpower / 100
        votetime = acc_data["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
        votetime = votetime.replace("T", " ")
        votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.utcnow()
        time_vp = now - votetime
        percentup = (int(((time_vp.total_seconds())/60))*0.0139)
        if ((votingpower+percentup)>100): # capping the vote percentage at 100 
            resulting_vp = 100
        else:
            resulting_vp = (votingpower+percentup)
        embed = discord.Embed(title="D-A-CH Support Status", description="Alive and kickin!", color=0x00ff00)
        #embed.add_field(name="Angemeldete User", value=liste, inline=False)
        embed.add_field(name="Votingpower", value="%.2f Prozent" % resulting_vp, inline=False)
        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)
        logger.info("Status von %s wurde ausgeführt" % (message.author.name))

        command_run = 1
        
        
    if message.content.upper().startswith("?HELP") or message.content.upper().startswith("§HILFE") : # code for the help function
        await printhelp(message)
        logger.info("Help von %s ist ausgeführt" % (message.author.name))

        command_run = 1

    if message.content.upper().startswith("?INFO"): # short info about steemusers
        args = message.content.split(" ")
        try:
            account_name = str(args[1]).lower()
            try:
                today = datetime.datetime.today()
                sbd = s.get_account(account_name)
                pos1 = (str(sbd["json_metadata"]))
                posanf = pos1.find("profile_image")
                if posanf == -1:
                    picurl="https://coinjournal.net/wp-content/uploads/2016/06/steemit-logo-blockchain-social-media-platform-696x364.png"
                else:
                    posanf = posanf +16
                    posend = pos1.find("\"",posanf)
                    picurl = (pos1[posanf:posend]) 
                    
                steemlink = "https://steemit.com/@"+ account_name
                cachedlink=("https://steemitimages.com/u/%s/avatar" % account_name)
                #print (sbd)
                #print (cachedlink)
                #profilepic = "https://img.busy.org/@" + account_name
                votingpower=float(sbd["voting_power"])
                votingpower = votingpower / 100
                SPown = sbd["vesting_shares"].replace("VESTS","") ## start of calculation of most recent Steempower value
                SPout = sbd["delegated_vesting_shares"].replace("VESTS","")
                SPout = float(SPout)
                SPown = float(SPown)
                SPin = sbd["received_vesting_shares"].replace("VESTS","")
                SPin = float(SPin)
                conv=Converter()
                steempower = conv.vests_to_sp(SPown)
                steempower_out = conv.vests_to_sp(SPout)
                steempower_in = conv.vests_to_sp(SPin)
                resulting_steempower = steempower - steempower_out + steempower_in
                #locales formating
                steempower = locale.format("%.2f",float(steempower), grouping = True)
                steempower_out = locale.format("%.2f",float(steempower_out), grouping = True)
                steempower_in = locale.format("%.2f",float(steempower_in), grouping = True)
                resulting_steempower = locale.format("%.2f",float(resulting_steempower), grouping = True)
                
                votetime = sbd["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
                votetime = votetime.replace("T", " ")
                votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
                created = sbd["created"]
                created = created.replace("T", " ")
                created = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                since = today - created
                rep = sbd["reputation"] # startpoint of the rep calculation out of the raw reputation
                rep = float(rep)
                if rep == 0: # special situation for the new accounts or the ones that never have received a single vote
                    rep = 25
                else:
                    neg = rep < 0
                    rep = abs(rep)
                    rep = math.log10(rep)
                    rep = max(rep - 9, 0)
                    rep = (-1 if neg else 1) * rep
                    rep = rep * 9 + 25
                    rep = round(rep, 2)
                    rep = locale.format("%.2f",rep, grouping = False) #locale format
                    
                now = datetime.datetime.utcnow() # start of the calculation of the current voting power
                time_vp = now - votetime
                percentup = (int((time_vp.total_seconds())/60)*0.0139)
                if ((votingpower+percentup)>100): # capping the vote percentage at 100 
                    resulting_vp = 100
                else:
                    resulting_vp = (votingpower+percentup)
                resulting_vp = locale.format("%.2f",resulting_vp)
                
                time_comment = sbd["last_post"] # start of caluclation of last activity information
                time_comment = time_comment.replace("T", " ")
                time_comment = datetime.datetime.strptime(time_comment, "%Y-%m-%d %H:%M:%S")
                time_post = sbd["last_root_post"] 
                time_post = time_post.replace("T", " ")
                time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
                latestactivity = max((votetime,time_comment,time_post))
                latestactivity = latestactivity.replace(tzinfo=timezone('UTC'))
                latestactivity_cet = latestactivity.astimezone(timezone('Europe/Berlin')) 
                
                # building the embed to broadcast via discor
                embed = discord.Embed(title="Short Account Information", description="[%s](%s)"% (account_name,steemlink), color=0x00ff00)
                embed.add_field(name="Steem Power", value="%s SP" % resulting_steempower)
                embed.add_field(name="Votingpower", value="%s Prozent" % resulting_vp)
                embed.add_field(name="Angemeldet seit", value="%s, %s Tage" % (datetime.datetime.strftime(created,"%d.%m.%Y"),since.days))
                embed.add_field(name="Reputation", value=rep)
                embed.add_field(name="Letzte Aktion auf Steem", value=datetime.datetime.strftime(latestactivity_cet,"%d.%m.%Y %H:%M"))
                
                embed.set_thumbnail(url=picurl)
                embed.timestamp=datetime.datetime.utcnow()
                embed.set_footer(text="frisch von der Blockchain")
                await client.send_message(message.channel, embed=embed) # send the built message
                command_run = 1
                logger.info("Infoanfrage von %s für Infos über %s ausgeführt" % (message.author.name,account_name))

            except TypeError as err:
                await client.send_message(message.channel, "Fehler - kein SteemAccount mit dem Namen %s gefunden" % account_name)
                print (err)
                command_run = 1
                logger.info("Infoanfrage von %s für %s ist fehlgeschlagen - keine User gefunden : %s" % (message.author.name,account_name,err))

        except IndexError as err:
            await client.send_message(message.channel, "Fehler - bitte Steemnamen nach §info eingeben")
            print (err)
            command_run = 1
            logger.info("Infoanfrage von %s ist fehlgeschlagen - falscher Index %s" % (message.author.name,err))

            
            
    if message.content.upper().startswith("?LONGINFO"): # long version of the info about steemusers
        args = message.content.split(" ")
        try:
            account_name = str(args[1]).lower()
            try:
                today = datetime.datetime.today()
                sbd = s.get_account(account_name)
                #print(sbd)
                pos1 = (str(sbd["json_metadata"]))
                posanf = pos1.find("profile_image")
                if posanf == -1:
                    picurl="https://coinjournal.net/wp-content/uploads/2016/06/steemit-logo-blockchain-social-media-platform-696x364.png"
                else:
                    posanf = posanf +16
                    posend = pos1.find("\"",posanf)
                    picurl = (pos1[posanf:posend]) 
                    
                steemlink = "https://steemit.com/@"+ account_name
                #cachedlink=("https://steemitimages.com/u/%s/avatar" % account_name)
                #print (sbd)
                #print (cachedlink)
                #profilepic = "https://img.busy.org/@" + account_name
                votingpower=float(sbd["voting_power"])
                votingpower = votingpower / 100
                SPown = sbd["vesting_shares"].replace("VESTS","") ## start of calculation of most recent Steempower value
                SPout = sbd["delegated_vesting_shares"].replace("VESTS","")
                SPout = float(SPout)
                SPown = float(SPown)
                SPin = sbd["received_vesting_shares"].replace("VESTS","")
                SPin = float(SPin)
                #rank calc
                if SPown >= 1000000000:
                    rank = "Wal"
                elif SPown >=100000000:
                    rank = "Orca"
                elif SPown >=10000000:
                    rank = "Delphin"
                elif SPown >=1000000:
                    rank = "Minnow"
                else:
                    rank = "Plankton"
                # converter action to get STEEMPOWER insteaf of vests    
                conv=Converter()
                steempower = conv.vests_to_sp(SPown)
                steempower_out = conv.vests_to_sp(SPout)
                steempower_in = conv.vests_to_sp(SPin)
                resulting_steempower = steempower - steempower_out + steempower_in
                #locales formating
                steempower = locale.format("%.2f",float(steempower), grouping = True)
                steempower_out = locale.format("%.2f",float(steempower_out), grouping = True)
                steempower_in = locale.format("%.2f",float(steempower_in), grouping = True)
                resulting_steempower = locale.format("%.2f",float(resulting_steempower), grouping = True)
                SPown = locale.format("%.2f",float(SPown), grouping = True)
                
                noposts = sbd["post_count"] # total number of posts
                votetime = sbd["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
                votetime = votetime.replace("T", " ")
                votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
                created = sbd["created"]
                created = created.replace("T", " ")
                created = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                since = today - created
                rep = sbd["reputation"] # startpoint of the rep calculation out of the raw reputation
                rep = float(rep)
                if rep == 0: # special situation for the new accounts or the ones that never have received a single vote
                    rep = 25
                else:
                    neg = rep < 0
                    rep = abs(rep)
                    rep = math.log10(rep)
                    rep = max(rep - 9, 0)
                    rep = (-1 if neg else 1) * rep
                    rep = rep * 9 + 25
                    rep = round(rep, 2)
                    rep = locale.format("%.2f",rep, grouping = False) #locale format
                    
                now = datetime.datetime.utcnow() # start of the calculation of the current voting power
                time_vp = now - votetime
                percentup = (int((time_vp.total_seconds())/60)*0.0139)
                if ((votingpower+percentup)>100): # capping the vote percentage at 100 
                    resulting_vp = 100
                else:
                    resulting_vp = (votingpower+percentup)
                resulting_vp = locale.format("%.2f",resulting_vp)
                
                time_comment = sbd["last_post"] # start of caluclation of last activity information
                time_comment = time_comment.replace("T", " ")
                time_comment = datetime.datetime.strptime(time_comment, "%Y-%m-%d %H:%M:%S")
                time_post = sbd["last_root_post"] 
                time_post = time_post.replace("T", " ")
                time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
                latestactivity = max((votetime,time_comment,time_post))
                latestactivity = latestactivity.replace(tzinfo=timezone('UTC'))
                latestactivity_cet = latestactivity.astimezone(timezone('Europe/Berlin')) 
                #building and localizing the amount of steem and savings
                amount_steem = (sbd["balance"].replace(" STEEM",""))
                amount_steem =  locale.format("%.2f",float(amount_steem), grouping = True)
                amount_steem_savings = (sbd["savings_balance"].replace(" STEEM",""))
                amount_steem_savings = locale.format("%.2f",float(amount_steem_savings), grouping = True)
                #building and localizing the amount of sbd and savings
                amount_sbd = (sbd["sbd_balance"].replace(" SBD",""))
                amount_sbd =  locale.format("%.2f",float(amount_sbd), grouping = True)
                amount_sbd_savings = (sbd["savings_sbd_balance"].replace(" SBD",""))
                amount_sbd_savings = locale.format("%.2f",float(amount_sbd_savings),grouping = True)
                
                
                
                # building the embed to broadcast via discor
                embed = discord.Embed(title="Account Information", description="[%s](%s)"% (account_name,steemlink), color=0x00ff00)
                embed.add_field(name="Steem Power", value="%s SP" % resulting_steempower)
                embed.add_field(name="Eigene SP", value="%s SP" % steempower)
                embed.add_field(name="Delegierte SP", value="%s SP" % steempower_out )
                embed.add_field(name="Erhaltene SP", value="%s SP" % steempower_in )
                embed.add_field(name="Votingpower", value="%s Prozent" % resulting_vp)
                embed.add_field(name="Kontostand Steem (Save)", value="%s (%s) STEEM" % (amount_steem,amount_steem_savings))
                embed.add_field(name="Kontostand SBD (Save)", value="%s (%s) SBD"% (amount_sbd,amount_sbd_savings))
                embed.add_field(name="Angemeldet seit", value="%s, %s Tage" % (datetime.datetime.strftime(created,"%d.%m.%Y"),since.days))
                embed.add_field(name="Reputation", value=rep)
                embed.add_field(name="Rang",value=rank)
                embed.add_field(name="MVests", value="%s" % SPown)
                embed.add_field(name="Anzahl Posts", value=noposts)
                embed.add_field(name="Letzte Aktion auf Steem", value=datetime.datetime.strftime(latestactivity_cet,"%d.%m.%Y %H:%M"))
                
                embed.set_thumbnail(url=picurl)
                embed.timestamp=datetime.datetime.utcnow()
                embed.set_footer(text="frisch von der Blockchain")
                await client.send_message(message.channel, embed=embed) # send the built message
                command_run = 1
                logger.info("Long-Infoanfrage von %s für Infos über %s ausgeführt" % (message.author.name,account_name))

            except TypeError as err:
                await client.send_message(message.channel, "Fehler - kein SteemAccount mit dem Namen %s gefunden" % account_name)
                print (err)
                command_run = 1
                logger.info("Long-Infoanfrage von %s für %s ist fehlgeschlagen - keine User gefunden : %s" % (message.author.name,account_name,err))
                
        except IndexError as err:
            await client.send_message(message.channel, "Fehler - bitte Steemnamen nach §info eingeben")
            print (err)
            command_run = 1
            logger.info("Long-Infoanfrage von %s ist fehlgeschlagen - falscher Index %s" % (message.author.name,err))
        
    
    if message.content.upper().startswith("?UPVOTE"): # code for the upvote command, writes the article and the author into a file to be used by the vote bot
        if (len(message.content.strip()) > 7) and message.content[7] == " ":
            args = message.content.split(" ")
            pos1 = args[1].find("@")
            check = 0
            if pos1 <= 0:
                await client.send_message(message.channel, "Fehler - Bitte den kompletten Link hinter §upvote einfügen, beginnend mit http...")
                logger.info("Upvote von %s gescheitert - Link nicht komplett" % (message.author.name))

                check = check +1
            else:
                pos2 = args[1].find("/",pos1)
                steem_name = (args[1][pos1+1:pos2])
                length = len(args[1])
                article = Post(args[1][pos1:length])
               
                elapsed = Post.time_elapsed(article)
                if elapsed >= datetime.timedelta(days=5):
                    await client.send_message(message.channel, "Fehler - Leider ist der Post älter als 5 Tage")
                    logger.info("Upvote von %s gescheitert - Post älter als 5 Tage %s" % (message.author.name, args[1][pos1:length]))
                    check = check +1
                    command_run = 1
                if article.is_main_post() is False:
                    await client.send_message(message.channel, "Fehler - Kommentare können nicht vorgeschlagen werden")
                    logger.info("Upvote von %s gescheitert - Artikel kein root Post %s" % (message.author.name,args[1][pos1:length]))

                    check = check +1
                    command_run = 1
                #await client.send_message(message.channel, "Alter des Posts : %s " % elapsed) 
        
                userID = message.author.id
                c.execute("SELECT * FROM users WHERE discordid = (?) and status = ?", (userID,"registered",))
                result = c.fetchone()
                curator_name= result[2]
                if result is None:
                    await client.send_message(message.channel, "Upvote kann nur von registrierten Mitgliedern benutzt werden -- bitte zuerst ?register aufrufen!")
                    check = check +1 
                    command_run = 1
                    logger.info("Upvote von %s gescheitert - User nicht registriert" % (message.author.name))

                elif result[6] == "Yes":
                    await client.send_message(message.channel, "Du hast heute schon einmal gevoted!")
                    logger.info("Upvote von %s gescheitert - User hat schon gevoted" % (message.author.name))

                    check = check +1
                    command_run = 1
                else:
                    registered_name = result[1]
                    
                    if curator_name == steem_name:
                        await client.send_message(message.channel, "Fehler - Das Vorschlagen eigener Posts ist untersagt!")
                        logger.info("Upvote von %s gescheitert - Eigener Post %s " % (message.author.name,args[1][pos1:length]))

                        check = check +1
                    else:
                        #check if the article is already in the list to vote
                        c.execute("SELECT * FROM articles WHERE permlink = (?)", (args[1][pos1:length],))
                        result = c.fetchone()
                        if result is not None and result[3] == "No": # Check if the article is already in the database and has not already been voted
                            votes=result[2]
                            votes = votes +1
                            await client.send_message(message.channel, "Artikel wurde bereits vorgeschlagen, erhöhe die Votes um 1")
                            c.execute("UPDATE articles SET votes = ? where permlink = ?", (votes,args[1][pos1:length],))
                            c.execute("UPDATE users SET has_voted = ? where steemname = ?", ("Yes",curator_name,))
                            db.commit()
                            check = 5
                            command_run = 1
                            logger.info("Upvote von %s erfolgreich - Votes auf %s wurden um 1 erhöht" % (message.author.name,args[1][pos1:length]))

                if check == 0:
                    
                    
                    data = article.export()
                    title=data["title"]
                    author = data["author"]
                    #print (title)
                    datarow =(registered_name,args[1][pos1:length],1,"No",title,author)
                    
                    # Insert the data into the SQLITE Table
                    c.execute("INSERT INTO articles VALUES(?,?,?,?,?,?)", datarow)
                    c.execute("UPDATE users SET has_voted = ? where steemname = ?", ("Yes",curator_name,))
                    #member  = discord.utils.get(message.server.members, name=steem_name)
                    #await client.send_message(member, "Wow - Ein Post von dir wurde von %s beim D-A-CH Support eingereicht!" % registered_name )
                    db.commit()
                    command_run = 1
                    await client.send_message(message.channel, "Erfolg - Du hast einen Post von %s beim D-A-CH Support eingereicht!" % steem_name )
                    logger.info("Upvote von %s erfolgreich - Artikel %s neu eingetragen " % (message.author.name,args[1][pos1:length]))

        else:
            await client.send_message(message.channel, "Fehler - Bitte den kompletten Link hinter §upvote einfügen, beginnend mit http...")
            command_run =1
            logger.info("Upvote von %s falsch aufgerufen" % (message.author.name))

            
#    if message.content.upper().startswith("?CHECKART"):
#        c.execute("SELECT * FROM articles")
#        result = c.fetchall() 
#        for r in result:
#            print(r)        
#        await client.send_message(message.channel, "Folgend Artikel sind derzeit eingereicht: \n %s " % result )
#        command_run =1
        
    if message.content.upper().startswith("?SHOWARTICLES"):
        c.execute("SELECT * FROM articles where voted = ? ORDER BY votes DESC", ("No",))
        result = c.fetchall() 
        for r in result:
            #print(r)        
            
            embed = discord.Embed(title="Artikel:" , description="[%s](%s)" % (str(r[4]),"https://steemit.com/"+str(r[1])), color=0x00ff00)
            embed.add_field(name="Autor", value="[%s](%s) " % (str(r[5]),"https://steemit.com/@"+str(r[5])), inline=True)
            #embed.add_field(name="Kurator", value="%s" % r[0], inline=True)
            embed.add_field(name="Votes", value="%s" % int(r[2]), inline=True)
            embed.set_thumbnail(url="")
            #embed.timestamp=datetime.datetime.utcnow()
            #embed.set_footer(text="fresh from the DACH-BOT")
            await client.send_message(message.channel, embed=embed)
        #await client.send_message(message.channel, "Folgend Artikel sind derzeit eingereicht: \n %s " % result )
        command_run =1
        logger.info("Showarticles von %s ausgeführt" % (message.author.name))



    
    if message.content.upper().startswith("?KILLART"): # Function to empty the table, only admins can do that, handle with care
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                c.execute("DELETE FROM articles")
                db.commit()
                executed = 1
                await client.send_message(message.channel, "Tabelle articles wurde geleert!" )
                logger.info("Killarticles von Admin %s ausgeführt - Tabelle geleert" % (message.author.name))

                command_run = 1
        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
            command_run = 1    
            logger.info("Killarticles von %s gescheitert - Keine Rechte " % (message.author.name))

    
    
    if message.content.upper().startswith("?ADDMEETUP"): # function to add new meetings, only usable by Admins
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                args = message.content.split(" ")
                Ort = str(args[1])
                Planer = str(args[2])
                Permlink = str(args[3])
                Datum = datetime.datetime.strptime(args[4], "%d.%m.%Y")
                #Datum = datetime.date(args[4])
                datarow =(Ort,Planer,Permlink,Datum)
                c.execute ("INSERT INTO meetup VALUES(?,?,?,?)", datarow )
                db.commit()
                command_run = 1
                executed = 1
                await client.send_message(message.channel, "Meetup von %s in %s wurde hinzugefügt" % (str(args[2]),str(args[1])) )
                logger.info("Addmeetup von Admin %s ausgeführt - Meetin in %s added" % (message.author.name,Ort))

        if executed == 0:  
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
            command_run = 1
            logger.info("Addmeetup von %s gescheitert - Keine Rechte " % (message.author.name))

    
        
        
    if message.content.upper().startswith("?NEXTMEETUP"): # funtion to display upoming meetings
        default = 4
        today = datetime.datetime.today()
        if (len(message.content.strip()) > 11) and message.content[11] == " ":
            args = message.content.split(" ")
            if args[1].isdigit():
                default = args[1]
            
        c.execute("SELECT * FROM meetup WHERE datum > (?) ORDER BY date(\"datum\") ASC LIMIT (?)", (today,default,))
        #print("fetchall:")
        result = c.fetchall() 
        if len(result)==0:
            await client.send_message(message.channel, "Derzeit sind keine Meetups geplant" )
            command_run = 1
        else:
            today = datetime.datetime.today()
            for r in result: # building the informations per meetup to fill the embed and post the message in a nice format
                pos1 = r[2].find("@")
                pos2 = r[2].find("/",pos1)
                steemname = (r[2][pos1+1:pos2])
                sbd = s.get_account(steemname)
                picdest = (str(sbd["json_metadata"]))
                posanf = picdest.find("profile_image")
                posanf = posanf +16
                posend = picdest.find("\"",posanf)
                deltadays = r[3] - today
                daystomeetup = deltadays.days
                
                
                if deltadays.days == 0:
                    daystomeetup = ("Morgen")
                if deltadays.days == -1:
                    daystomeetup = ("Heute")
                
                embed = discord.Embed(title="Nächstes Meetup in: %s" % r[0], description="", color=0x00ff00)
                embed.add_field(name="Planer", value="[%s](%s)" % (str(r[1]),"https://steemit.com/@"+str(r[1])))
                embed.add_field(name="Link", value="[Link zum Steemit-Post](%s) " % str(r[2]), inline=True)
                embed.add_field(name="Datum", value="%s" % datetime.datetime.strftime(r[3],"%d.%m.%Y"), inline=True)
                embed.add_field(name="Tage bis zum Meetup", value="%s" % daystomeetup, inline=True)
                embed.set_thumbnail(url=(picdest[posanf:posend]))
                embed.timestamp=datetime.datetime.utcnow()
                embed.set_footer(text="fresh from the DACH-BOT")
                await client.send_message(message.channel, embed=embed)
                command_run = 1
                logger.info("Nextmeetups von %s ausgeführt" % (message.author.name))

                
                
        
#    if message.content.upper().startswith("?KILLMEETUP"): # Function to empty the table, only admins can do that, handle with care
#        executed = 0
#        for role in message.author.roles:
#            if role.name == "Admin":
#                c.execute("DELETE FROM meetup")
#                db.commit()
#                executed = 1
#                await client.send_message(message.channel, "Tabelle meetup wurde geleert!" )
#                command_run = 1
#        if executed == 0:
#            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )
#            command_run = 1
                
    if message.content.upper().startswith("?MÄCHTIGERÖSI"): # special function for theaustrianguy and his welcoming project
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":
                account = Account("welcoming")
                count = 0
                for x in account.history(filter_by=["custom_json"]):
                    if "reblog" in str(x):
                        count = count + 1
                #print(str(count))
                await client.send_message(message.channel, "Der mächtige Ösi hat mit Welcoming %s Posts resteemed" % str(count) ) 
                executed = 1
                command_run = 1
                logger.info("MÄCHTIGERösicommand von %s ausgeführt - %s reblogs" % (message.author.name,count))

        if executed == 0:
            await client.send_message(message.channel, "Du hast nicht die benötigten Berechtigungen den Befehl auszuführen" )    
            command_run = 1
            logger.info("MÄCHTIGERösicommand von %s gescheitert - Keine Rechte!" % (message.author.name))

            
            
    if message.content.upper().startswith("?VERSION"): # display of version and thanks
        await client.send_message(message.channel, "D-A-CH Bot Version 0.4.1, brought to you by jedigeiss\nThanks to: louis88, rivalzzz, theaustrianguy, asperger-kids and mys" )
        command_run = 1
        
    
    if message.content.upper().startswith("?VOTE"):
        executed = 0
        for role in message.author.roles:
            if role.name == "Admin":# very basic voting functionality
                executed =1
                if(len(message.content.strip()) > 4) and message.content[5] == " ":
                    args = message.content.split(" ")
                    pos1 = args[1].find("@")
                    check = 0
                    if pos1 <= 0:
                        await client.send_message(message.channel, "Fehler - Bitte den kompletten Link hinter §upvote einfügen, beginnend mit http...")
                       # check = check +1
                    else:
                        pos2 = args[1].find("/",pos1)
                        steem_name = (args[1][pos1+1:pos2])
                        length = len(args[1])
                        article = (args[1][pos1:length])
                        #print (article)
                        percentage = int(args[2])
                        #print (percentage)
                        #print (permlink)
                        #print (percentage)
                        try: 
                            s.vote(article,percentage)
                            #await asyncio.sleep(1)
                            await client.send_message(message.channel, "Artikel %s erfolgreich mit %.2f Prozent gevoted!" % (article,percentage))
                            logger.info("Manuelles Upvote von %s mit %.2f Prozent ausgeführt, Post : %s" % (message.author.name,percent,article))
                        except Exception as e:
                            print (repr(e))
                            logger.info("Manuelles upvote von %s auf %s gescheitert Fehlercode : %s" % (message.author.name,article,e))
                            await client.send_message(message.channel, "Da ging was schief! Hast du vielleicht für den Artikel schon gevoted?")
                else: 
                    await client.send_message(message.channel, "Bitte ?vote Permlink Prozent benutzen!")
        if executed == 0:
            await client.send_message(message.channel, "Du hast keine Berechtigung den Befehl auszuführen!")
            logger.info("Manueller Vote von %s gescheitert - Keine Rechte" % (message.author.name))
            command_run =1
    
    
    
    else:
        if message.content.upper().startswith("?") and command_run == 0 and len(message.content.strip()) > 2 :
            #await printhelp(message)
            await client.send_message(message.channel, "Ruf den ?hilfe Befehl auf um die Benutzung der Befehle zu sehen, am besten in einer privaten Nachricht an den Bot")
        command_run =0           
client.run("your token here")
