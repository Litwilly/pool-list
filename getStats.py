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

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

#Config Redis server we're connecting to
pool = redis.ConnectionPool( host='127.0.0.1', port=6379,password='',db=1 )
redisServer = redis.Redis( connection_pool=pool )
pipe = redisServer.pipeline()

# 2D array group name used in Redis key
poolArray = [
{'url':'https://btg.cryptopros.us', 'api':'https://btg.cryptopros.us/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'CryptoPros', 'poolkey':'bitcoin-gold', 'fee':'0.0%'},
# cloudflare {'url':'http://pool.miningspeed.com', 'stats':'stats/', 'blocks':'blocks/', 'name':'Miningspeed', 'poolkey':'bitcoingold'},
  {'url':'https://btg.poool.io', 'api':'https://btg.poool.io/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Pool.io', 'poolkey':'bitcoin gold', 'fee':'1%'},
  {'url':'http://btg.cloudhash.eu', 'api':'http://btg.cloudhash.eu/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'CloudHash', 'poolkey':'bitcoin gold', 'fee':'1%'},
  {'url':'http://btg.nibirupool.com', 'api':'http://btg.nibirupool.com/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Nibirupool', 'poolkey':'bitcoin gold', 'fee':'1%'},
  {'url':'https://pool.serverpower.net', 'api':'https://pool.serverpower.net/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'ServerPower', 'poolkey':'bitcoin_gold', 'fee':'0.5%'},
  {'url':'http://btgpool.pro', 'api':'http://btgpool.pro/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'BTGPool.Pro', 'poolkey':'bgold', 'fee':'N/A'},
  {'url':'http://lucky-mining.com.ua', 'api':'http://lucky-mining.com.ua/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Lucky-Mining[RU]', 'poolkey':'bitcoingold', 'fee':'0.0%'},
  {'url':'https://multipool.es', 'api':'https://multipool.es/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Multipool[ES]', 'poolkey':'bitcoin gold', 'fee':'0.25%'},
  {'url':'http://savspool.mine.nu', 'api':'http://savspool.mine.nu/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Savspool', 'poolkey':'bitcoin gold', 'fee':'1%'},
  {'url':'http://bgold.mining4.co.uk', 'api':'http://bgold.mining4.co.uk/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Mining4', 'poolkey':'bitcoin gold', 'fee':'0.25%'},
  {'url':'http://kulturmining.com', 'api':'http://kulturmining.com/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'KulturMining', 'poolkey':'bitcoin gold', 'fee':'0.7%'},
  {'url':'http://btg.goldenshow.io', 'api':'http://btg.goldenshow.io/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'GoldenShow', 'poolkey':'bitcoin gold', 'fee':'1%'},
  {'url':'http://pool.gold', 'api':'https://stat.pool.gold/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Pool.Gold', 'poolkey':'bitcoin gold', 'fee':'0.0%'},
# cloudflare {'url':'https://gpool.guru', 'stats':'stats/', 'blocks':'blocks/', 'name':'Gpool.guru', 'poolkey':'btg'},
  {'url':'http://bitcoingoldpool.cloud', 'api':'http://bitcoingoldpool.cloud/api/', 'stats':'stats/', 'blocks':'blocks/', 'name':'Miningpools.cloud', 'poolkey':'btcgold', 'fee':'0.0%'}]


redisServer.delete('pools')

for p in poolArray:
    print(p['name'])
    redisServer.sadd('pools', p['name'])

for pool in poolArray:
    try:
        response = json.loads(urllib.urlopen(pool['api']+pool['stats']).read())
        hashrate = response['pools'][pool['poolkey']]['hashrateString']
        hashnum = response['pools'][pool['poolkey']]['hashrate']
        blocks = response['pools'][pool['poolkey']]['poolStats']['validBlocks']
        netblocks = response['pools'][pool['poolkey']]['poolStats']['networkBlocks']
        workers = response['pools'][pool['poolkey']]['workerCount']
        miners = response['pools'][pool['poolkey']]['minerCount']

        #add to redis
        redisServer.hset(pool['name'], 'name', pool['name'])
        redisServer.hset(pool['name'], 'hashrate', hashrate)
        redisServer.hset(pool['name'], 'hashnum', hashnum)
        redisServer.hset(pool['name'], 'blocks', blocks)
        redisServer.hset(pool['name'], 'netblocks', netblocks)
        redisServer.hset(pool['name'], 'workers', workers)
        redisServer.hset(pool['name'], 'miners', miners)
        redisServer.hset(pool['name'], 'status', "Live")
        redisServer.hset(pool['name'], 'api', pool['url'])
        redisServer.hset(pool['name'], 'fee', pool['fee'])

    except:
        print("no response from "+ pool['name'])
        redisServer.hset(pool['name'], 'name', pool['name'])
        redisServer.hset(pool['name'], 'hashrate', 'n/a')
        redisServer.hset(pool['name'], 'hashnum', 0)
        redisServer.hset(pool['name'], 'blocks', 'n/a')
        redisServer.hset(pool['name'], 'netblocks', 'n/a')
        redisServer.hset(pool['name'], 'workers', 'n/a')
        redisServer.hset(pool['name'], 'miners', 'n/a')
        redisServer.hset(pool['name'], 'status', "n/a")
        redisServer.hset(pool['name'], 'api', pool['url'])
        redisServer.hset(pool['name'], 'fee', pool['fee'])

    try:
        resBlocks = json.loads(urllib.urlopen(pool['api']+pool['blocks']).read())
        if not resBlocks:
            redisServer.hset(pool['name'], 'mined', 'None')
            print("no blocks from "+ pool['name'])
        else:
            blockArray = []
            for lb in resBlocks.keys():
                blockArray.append(lb.encode('ascii','ignore'))
            blockArray.sort(reverse=True)
            lastBlock = blockArray[0]
            redisServer.hset(pool['name'], 'mined', lastBlock)
            print(lastBlock)
    except:
        print("no block response from "+ pool['name'])
        redisServer.hset(pool['name'], 'mined', 'N/A')

print "main done"
