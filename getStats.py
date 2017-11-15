#!/usr/bin/python
import pycurl
import re
import urllib
import os
from urllib import urlencode
from io import BytesIO
from StringIO import StringIO
import sys
import redis
import time
import json
from datetime import datetime




#Config Redis server we're connecting to
pool = redis.ConnectionPool( host='127.0.0.1', port=6379,password='',db=1 )
redisServer = redis.Redis( connection_pool=pool )
pipe = redisServer.pipeline()

# 2D array group name used in Redis key, and groups fitbit URL
poolArray = [
  {'url':'https://btg.cryptopros.us', 'api':'http://btg.cryptopros.us/api/stats', 'name':'CryptoPros', 'poolkey':'bitcoin-gold'},
  {'url':'https://pool.miningspeed.com', 'api':'https://pool.miningspeed.com/api/stats', 'name':'Miningspeed', 'poolkey':'bitcoingold'},
  {'url':'http://btg.nibirupool.com', 'api':'http://btg.nibirupool.com/api/stats', 'name':'Nibirupool', 'poolkey':'bitcoin gold'},
  {'url':'http://btg.cloudhash.eu', 'api':'http://btg.cloudhash.eu/api/stats', 'name':'CloudHash', 'poolkey':'bitcoin gold'},
  {'url':'https://pool.serverpower.net', 'api':'https://pool.serverpower.net/api/stats', 'name':'ServerPower', 'poolkey':'bitcoin_gold'},
  {'url':'http://btgpool.pro', 'api':'http://btgpool.pro/api/stats', 'name':'BTGPool.Pro', 'poolkey':'bgold'},
  {'url':'http://lucky-mining.com.ua', 'api':'http://lucky-mining.com.ua/api/stats/', 'name':'Lucky-Mining[RU]', 'poolkey':'bitcoingold'},
  {'url':'https://coinblockers.com', 'api':'https://coinblockers.com/api/stats/', 'name':'Coinblockers', 'poolkey':'bitcoin gold'},
  {'url':'http://btgmine.org', 'api':'http://btgmine.org/api/stats/', 'name':'BTGMine', 'poolkey':'bitcoin gold'},
  {'url':'https://multipool.es', 'api':'https://multipool.es/api/stats/', 'name':'Multipool[ES]', 'poolkey':'bitcoin gold'}]


date = time.strftime("%Y-%m-%d")
redisServer.delete('pools')

for pool in poolArray:
    try:
        response = json.loads(urllib.urlopen(pool['api']).read())
        hashrate = response['pools'][pool['poolkey']]['hashrateString'];
        blocks = response['pools'][pool['poolkey']]['poolStats']['validBlocks'];
        netblocks = response['pools'][pool['poolkey']]['poolStats']['networkBlocks'];
        workers = response['pools'][pool['poolkey']]['workerCount'];

        #add to redis
        redisServer.hset(pool['name'], 'name', pool['name'])
        redisServer.hset(pool['name'], 'hashrate', hashrate)
        redisServer.hset(pool['name'], 'blocks', blocks)
        redisServer.hset(pool['name'], 'netblocks', netblocks)
        redisServer.hset(pool['name'], 'workers', workers)
        redisServer.hset(pool['name'], 'status', "Live")
        redisServer.sadd('pools', pool['name'])

    except:
        print "no response from "+ pool['name']
        redisServer.hset(pool['name'], 'name', pool['name'])
        redisServer.hset(pool['name'], 'hashrate', 'n/a')
        redisServer.hset(pool['name'], 'blocks', 'n/a')
        redisServer.hset(pool['name'], 'netblocks', 'n/a')
        redisServer.hset(pool['name'], 'workers', 'n/a')
        redisServer.hset(pool['name'], 'status', "n/a")
        redisServer.sadd('pools', pool['name'])


print "main done"
