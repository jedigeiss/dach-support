#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 19:01:56 2018

@author: jan
"""
import locale
import datetime
import os
from beem import Steem
from beem.account import Account
from beem.exceptions import AccountDoesNotExistsException

#import discord
#from steem.converter import Converter
#import math
from pytz import timezone

STEEMPOSTINGKEY = os.environ.get('steemPostingKey')
S = Steem(wif=STEEMPOSTINGKEY)

def getinfo(account_name, switch):
    """provide information about a steem Account
    Arguments:
        account_name - the user name within steem
        switch - the level of detail to be fetched, possible values are
        vp for voting power, short for short information and long for
        a lot of information.
    """
    try:
        account = Account(account_name)
    except TypeError:
        #print(err)
        return -1
    except AccountDoesNotExistsException:
        return-1

    voting_power = account.get_voting_power()
    recharge = account.get_recharge_timedelta(voting_power_goal=100)
    now = datetime.datetime.now()
    timefull = now + recharge
    voting_power = round(voting_power, 2)
    voting_power = locale.format("%.2f", voting_power, grouping=True)
    steempower = account.get_steem_power()
    steempower = locale.format("%.2f", steempower, grouping=True)
    if switch == "vp":
        return voting_power, timefull


    reputation = account.get_reputation()
    reputation = locale.format("%.2f", reputation, grouping=True)
    steempower = account.get_steem_power()
    steempower = locale.format("%.2f", steempower, grouping=True)
    try:
        data = account.profile
        picurl = data["profile_image"]

    except TypeError:
        picurl = ("https://coinjournal.net/wp-content/uploads/2016/06/"
                  "steemit-logo-blockchain-social-media-platform-696x364.png")

    try:
        #maxops = account.virtual_op_count()
        #for r in account.history_reverse(start=maxops, stop=maxops -10,
        #                                  only_ops=["vote"],
        #                                  use_block_num=False):
        #    print("r %s"%r)
        json = account.json()
    except TypeError:
        return -1

    steemlink = "https://steemit.com/@"+ account_name
    today = datetime.datetime.today()
    created = json["created"]
    created = created.replace("T", " ")
    created = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
    since = today - created

    votetime = json["last_vote_time"]
    votetime = votetime.replace("T", " ")
    votetime = datetime.datetime.strptime(votetime, "%Y-%m-%d %H:%M:%S")
    time_comment = json["last_post"] # start of caluclation of last activity information
    time_comment = time_comment.replace("T", " ")
    time_comment = datetime.datetime.strptime(time_comment, "%Y-%m-%d %H:%M:%S")
    time_post = json["last_root_post"]
    time_post = time_post.replace("T", " ")
    time_post = datetime.datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
    latestactivity = max((votetime, time_comment, time_post))
    latestactivity = latestactivity.replace(tzinfo=timezone('UTC'))
    latestactivity_cet = latestactivity.astimezone(timezone('Europe/Berlin'))



    if switch == "short":
        return (steemlink, steempower, voting_power, created, since.days,
                reputation, latestactivity_cet, picurl)

    noposts = json["post_count"]
    balances = account.balances
    own_steem_power = account.get_steem_power(onlyOwnSP=True)
    own_steem_power = round(own_steem_power, 2)
    own_steem_power = locale.format("%.2f", own_steem_power, grouping=True)
    voteworth = account.get_voting_value_SBD()
    voteworth = locale.format("%.2f", voteworth, grouping=True)
    steem = balances["available"][0]
    steem = str(steem).replace("STEEM", "")
    steem = locale.format("%.2f", float(steem), grouping=True)

    sbd = balances["available"][1]
    sbd = str(sbd).replace("SBD", "")
    sbd = locale.format("%.2f", float(sbd), grouping=True)

    steem_savings = balances["savings"][0]
    steem_savings = str(steem_savings).replace("STEEM", "")
    steem_savings = locale.format("%.2f", float(steem_savings), grouping=True)

    sbd_savings = balances["savings"][1]
    sbd_savings = str(sbd_savings).replace("SBD", "")
    sbd_savings = locale.format("%.2f", float(sbd_savings), grouping=True)


    vests = balances["available"][2]

    if vests >= 1000000000:
        rank = "Wal"
    elif vests >= 100000000:
        rank = "Orca"
    elif vests >= 10000000:
        rank = "Delphin"
    elif vests >= 1000000:
        rank = "Minnow"
    else:
        rank = "Plankton"

    vests = str(vests).replace("VESTS", "")
    vests = locale.format("%.2f", float(vests), grouping=True)


    followers = account.get_follow_count()
    follower = followers["follower_count"]
    following = followers["following_count"]


    if switch == "long":
        return (steemlink, steempower, voting_power, created, since.days,
                reputation, latestactivity_cet, picurl, own_steem_power, steem,
                steem_savings, sbd, sbd_savings, rank, vests, noposts,
                follower, following, voteworth)        
