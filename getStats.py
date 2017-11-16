#!/usr/bin/python
import urllib
from urllib import urlencode
import redis
import json


#Config Redis server we're connecting to
pool = redis.ConnectionPool( host='127.0.0.1', port=6379,password='',db=1 )
redisServer = redis.Redis( connection_pool=pool )
pipe = redisServer.pipeline()

# 2D array group name used in Redis key
poolArray = [
#commented these pools because they are behind cloudflare.
  {'url':'https://btg.cryptopros.us', 'api':'http://btg.cryptopros.us/api/stats', 'name':'CryptoPros', 'poolkey':'bitcoin-gold'},
#  {'url':'http://pool.miningspeed.com', 'api':'http://pool.miningspeed.com/api/stats/', 'name':'Miningspeed', 'poolkey':'bitcoingold'},
  {'url':'http://btg.nibirupool.com', 'api':'http://btg.nibirupool.com/api/stats/', 'name':'Nibirupool', 'poolkey':'bitcoin gold'},
  {'url':'http://btg.cloudhash.eu', 'api':'http://btg.cloudhash.eu/api/stats/', 'name':'CloudHash', 'poolkey':'bitcoin gold'},
  {'url':'https://pool.serverpower.net', 'api':'https://pool.serverpower.net/api/stats/', 'name':'ServerPower', 'poolkey':'bitcoin_gold'},
  {'url':'http://btgpool.pro', 'api':'http://btgpool.pro/api/stats/', 'name':'BTGPool.Pro', 'poolkey':'bgold'},
  {'url':'http://lucky-mining.com.ua', 'api':'http://lucky-mining.com.ua/api/stats/', 'name':'Lucky-Mining[RU]', 'poolkey':'bitcoingold'},
  {'url':'https://multipool.es', 'api':'https://multipool.es/api/stats/', 'name':'Multipool[ES]', 'poolkey':'bitcoin gold'},
  {'url':'https://pool.4miner.me', 'api':'https://pool.4miner.me:8085/api/stats/', 'name':'4miner.me', 'poolkey':'bitcoin gold'},
  {'url':'http://savspool.mine.nu/', 'api':'http://savspool.mine.nu/api/stats/', 'name':'Savspool', 'poolkey':'bitcoin gold'},
  {'url':'http://bgold.mining4.co.uk', 'api':'http://bgold.mining4.co.uk/api/stats/', 'name':'Mining4', 'poolkey':'bitcoin gold'},
#  {'url':'https://gpool.guru', 'api':'https://gpool.guru/api/stats', 'name':'Gpool.guru', 'poolkey':'btg'},
  {'url':'http://bitcoingoldpool.cloud', 'api':'http://bitcoingoldpool.cloud/api/stats/', 'name':'Miningpools.cloud', 'poolkey':'btcgold'}]

#reset pool list hash
redisServer.delete('pools')

for p in poolArray:
    redisServer.sadd('pools', p['name'])

for pool in poolArray:
    try:
        response = json.loads(urllib.urlopen(pool['api']).read())
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
        redisServer.hset(pool['name'], 'url', pool['url'])

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
        redisServer.hset(pool['name'], 'url', pool['url'])

print "main done"
