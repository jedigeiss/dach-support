#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 18:26:01 2018

@author: jan
"""
import datetime
import locale
import os
import discord
import asyncio
import sqlite3
from beem.account import Account

from discord.ext.commands import Bot
from discord.ext import commands
from steem import Steem
from steeminfo import getinfo
from corecommands import doupvote
from corecommands import check_maxops
from corecommands import update_db
from corecommands import doaddmeetup
from corecommands import dokillmeetup
from corecommands import getmeetup
from externalinfo import getweather
from externalinfo import getprice


BOT_PREFIX = "?"
TOKEN = "NDI0NzAyMDM1Njg2OTgxNjQy.DY8uNA.P4r1zXK2XoSUnBmZZjtZEiYzvxk"

#STEEMPOSTINGKEY = os.environ.get('steemPostingKey')


#s = Steem(wif=STEEMPOSTINGKEY)

locale.setlocale(locale.LC_ALL, '')

client = Bot(command_prefix=BOT_PREFIX)

db = sqlite3.connect("articles.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)
c = db.cursor()


async def check_register():
    await client.wait_until_ready()
    while not client.is_closed:
        ret = check_maxops() # check if there are any new operations
        #counter += 1
        if ret[0] > 1:
            switch = update_db(ret[0],ret[1]) # checking if the latest operations have been transfers, if yes switch is > 0 
            if switch > 0:    
                c.execute("SELECT * FROM users WHERE status = ?", ("pending steem",))
                result = c.fetchall()
                if len(result)>0:
                    print("Neue Transaktionen gefunden, vergleiche Token ..")
                    for r in result:
                        discorduser= r[1]
                        reguser = r[2]
                        regtoken =r[3]
                        c.execute("SELECT * FROM transfers where steemname = ? AND memo = ?", (reguser, regtoken))
                        result = c.fetchone()
                        if result is not None:
                            c.execute("UPDATE users SET status = ? where discordname = ?", ("registered",discorduser,))
                            u=discord.User(id=r[0])
                            await client.send_message(u, "Registrierung mit dem D-A-CH Support Bot abgeschlossen!\nDiscordUser: %s ist jetzt mit Steemname: %s registriert" %(discorduser, reguser))
                            db.commit()
                            print(reguser,regtoken)
                        
        elif ret[0] == 0:
            print("Keine neuen Operationen, nichts zu tun ..")
                

        
        #print("max op count %s" % max_op_count)
        await asyncio.sleep(120)


@client.event
async def on_ready(): # print on console that the bot is ready
    print("Bot is online and connected to Discord")

@client.event
async def on_command_error(error, ctx):
    await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen: %s" % error)


@client.command(description="Information über einen Steem User.",
                brief="Kurzinformationen über einen Steem User",
                aliases=["shortinfo", "short", "Info"])
async def info(account_name):

    data = getinfo(account_name, "short")
    if data == -1:
        await client.say("Es konnte kein Steem Account mit Namen %s gefunden werden" % account_name)

    else:
        #print (data)
        steemlink = data[0]
        resulting_steempower = data[1]
        resulting_vp = data[2]
        created = data[3]
        days = data[4]
        rep = data[5]
        latestactivity_cet = data[6]
        picurl = data[7]

        embed = discord.Embed(title="Short Account Information",
                              description="[%s](%s)"% (account_name, steemlink), color=0x00ff00)
        embed.add_field(name="Steem Power", value="%s SP" % str(resulting_steempower))
        embed.add_field(name="Votingpower", value="%s Prozent" % resulting_vp)
        embed.add_field(name="Angemeldet seit", value="%s, %s Tage" %
                        (datetime.datetime.strftime(created, "%d.%m.%Y"), days))
        embed.add_field(name="Reputation", value=rep)
        embed.add_field(name="Letzte Aktion auf Steem",
                        value=datetime.datetime.strftime(latestactivity_cet, "%d.%m.%Y %H:%M"))

        embed.set_thumbnail(url=picurl)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="frisch von der Blockchain")
        await client.say(embed=embed) # send the built message


@client.command(description="Viele Information über einen Steem User.",
                brief="Deutlich mehr Informationen über einen Steem User",
                aliases=["long", "Longinfo", "Long"])
async def longinfo(account_name):

    data = getinfo(account_name, "long")
    if data == -1:
        await client.say("Es konnte kein Steem Account mit Namen %s gefunden werden" % account_name)

    else:
        #print (data)
        steemlink = data[0]
        resulting_steempower = data[1]
        resulting_vp = data[2]
        created = data[3]
        days = data[4]
        rep = data[5]
        latestactivity_cet = data[6]
        picurl = data[7]
        steempower = data[8]
        amount_steem = data[9]
        amount_steem_savings = data[10]
        amount_sbd = data[11]
        amount_sbd_savings = data[12]
        rank = data[13]
        SPown = data[14]
        noposts = data[15]
        follower = data[16]
        following = data[17]
        voteworth = data[18]

        embed = discord.Embed(title="Account Information",
                              description="[%s](%s)"% (account_name, steemlink), color=0x00ff00)
        embed.add_field(name="Steem Power", value="%s SP" % resulting_steempower)
        embed.add_field(name="Eigene SP", value="%s SP" % steempower)
        embed.add_field(name="Votingpower", value="%s Prozent" % resulting_vp)
        embed.add_field(name="Vote Wert", value="%s STU" % voteworth)
        embed.add_field(name="Kontostand Steem (Save)", value="%s (%s) STEEM"
                        % (amount_steem, amount_steem_savings))
        embed.add_field(name="Kontostand SBD (Save)", value="%s (%s) SBD"%
                        (amount_sbd, amount_sbd_savings))
        embed.add_field(name="Angemeldet seit", value="%s, %s Tage" %
                        (datetime.datetime.strftime(created, "%d.%m.%Y"), days))
        embed.add_field(name="Reputation", value=rep)
        embed.add_field(name="Rang", value=rank)
        embed.add_field(name="MVests", value="%s" % SPown)
        embed.add_field(name="Anzahl Posts", value=noposts)
        embed.add_field(name="Anzahl Follower", value=follower)
        embed.add_field(name="Anzahl Following", value=following)

        embed.add_field(name="Letzte Aktion auf Steem",
                        value=datetime.datetime.strftime(latestactivity_cet, "%d.%m.%Y %H:%M"))

        embed.set_thumbnail(url=picurl)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="frisch von der Blockchain")
        await client.say(embed=embed) # send the built message

@client.command(description="Votingpower.",
                brief="Aktuelle Voting Power eines Steem User",
                aliases=["VP", "vp", "Votingpower"])
async def votingpower(account_name):
    data = getinfo(account_name, "vp")
    if data == -1:
        await client.say("Es konnte kein Steem Account mit Namen %s gefunden werden" % account_name)
    elif data[0] == "100,00":
        await client.say("Die aktuelle Voting Power von %s beträgt 100 Prozent." % account_name)
    else:
        datefull = datetime.datetime.strftime(data[1], "%d.%m. um %H:%M")
        await client.say("Die aktuelle Voting Power von %s beträgt %s Prozent.\n"
                         "Die VP wird am %s wieder auf 100 Prozent sein." %
                         (account_name, data[0], datefull))

@client.command(description="Wetter-Informationen",
                brief="Wetter Informationen und Vorschau",
                aliases=["Wetter", "wetter", "Weather"])
async def weather(city):
    condition, forecasts = getweather(city)
    if condition == -1 or forecasts == -1:
        await client.say("Keine daten für %s gefunden!" % city)
    else:
        embed = discord.Embed(title="Wetter Übersicht für :", description=city,
                              color=0x00ff00)
        embed.add_field(name="Wetterlage Heute", value="%s bei %s Grad Celsius" %
                        (condition.text, condition.temp))
        embed.add_field(name="Vorhersage %s" % forecasts[1].date,
                        value="%s %s bis %s Grad" %
                        (forecasts[1].text, forecasts[1].low, forecasts[1].high), inline=False)
        embed.add_field(name="Vorhersage %s" % forecasts[2].date,
                        value="%s %s bis %s Grad" %
                        (forecasts[2].text, forecasts[2].low, forecasts[2].high), inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the DACH-BOT and Yahoo Weather")
        await client.say(embed=embed)

@client.command(description="Kurse von Kryptocoins",
                brief="Detaillierte Infos über Kryptocoins",
                aliases=["Kurs", "price", "Price"])
async def kurs(coin):
    data = getprice(coin)
    if data == -1:
        await client.say("Die Coin %s wurde auf Coinmarketcap nicht gefunden" % coin)
    else:
        priceusd = data[0]
        priceeur = data[1]
        pricebtc = data[2]
        name = data[3]
        change1h = data[4]
        change24h = data[5]
        change7d = data[6]

        embed = discord.Embed(title="Preis Übersicht :", description=name, color=0x00ff00)
        embed.add_field(name="Preis USD", value="%.3f" % float(priceusd))
        embed.add_field(name="Preis EUR", value="%.3f" % float(priceeur))
        embed.add_field(name="Preis BTC", value="%s" % pricebtc)
        embed.add_field(name="Change 1h", value="%s %%" % change1h)
        embed.add_field(name="Change 24h", value="%s %%" % change24h)
        embed.add_field(name="Change 7d", value="%s %%" % change7d)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="fresh from the DACH-BOT and Coinmarketcap")
        await client.say(embed=embed)

@client.command(description="D-A-CH Bot Version",
                brief="Version des D-A-CH Bots",
                aliases=["Version", "ver", "Ver"])
async def version():
    await client.say("D-A-CH Bot Version 0.8, brought to you by jedigeiss"
                     "\nThanks to: louis88, rivalzzz, theaustrianguy, asperger-kids and mys")

@client.command(description="Funktion zum Vorschlagen eines Artikels beim DachBot",
                brief="Community Vote für einen Artikel",
                aliases=["Up", "Upvote", "up"],
                pass_context=True)

async def upvote(ctx, permlink):
    print(ctx.message.author)
    result = doupvote(ctx.message.author.id, permlink)

    if result == -1:
        await client.say("Bitte den kompletten Link hinter ?Upvote eingeben "
                         "beginnend mit https://...")
    elif result == -2:
        await client.say("Der Post ist leider älter als 5 Tage...")

    elif result == -3:
        await client.say("Kommentare können nicht gevoted werden!")

    elif result == -4:
        await client.say("Upvote kann nur von registrierten Mitgliedern"
                         " benutzt werden!")
    elif result == -5:
        await client.say("Du hast heute schon 3 Votes vergeben, die Votes werden"
                         " um Mitternacht zurückgesetzt!")

    elif result == -6:
        await client.say("Selbstupvotes sind nicht erlaubt!")

    elif result == -8:
        await client.say("Du hast diesen Artikel schon gevoted!")

    elif result[0] == -7:
        await client.say("Artikel wurde bereits vom Bot mit %s Prozent"
                         " gevoted" % result[1])
    elif result[0] == -10:
        await client.say("User %s ist auf der Blacklist und kann"
                         " nicht gevoted werden!" % result[1])

    elif result[0] == 1:
        await client.say("Der Artikel von %s war schon vorgeschlagen, erhöhe die"
                         " Anzahl der Votes um 1." % result[1])
    elif result[0] == 2:
        await client.say("Erfolg! Der Artikel von %s wurde beim D-A-CH Support"
                         " Bot eingereicht!" % result[1])



@client.command(description="Hinzufügen eines Meetups -- nur Admins",
                brief="Hinzufügen eines Meetups -- nur Admins",
                aliases=["Addmeetup", "AM"],
                pass_context=True)
@commands.has_role("Admin")
async def addmeetup(ctx, ort, planer, permlink, datum, uhrzeit):
    result = doaddmeetup(ort, planer, permlink, datum, uhrzeit)
    if result == 0:
        await client.send_message(ctx.message.channel, "Meetup von %s in"
                                  " %s wurde hinzugefügt" % (planer, ort))
    else:
        await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen")
    

@client.command(description="Löschen eines Meetups -- nur Admins",
                brief="Löschen eines Meetups -- nur Admins",
                aliases=["KM", "km"],
                pass_context=True)
@commands.has_role("Admin")
async def killmeetup(ctx, key):
    result = dokillmeetup(key)
    if result == 1:
        await client.send_message(ctx.message.channel, "Meetup %s"
                                  " wurde gelöscht" % (key))
    if result == 0:
        await client.send_message(ctx.message.channel, "Meetup %s"
                                  " wurde nicht gefunden" % (key))
    if result == -1:
        await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen")





@client.command(description="Anzeigen der nächsten Meetups",
                brief="Anzeigen der nächsten Meetups",
                aliases=["Nextmeetup", "NM", "nm"],
                pass_context=True)
async def nextmeetup(ctx, anzahl=4):
    
    result = getmeetup(anzahl)
    today = datetime.datetime.today()
    if result == -1:
        await client.send_message(ctx.message.channel, "Keine zukünftigen"
                                  " Meetups in der DB")
    
    else:
        for r in result:    
        
            deltadays = r[3] - today
            picurl="https://coinjournal.net/wp-content/uploads/2016/06/steemit-logo-blockchain-social-media-platform-696x364.png"
    
            if deltadays.days == 0:
                daystomeetup = ("Morgen")
            if deltadays.days == -1:
                daystomeetup = ("Heute")
            elif deltadays.days >=1 :
                daystomeetup = deltadays.days + 1  
            embed = discord.Embed(title="Nächstes Meetup in: %s" % r[1], description="", color=0x00ff00)
            embed.add_field(name="Planer", value="[%s](%s)" % (str(r[0]),"https://steemit.com/@"+str(r[0])))
            embed.add_field(name="Link", value="[Link zum Steemit-Post](%s) " % str(r[2]), inline=True)
            embed.add_field(name="Datum", value="%s" % datetime.datetime.strftime(r[3],"%d.%m.%Y"), inline=True)
            embed.add_field(name="Uhrzeit", value="%s Uhr" % r[5], inline=True)
            embed.add_field(name="Tage bis zum Meetup", value="%s" % daystomeetup, inline=True)
            embed.set_thumbnail(url=picurl)
            embed.timestamp=datetime.datetime.utcnow()
            embed.set_footer(text="ID: %s | fresh from the DACH-BOT" % r[4])
            await client.send_message(ctx.message.channel, embed=embed)
                    
    #if result == 0:
    #    await client.send_message(ctx.message.channel, "Meetup von %s in"
   #                               "%s wurde hinzugefügt" % (planer, ort))
    #else:
    #    await client.send_message(ctx.message.channel, "Da ist was schiefgelaufen")
    
                
            #logger.info("Addmeetup von Admin %s ausgeführt - Meetin in %s added", ctx.message.author.name, Ort)

client.loop.create_task(check_register())

    
client.run(TOKEN)
