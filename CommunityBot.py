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

Client = discord.Client()
client = commands.Bot(command_prefix = "?") # currently not used
fname = "save.txt" # Define the filename for the registered users data


if os.path.isfile(fname): # routine to either open an existing file or create a new one
    liste = pickle.load(open(fname,"rb")) 
else: 
    print ("File %s does not exist, creating a new one!" % fname)
    liste={}

s=Steem()
    
@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def printhelp(message): #function to print out help and usage methods
        embed = discord.Embed(title="D-A-CH Support Help", description="Befehle und Hilfe", color=0x00ff00)
        embed.add_field(name="!register", value="Benutzung: !register gefolgt vom Steemnamen eingeben um die Verbindung DiscordID und SteemID zu schaffen", inline=False)
        embed.add_field(name="!status", value="Benutzung: !status gibt die registrierten Benutzer und den Status des SteemBots zurück", inline=False)
        embed.add_field(name="!help oder !hilfe", value="Benutzung: !help gibt diese Hilfe zurück", inline=False)
        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)

@client.event
async def on_message(message):
    command_run=0
    if message.content.upper().startswith("§REGISTER"): # code for the !register command
        userID = message.author.id
        if (len(message.content.strip()) > 9):
            args = message.content.split(" ")
            if "@" in args[1]:
                await client.send_message(message.channel, "Fehler -- Bitte Steem ID ohne @ eingeben!")
            else:    
                command_run = 1
                if userID not in liste and args[1] not in liste :    
                    liste[userID] = args[1] # append the userid and the steem handle to the dict
                    await client.send_message(message.channel, "Für die Discord ID <@%s> wurde die Steem ID %s registriert !" % (userID,liste[userID]) )
                    f = open(fname,"wb") #write the dict into a file
                    pickle.dump(liste,f)
                    f.close()

                else:
                    await client.send_message(message.channel, "Die Discord ID <@%s> ist bereits mit der Steem ID %s verknüpft!" % (userID,liste[userID]) )
                    print (liste)           
                          
                    
    if message.content.upper().startswith("§STATUS"): # code for the status command, will list users and basic data about the bot
        account_name="dach-support"
        acc_data = s.get_account(account_name)
        votingpower=float(acc_data["voting_power"])
        votingpower = votingpower / 100
        votetime = acc_data["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
        votetime = votetime.replace("T", " ")
        votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        time_vp = now - votetime
        percentup = (int(((time_vp.total_seconds())/60)-60)*0.0139)
        if ((votingpower+percentup)>100): # capping the vote percentage at 100 
            resulting_vp = 100
        else:
            resulting_vp = (votingpower+percentup)
        embed = discord.Embed(title="D-A-CH Support Status", description="Alive and kickin!", color=0x00ff00)
        embed.add_field(name="Angemeldete User", value=liste, inline=False)
        embed.add_field(name="Votingpower", value="%.2f Prozent" % resulting_vp, inline=False)
        embed.set_thumbnail(url="https://steemitimages.com/DQmSxg3TwiR7ZcTdH9WKH2To48eJsdQ7D1ejpYUmvLtuzUk/steemitdachfullress.png")
        await client.send_message(message.channel, embed=embed)
        command_run = 1
    if message.content.upper().startswith("§HELP") or message.content.upper().startswith("§HILFE") : # code for the help function
        await printhelp(message)
        command_run = 1


     
        
    if message.content.upper().startswith("§ACCOUNT"): # code for the status command, will list users and basic data about the bot
        args = message.content.split(" ")
        account_name = str(args[1])
        sbd = s.get_account(account_name)
        profilepic = "https://img.busy.org/@" + account_name
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
        votetime = sbd["last_vote_time"] # start of caluclation of actual voting power, need to go some strange ways
        votetime = votetime.replace("T", " ")
        votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        time_vp = now - votetime
        percentup = (int(((time_vp.total_seconds())/60)-60)*0.0139)
        if ((votingpower+percentup)>100): # capping the vote percentage at 100 
            resulting_vp = 100
        else:
            resulting_vp = (votingpower+percentup)
        # building the embed to broadcast via discord    
        embed = discord.Embed(title="Account Übersicht", description=account_name, color=0x00ff00)
        embed.add_field(name="Steem Power", value="%.2f Steempower" % resulting_steempower)
        embed.add_field(name="Votingpower", value="%.2f Prozent " % resulting_vp)
        embed.add_field(name="Kontostand Steem", value=sbd["balance"])
        embed.add_field(name="Kontostand SBD", value=sbd["sbd_balance"])
        embed.set_thumbnail(url=profilepic)
        embed.timestamp=datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the blockchain")
        await client.send_message(message.channel, embed=embed) # send the built message
        command_run = 1
        
   
    else:
        if message.content.upper().startswith("§") and command_run == 0:
            await printhelp(message)
        command_run =0           
client.run("yourtokenhere")
