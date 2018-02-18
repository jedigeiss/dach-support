import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import pickle
import os

Client = discord.Client()
client = commands.Bot(command_prefix = "?") # currently not used
fname = "save.txt" # Define the filename for the registered users data

if os.path.isfile(fname): # routine to either open an existing file or create a new one
    liste = pickle.load(open(fname,"rb")) 
else: 
    print ("File %s does not exist, creating a new one!" % fname)
    liste={}


    
@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def printhelp(message): #function to print out help and usage methods
        embed = discord.Embed(title="D-A-CH Support Help", description="Befehle und Hilfe", color=0x00ff00)
        embed.add_field(name="!register", value="Benutzung: !register gefolgt vom Steemnamen eingeben um die Verbindung DiscordID und SteemID zu schaffen", inline=False)
        embed.add_field(name="!status", value="Benutzung: !status gibt die registrierten Benutzer und den Status des SteemBots zurück", inline=False)
        embed.add_field(name="!help oder !hilfe", value="Benutzung: !help gibt diese Hilfe zurück", inline=False)
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
                    
        #else:
         #   await printhelp(message)
            #await client.send_message(message.channel, "Benutzung: !register direkt gefolgt vom Steemnamen eingeben") #print out usage 
            #print (liste)           
                    
    if message.content.upper().startswith("§STATUS"): # code for the status command, will list users and basic data about the bot
        embed = discord.Embed(title="D-A-CH Support Status", description="Alive and kickin!", color=0x00ff00)
        embed.add_field(name="Angemeldete User", value=liste, inline=False)
        embed.add_field(name="Votingpower", value="not yet", inline=False)
        embed.set_thumbnail(url="")
        await client.send_message(message.channel, embed=embed)
        command_run = 1
    if message.content.upper().startswith("§HELP") or message.content.upper().startswith("§HILFE") : # code for the help function
        await printhelp(message)
        command_run = 1


    else:
        if message.content.upper().startswith("§") and command_run == 0:
            await printhelp(message)
        command_run =0    

client.run("yourbottoken") # you need to enter your own bot token here
