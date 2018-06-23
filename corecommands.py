#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 17:32:48 2018

@author: jan
"""
import datetime
import sqlite3
from beem.comment import Comment
from beem.account import Account
#import asyncio
#import time
#import os

# initializing the db that will hold the articles to be voted
db = sqlite3.connect("articles.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)
c = db.cursor()


def check_maxops():
    acc = Account("dach-support")
    #counter = 0
    max_op_count = acc.virtual_op_count()
    c.execute("SELECT operations FROM config")
    result = c.fetchone()
    if max_op_count > result[0]:
        return max_op_count, result[0]
        
    return 0, 0


    

def update_db(max_op_count, min_op_count):
    acc = Account("dach-support")
    #min_op_count
    updates = 0
    for row in acc.history_reverse(start=max_op_count, stop=min_op_count,
                               only_ops=["transfer"], use_block_num=False):
        steemuser = row["from"]
        token = row["memo"]
        amount = row["amount"]
        datarow = (steemuser,token,amount)
        c.execute("INSERT INTO transfers (steemname, memo, amount) VALUES(?,?,?)", datarow)
        db.commit()
        updates = updates + 1
    c.execute("UPDATE config SET operations = ?", (max_op_count,))
    db.commit()
    return updates
                    
                                 
    

def doupvote(curator, steemlink):
    pos = steemlink.find("@")
    if pos <= 0:
        return -1
    else:
        pos1 = steemlink.find("/", pos)
        steem_name = (steemlink[pos+1:pos1])
        length = len(steemlink)
        permlink = (steemlink[pos:length])
        try:
            article = Comment(permlink)
        except TypeError:
            return -1
        json = article.json()
        #print(json)
        created = json["created"]
        created = created.replace("T", " ")
        created = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.utcnow()
        now_cet = datetime.datetime.now()
        today = datetime.datetime.strftime(now_cet, "%d.%m.%Y")
        elapsed = now - created


        # starting the checks to see if curator and post are valid
        # check if the curator is registered correctly
        c.execute("SELECT * FROM users WHERE discordid = (?) and status = ?",
                  (curator, "registered",))
        result = c.fetchone()
        curator_steem_name = result[2]
        if result is None:
            return -4
        # check if the curator has votes left
        c.execute("SELECT Count() from votes where kurator_ID = ? AND datum = ?",
                  (curator, today,))
        no_of_votes = c.fetchone()

        if no_of_votes[0] >= 3:
            return -5

        # check if the author is on the blacklist
        c.execute("SELECT Count() FROM blacklist WHERE steemname = ?", (steem_name,))
        result = c.fetchone()
        if result[0] == 1:
            return -10, steem_name


        # check if the curator has already voted for that article
        c.execute("SELECT Count() FROM votes where kurator_ID = ? AND permlink = ?",
                  (curator, permlink,))

        result = c.fetchone()
        if result[0] > 0:
            return -8
        # check if the post is not older than five days
        if elapsed >= datetime.timedelta(days=5):
            return -2
        # check if the post is a main article
        if article.is_main_post() is False:
            return -3

        # check if the author of the post and the curator are the same
        # selfuptvoting is not allowd
        if curator_steem_name == steem_name:
            return -6
        # check if the article is already in the database or if it needs to be inserted
        c.execute("SELECT * FROM articles WHERE permlink = ?", (permlink,))
        result = c.fetchone()
        # check if the article has already received a vote from the bot
        if result is not None and result[3] != "No":
            return -7, result[3]
        # article is in the DB and votes are increased by 1
        if result is not None and result[3] == "No":
            votes = result[2]
            votes = votes +1
            c.execute("UPDATE articles SET votes = ? WHERE permlink = ?", (votes, permlink,))
            c.execute("INSERT INTO votes (permlink, kurator_ID, datum) VALUES (?,?,?)",
                      (permlink, curator, today,))
            db.commit()
            return 1, steem_name
        # article needs to be added new to the database
        title = json["title"]
        datarow = (curator, permlink, 1, "No", title, steem_name)
        c.execute("INSERT INTO articles (kurator, permlink, votes, voted, title, author)"
                  "Values (?,?,?,?,?,?)", datarow)
        c.execute("INSERT INTO votes (permlink, kurator_ID, datum) VALUES (?,?,?)",
                  (permlink, curator, today,))
        db.commit()
        return 2, steem_name

def doaddmeetup(ort, planer, permlink, datum, uhrzeit):
    datum = datetime.datetime.strptime(datum, "%d.%m.%Y")
    datarow = (ort, planer, permlink, datum, uhrzeit)
    try:
        c.execute("INSERT INTO meetup (ort, planer, permlink, datum, uhrzeit)"
                  " VALUES(?,?,?,?,?)", datarow)
        db.commit()
        return 0
    except sqlite3.Error as err:
        print(err)
        return -1

def dokillmeetup(key):

    try:
        c.execute("SELECT count(*) from meetup where ID = ?", (key, ))
        result = c.fetchone()
        if result[0] == 1:
            c.execute("DELETE FROM meetup where ID = ?", (key, ))
            db.commit()
            return 1
        return 0
    except sqlite3.Error as err:
        print(err)
        return -1


def getmeetup(anzahl):
    today = datetime.datetime.today()
    c.execute("SELECT * FROM meetup WHERE datum > (?) ORDER BY"
              " date(\"datum\") ASC LIMIT (?)", (today, anzahl, ))
    result = c.fetchall()
    if not result:
        return -1
    return result
