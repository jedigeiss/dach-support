#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 21:49:13 2018

@author: jan
"""
import os
from steem import Steem
import sqlite3
import time
import logging


logger = logging.getLogger("DachBot")
logger.setLevel(logging.INFO)

# Logging Format definitions

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler = logging.FileHandler("DachVoter.log")
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

db = sqlite3.connect("articles.db", detect_types=sqlite3.PARSE_DECLTYPES) # initializing the connection to the db that holds the articles to be voted
cursor = db.cursor()
    

# clears all set votes for the new voting round after the votes have been executed
def clearvotes():
    cursor.execute("UPDATE users SET has_voted = ?", ("No",))
    db.commit()
                              
def run():
    
    steemPostingKey = os.environ.get('steemPostingKey')
    s = Steem(wif=steemPostingKey) # Steem initialisation for use with environment variable

    cursor.execute("Select Count() from articles where voted = ? ORDER BY votes DESC", ("No",))
    count  = cursor.fetchone()   
    count = int(count[0])
    cursor.execute("SELECT * FROM articles where voted = ? ORDER BY votes DESC", ("No",))
    result = cursor.fetchall() 
    if count == 0:
        logger.info("Nothing to do exiting")
        return 0
    # calculation of the voting percentages per article, less than 11 will result in full votes
    if count > 0 and count <= 11:
        for r in result:
            permlink = r[1]
            #print ("permlink %s percentage %s" % (permlink,100))
            s.vote(permlink,100)
            cursor.execute("UPDATE articles set voted = ? where permlink = ?", ("100",permlink,))
            db.commit()
            time.sleep(4)
            logger.info("Voted Article %s with %s percent", permlink, 100)
        
        logger.info("Voted %s Articles with 100 percent", count)
        return count
    else:# check if it is exactly 11 articles that are on the first eleven places with discrete number of votes
        if result[10][2] > result[11][2]:
            newlist = result[0:11]
            notvoted = result[12:]
            restcount = count - 11
            for r in newlist:
                permlink = r[1]
                #print ("permlink %s percentage %s" % (permlink,100)
                s.vote(permlink,100)
                cursor.execute("UPDATE articles set voted = ? where permlink = ?", ("100",permlink,))
                db.commit()
                time.sleep(4)
                logger.info("Voted Article %s with %s percent", permlink, 100)
            for r in notvoted:
                permlink = r[1]
                cursor.execute("UPDATE articles set voted = ? where permlink = ?",("0",permlink,))
                db.commit()
                logger.info("Voted Article %s with %s percent", permlink, 0)
            
            logger.info("Voted %s Articles with 100 percent, %s Articles are not voted", 11, restcount)
            return 11    
        else: # last option, we have a last level of votes (normally this is the 1 vote per article category) that we also need to take into account
            minvotes = result[10][2]
            cursor.execute("Select Count() from articles where voted = ? AND votes >= ? ORDER BY votes DESC", ("No", minvotes,))
            newcount  = cursor.fetchone()      
            cursor.execute("Select Count() from articles where voted = ? AND votes = ? ORDER BY votes DESC", ("No", minvotes,))
            mincount = cursor.fetchone()
            newcount = int(newcount[0])
            mincount = int(mincount[0])
            
            if newcount == mincount: # for the rare case that we are having complete homogeneous voting distribution
                remaining = round(1100 / newcount,2)
                votelist = result[0:newcount]
                rest = result[newcount:]
                restcount = count - newcount
                for r in votelist:
                    permlink = r[1]
                    s.vote(permlink,remaining)
                    cursor.execute("UPDATE articles set voted = ? where permlink = ?", (remaining,permlink,))
                    db.commit()
                    logger.info("Voted Article %s with %s percent", permlink, remaining)
                    #print ("permlink %s percentage %s" % (permlink,remaining))
                    time.sleep(4)
                
                for r in rest:
                    permlink = r[1]
                    cursor.execute("UPDATE articles set voted = ? where permlink = ?", ("0",permlink,))
                    db.commit()
                    #print ("permlink %s percent %s" % (permlink,0))
                    logger.info("Voted Article %s with %s percent", permlink, 0)
                    
                logger.info("Voted %s Articles with %s percent, %s Articles are not voted", newcount, remaining, restcount )
                return newcount
                
            else: # normal case 
                toposts = newcount - mincount
                top = result[0:toposts]
                votes = result[toposts:newcount]
                rest = result[newcount:]
                restcount = count - newcount
                for r in top:
                    permlink = r[1]
                    s.vote(permlink,100)
                    cursor.execute("UPDATE articles set voted = ? where permlink = ?", ("100",permlink,))
                    db.commit()
                    logger.info("Voted Article %s with %s percent", permlink, 100)
                    time.sleep(4)
                    
                remaining = round((1100 - (toposts*100)) / mincount,2)
                for r in votes:
                    permlink = r[1]
                    s.vote(permlink,remaining)
                    cursor.execute("UPDATE articles set voted = ? where permlink = ?", (remaining,permlink,))
                    db.commit()
                    logger.info("Voted Article %s with %s percent", permlink, remaining)
                    time.sleep(4)
                
                for r in rest:
                    permlink = r[1]
                    cursor.execute("UPDATE articles set voted = ? where permlink = ?", ("0",permlink,))
                    db.commit()
                    logger.info("Voted Article %s with %s percent", permlink, 0)
                    #print ("permlink %s percent %s" % (permlink,0))
                    
                logger.info("Voted %s Articles with %s percent, %s Articles with %s percent and %s Articles with 0 percent", toposts, 100, mincount, remaining, restcount)
                return newcount    
    
if __name__ == "__main__":
    x = run()
    if x == 0:
        print ("Nothing to do.. Exiting")
    if x > 1:
        print ("Voted sucessfully %s Posts! Exiting.." % x)
    clearvotes()
                   