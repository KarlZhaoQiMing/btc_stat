#!/usr/bin/env  python
# -*- coding: utf-8 -*-
# 统计比特币交易信息，实现自动化交易

import time
import datetime
import pymongo
import sys
import requests
reload(sys)
sys.setdefaultencoding('utf-8')

coin_name_list = {"btc":"比特币","doge":"狗狗币","etc":"以太经典","eth":"以太坊","ltc":"莱特币","ybc":"元宝币"}

coin_type_dict = {"btc":1,"doge":5,"etc":7,"eth":6,"ltc":2,"ybc":4}

def trade_info(url):
    result = requests.get(url)
    if result.status_code != 200:
        print "url:{}, code:{}".format(url, result.status_code)
        return None
    else:
        return result.json()

def get_coin_price_info_url(timestamp):
    url = "https://www.btctrade.com/coin/rmb/rate.js?t={}".format(timestamp)
    
    return url

def get_trade_url(coin_type, timestamp):
    url = "https://www.btctrade.com/coin/rmb/{}/trust.js?t={}".format(coin_type, timestamp)
    return url

def trade_info_stat(trade_info):
    price_avg = 0
    price_amt_max = 0
    price_amt_max_price = 0
    price_max = 0
    price_min = 10000000
    price_total = 0
    price_number = 0
    for one_info in trade_info:
        price = float(one_info.get("p"))
        number = float(one_info.get("n"))
        #print "p:{}, n:{}, total:{}".format(price, number,price_total, price_number)
        price_total = price_total + price * number
        price_number = price_number + number
        price
        if number > price_amt_max:
            price_amt_max = number
            price_amt_max_price = price
        if price > price_max:
            price_max = price
        if price < price_min:
            price_min = price
    price_avg = price_total / price_number
    price_amt_max_per = price_amt_max / price_number
    print "    total:{}, count:{}, avg:{}".format(price_total,price_number, price_avg)
    print "    price_amt_max:{}, price:{}, percent:{}".format(price_amt_max, price_amt_max_price, price_amt_max_per)
    return (price_avg,price_amt_max_price,price_number)

def recommend_buy_price(price_avg, price_amt_max_price):
    if price_avg < price_amt_max_price:
        return price_amt_max_price * 1.005
    else:
        return price_avg * 1.005

def recommend_sale_price(price_avg, price_amt_max_price):
    if price_avg < price_amt_max_price:
        return price_avg * 0.995
    else:
        return price_amt_max_price * 0.995


def make_trust():
    return 0

def cancel_trust():
    return 0

def get_trust_info(session, coin):
    coin_type = coin_type_dict.get(coin)
    url = "https://www.btctrade.com/ajax/opentrades/coin/{}".format(coin_type)
    #print url
    result = session.post(url)
    #print result.status_code
    if result != None:
        data = result.json()
        if data.get("status") == 1:
            #print data.get("data")
            return data.get("data").get("datas")
        else:
            return None
    else:
        return None



def web_login():
    url = "https://www.btctrade.com/user/login/"
    s = requests.Session()
    data = {
                "email":"18611175072",
                "pwd":"20081003569",
                "captcha":None,
                "hotp":None
            }
    s.post(url,data)
    return s


def save_coin_price():
    timestamp = time.time()
    url = get_coin_price_info_url(timestamp)
    coin_info = get_trade_info(url)
    if coin_info is not None:
        
        return "success"

def main(coin_name_list):
    #获取doge_coin的交易信息
    timestamp = time.time()
    print timestamp
    profit_dict = {}
    session = web_login()
    for (coin,name) in coin_name_list.items():
        print "  \n  =====  {}:{} 交易信息   ==== ".format(coin,name)
        doge_trade_url = get_trade_url(coin, timestamp)
        doge_trade_info = trade_info(doge_trade_url)
        if doge_trade_info is not None:
            doge_buy = doge_trade_info.get("buy")
            doge_sale = doge_trade_info.get("sale")
            print "  **  buy stat info  **"
            (price_avg, price_amt_max_price,buy_number) = trade_info_stat(doge_buy)
            recommend_buy = recommend_buy_price(price_avg, price_amt_max_price)
            print "    recommend buy price:{}".format(recommend_buy)
            print "  **  sale stat info  **"
            (price_avg_1, price_amt_max_price_1,sale_number) = trade_info_stat(doge_sale)
            recommend_sale = recommend_sale_price(price_avg_1, price_amt_max_price_1)
            print "    recommend sale price:{}".format(recommend_sale)
            
            if buy_number > sale_number:
                print "    buy_numbe > sale_number, ratio:{}   ↑↑↑↑↑↑".format(buy_number/sale_number)
            else:
                print "    sale_number > buy_number, ratio:{}   ↓↓↓↓↓↓".format( sale_number/buy_number)



            profit = recommend_sale - recommend_buy
            profit_rate = profit / recommend_buy  
            profit_dict[coin] = profit_rate
            print "    profit:{}, profit_rate:{}".format(profit, profit_rate)
            
            trust_data = get_trust_info(session, coin)
            if trust_data is not None and len(trust_data) > 0:
                print "  ** trust info  **"
            for one_trust in trust_data:
                price = one_trust.get("price")
                number = one_trust.get("numberover")
                flag = one_trust.get("flag")
                print "    {}: {} {}".format(flag,price,number)
    print "\n**************************\n"
    sort_profit_dict = sorted(profit_dict.items(), key=lambda d: d[1], reverse=True)

    for profit in sort_profit_dict:
        key = profit[0]
        profit_rate = profit[1]
        name = coin_name_list.get(key)
        if profit_rate > 0.03:
            print " best coin:{}, name:{}, profit_rate:{}  good time to buy".format(key, name, profit_rate)
        else:
            print " best coin:{}, name:{}, profit_rate:{}".format(key, name, profit_rate)

if __name__ == "__main__":
    coin_name_list = {"btc":"比特币","doge":"狗狗币","etc":"以太经典","eth":"以太坊","ltc":"莱特币","ybc":"元宝币"}
    main(coin_name_list)

