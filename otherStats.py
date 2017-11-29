#!/usr/bin/python
import urllib
import os
from urllib import urlencode
import sys
import redis
import time
import json
import ssl
import re
import requests

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

#Config Redis server we're connecting to
pool = redis.ConnectionPool( host='127.0.0.1', port=6379, password='', db=2 )
redisServer = redis.Redis( connection_pool=pool )
pipe = redisServer.pipeline()

#Coin Arrays
dbixArray = [
  {'url':'https://dbix.cryptopros.us', 'api':'https://dbix.cryptopros.us/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'CryptoPros', 'fee':'0.2%', 'cloudflare':'true'},
  {'url':'http://dbix.krokipool.pro', 'api':'http://dbix.krokipool.pro/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Krokipool', 'fee':'0.2%', 'cloudflare':'false'},
  {'url':'http://dbix.pool.sexy', 'api':'http://dbix.pool.sexy/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'PoolSexy1', 'fee':'0.25%', 'cloudflare':'false'},
  {'url':'http://dbix2.pool.sexy', 'api':'http://dbix2.pool.sexy/api3/', 'stats':'stats', 'blocks':'blocks/', 'name':'PoolSexy2', 'fee':'0.15%', 'cloudflare':'false'},
  {'url':'http://dbix3.pool.sexy', 'api':'http://dbix3.pool.sexy/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'PoolSexy3', 'fee':'0.05%', 'cloudflare':'false'},
  {'url':'https://dbix.zet-tech.eu', 'api':'https://dbix.zet-tech.eu/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Zet', 'fee':'0%', 'cloudflare':'false'}]

pirlArray = [
  {'url':'https://pirl.cryptopros.us', 'api':'https://pirl.cryptopros.us/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'CryptoPros', 'fee':'0%', 'cloudflare':'true'},
  {'url':'http://pirl.espool.eu', 'api':'http://pirl.espool.eu/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'ESPOOL.EU', 'fee':'0%', 'cloudflare':'false'},
  {'url':'http://pirl.minerpool.net', 'api':'http://pirl.minerpool.net/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Minerpool', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://pools.hppcg.com', 'api':'https://us-nj-01.pools.hppcg.com/pirl/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'HPPCG', 'fee':'0.25%', 'cloudflare':'false'},
  {'url':'http://pirl.digitalpool.cc', 'api':'http://pirl.digitalpool.cc/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'DigitalPool', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://pirl.pool.sexy', 'api':'http://pirl.pool.sexy/api6/', 'stats':'stats', 'blocks':'blocks/', 'name':'Pool.Sexy', 'fee':'0.25%', 'cloudflare':'false'},
  {'url':'http://mole-pool.net', 'api':'http://109.70.186.58:3020/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Mole-Pool', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://pirl.ethash-coins.ru', 'api':'http://pirl.ethash-coins.ru/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Ethash-Coins', 'fee':'1%', 'cloudflare':'false'},
  {'url':'http://pirl.coinminer.space', 'api':'http://pirl.coinminer.space/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Coinminer', 'fee':'0.1%', 'cloudflare':'false'},
  {'url':'https://pirl.reidocoin.com.br', 'api':'https://pirl.reidocoin.com.br/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Reidocoin', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://pirl.cryptopools.info', 'api':'http://pirl.cryptopools.info/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Cryptopools', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'https://pirl.zet-tech.eu', 'api':'https://pirl.zet-tech.eu/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Zet-Tech', 'fee':'0%', 'cloudflare':'false'}]

pegaArray = [
  {'url':'https://pega.litwiller.us', 'api':'https://pega.litwiller.us/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'CryptoPros', 'fee':'0.2%', 'cloudflare':'true'},
  {'url':'', 'api':'http://pgc.minerpool.net/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Minerpool', 'fee':'1%', 'cloudflare':'false'},
  {'url':'http://pgc.coinminer.space', 'api':'http://pgc.coinminer.space/api/stats', 'stats':'stats', 'blocks':'blocks/', 'name':'Coinminer', 'fee':'1%', 'cloudflare':'false'},
  {'url':'https://pgc.coin-miners.info', 'api':'https://pgc.coin-miners.info/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Coin-Miners', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://pgc.ethash-coins.ru', 'api':'http://pgc.ethash-coins.ru/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Ethash-Coins', 'fee':'1%', 'cloudflare':'false'},
  {'url':'http://pegas.cryptopools.info', 'api':'http://pegas.cryptopools.info/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'CryptoPools', 'fee':'1%', 'cloudflare':'false'}]
  # {'url':'https://dbix.zet-tech.eu', 'api':'https://dbix.zet-tech.eu/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Zet', 'fee':'0%', 'cloudflare':'false'}]

def openEthPool(poolArray, coin):

    headers = {
        'cache-control': "no-cache",
    }

    redisServer.delete(coin+':pools')

    #pirl stats
    if coin == "pirl":
        pRes = requests.request("GET", "https://pirl.site/api/stats", headers=headers)
        pRes = json.loads(pRes.text)
        coinHash = pRes['hashrate']
        redisServer.hset("stats", coin+"blocktime", format(pRes['blocktime'], '.2f'))
        redisServer.hset("stats", coin+"coinHashFull", coinHash)
        redisServer.hset("stats", coin+"coinHash", format(coinHash/1000000000.00, '.2f'))
        redisServer.hset("stats", coin+"price", format(pRes['price'], '.3f'))

    #pega stats
    if coin == "pega":
        pegaRes = requests.request("GET", "https://aikapool.com/pgc/index.php?page=api&action=getpoolstatus&api_key=d17748bb30a7f00f2739f8a9d4e79d965a273ef2ff8389ddcfa32417009e65a9", headers=headers)
        pegaRes = json.loads(pegaRes.text)
        pegaHash = float(pegaRes['getpoolstatus']['data']['nethashrate'])
        redisServer.hset("stats", coin+"Hash", pegaHash)
        redisServer.hset("stats", coin+"HashNice", format(pegaHash/1000000000, '.2f'))


    for p in poolArray:
        print(p['name'])
        redisServer.sadd(coin+':pools', p['name'])

    for pool in poolArray:
        try:
            url = pool['api']+pool['stats']
            response = requests.request("GET", url, headers=headers)
            response = json.loads(response.text)
            hashrateFull = long(response['hashrate'])

            if coin == "pirl":
                percentage = hashrateFull/coinHash
                percentage = '{:.3%}'.format(percentage)
                redisServer.hset(coin+":"+pool['name'], 'percentage', percentage)

            if coin == "pega":
                pegaper = hashrateFull/pegaHash
                pegaper = '{:.3%}'.format(pegaper)
                redisServer.hset(coin+":"+pool['name'], 'percentage', pegaper)

            hashrate = format(hashrateFull/1000000000.00, '.3f')
            blocks = response['maturedTotal']
            netblocks = response['nodes'][0]['height']
            miners = response['minersTotal']

            #add to redis
            redisServer.hset(coin+":"+pool['name'], 'name', pool['name'])
            redisServer.hset(coin+":"+pool['name'], 'hashrate', hashrate)
            redisServer.hset(coin+":"+pool['name'], 'hashrateFull', hashrateFull)
            redisServer.hset(coin+":"+pool['name'], 'miners', miners)
            redisServer.hset(coin+":"+pool['name'], 'blocks', blocks)
            redisServer.hset(coin+":"+pool['name'], 'netblocks', netblocks)
            redisServer.hset(coin+":"+pool['name'], 'status', "Live")
            redisServer.hset(coin+":"+pool['name'], 'url', pool['url'])
            redisServer.hset(coin+":"+pool['name'], 'fee', pool['fee'])

        except:
            print("no response from "+coin+" "+pool['name'])
            redisServer.hset(coin+":"+pool['name'], 'name', pool['name'])
            redisServer.hset(coin+":"+pool['name'], 'hashrate', 'N/A')
            redisServer.hset(coin+":"+pool['name'], 'miners', 'N/A')
            redisServer.hset(coin+":"+pool['name'], 'blocks', 'N/A')
            redisServer.hset(coin+":"+pool['name'], 'netblocks', 'N/A')
            redisServer.hset(coin+":"+pool['name'], 'status', "Live")
            redisServer.hset(coin+":"+pool['name'], 'url', pool['url'])
            redisServer.hset(coin+":"+pool['name'], 'fee', pool['fee'])

    print "main done"

openEthPool(dbixArray, "dbix")
openEthPool(pirlArray, "pirl")
openEthPool(pegaArray, "pega")
