#!/usr/bin/python
import os
import sys
import redis
import json
import ssl
import re
import requests
import urllib
import urllib2
from urllib import urlencode

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

#Config Redis server we're connecting to
pool = redis.ConnectionPool( host='127.0.0.1', port=6379, password='', db=2 )
redisServer = redis.Redis( connection_pool=pool )
pipe = redisServer.pipeline()

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'}

# Network stats
coin = "btg"
pRes = requests.request("GET", "https://btg.cryptopros.us/api/stats", headers=headers)
pRes = json.loads(pRes.text)
netHash = pRes['pools']['bitcoin-gold']['poolStats']['networkSols']
netDiff = pRes['pools']['bitcoin-gold']['poolStats']['networkDiff']
netHashNice = float(netHash)/100000.00
cm = requests.request("GET", "https://api.coinmarketcap.com/v1/ticker/bitcoin-gold/", headers=headers)
cm = json.loads(cm.text)
btgPrice = cm[0]['price_usd']
redisServer.hset("stats", coin+"netDiff", format(float(netDiff), '.0f'))
redisServer.hset("stats", coin+"coinHashFull", netHash)
redisServer.hset("stats", coin+"coinHash", format(float(netHash)/1000000.00, '.2f'))
redisServer.hset("stats", coin+"price", btgPrice)

redisServer.delete('btg:pools')

#Suprnova
try:
    res = requests.request("GET", "https://btg.suprnova.cc/index.php?page=api&action=getpoolstatus&api_key=d5ecb8199bb1868732179a86f00db9a1fd3e21fb75d1c22ffd5ec14eb5b83a88", headers=headers)
    res = json.loads(res.text)
    snhash = float(res['getpoolstatus']['data']['hashrate'])
    snnethash = float(netHash)
    snpercent = format(snhash/(snnethash*10), '.2f')
    redisServer.hset("btg:Suprnova", 'name', "Supernova")
    redisServer.hset("btg:Suprnova", 'hashnumnice', format(snhash/1000000, '.3f'))
    redisServer.hset("btg:Suprnova", 'hashrate', format(snhash/1000000, '.3f'))
    redisServer.hset("btg:Suprnova", 'percentage', snpercent)
    redisServer.hset("btg:Suprnova", 'blocks', 'N/A')
    redisServer.hset("btg:Suprnova", 'netblocks', res['getpoolstatus']['data']['currentnetworkblock'])
    redisServer.hset("btg:Suprnova", 'validShares', 'N/A')
    redisServer.hset("btg:Suprnova", 'shareCount', 'N/A')
    redisServer.hset("btg:Suprnova", 'miners', res['getpoolstatus']['data']['workers'])
    redisServer.hset("btg:Suprnova", 'status', "Live")
    redisServer.hset("btg:Suprnova", 'url', 'https://btg.suprnova.cc')
    redisServer.hset("btg:Suprnova", 'fee', '1%')
    redisServer.sadd('btg:pools', 'Suprnova')
except:
    redisServer.hset("btg:Suprnova", 'status', "Dead")
    redisServer.sadd('btg:pools', 'Suprnova')


# 2D array group name used in Redis key
poolArray = [
  {'url':'https://btg.cryptopros.us', 'api':'https://btg.cryptopros.us/api/', 'stats':'stats', 'blocks':'blocks', 'name':'CryptoPros', 'poolkey':'bitcoin-gold', 'fee':'0%', 'cloudflare':'false'},
  {'url':'http://btg.cloudhash.eu', 'api':'http://btg.cloudhash.eu/api/', 'stats':'stats', 'blocks':'blocks', 'name':'CloudHash', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  {'url':'http://btg.nibirupool.com', 'api':'http://btg.nibirupool.com/api/', 'stats':'stats', 'blocks':'blocks', 'name':'Nibirupool', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  {'url':'https://pool.serverpower.net', 'api':'https://pool.serverpower.net/api/', 'stats':'stats', 'blocks':'blocks', 'name':'ServerPower', 'poolkey':'bitcoin_gold', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'http://btgpool.pro', 'api':'http://btgpool.pro/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'BTGPool.Pro', 'poolkey':'bgold', 'fee':'0.5%', 'cloudflare':'false'},
  {'url':'https://multipool.es', 'api':'https://multipool.es/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Multipool[ES]', 'poolkey':'bitcoin gold', 'fee':'0.25%', 'cloudflare':'false'},
  {'url':'http://bgold.mining4.co.uk', 'api':'http://bgold.mining4.co.uk/api/', 'stats':'stats', 'blocks':'blocks', 'name':'Mining4', 'poolkey':'bitcoin gold', 'fee':'0.25%', 'cloudflare':'false'},
  {'url':'http://btg.goldenshow.io', 'api':'http://btg.goldenshow.io/api/', 'stats':'stats', 'blocks':'blocks', 'name':'GoldenShow', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  {'url':'http://pool.gold', 'api':'https://stat.pool.gold/api/', 'stats':'stats', 'blocks':'blocks', 'name':'Pool.Gold', 'poolkey':'bitcoin gold', 'fee':'0%', 'cloudflare':'false'},
  {'url':'https://coinblockers.com', 'api':'http://173.212.207.13/api/', 'stats':'stats', 'blocks':'blocks', 'name':'CoinBlockers', 'poolkey':'bitcoin-gold', 'fee':'0%', 'cloudflare':'false'},
  {'url':'https://btgminers.eu', 'api':'http://btgminers.eu/api/', 'stats':'znomp_compatibility', 'blocks':'blocks', 'name':'BTGMiners.eu', 'poolkey':'btgminers.eu', 'fee':'1%'},
  {'url':'http://bitcoingoldpool.cloud', 'api':'http://bitcoingoldpool.cloud/api/', 'stats':'stats', 'blocks':'blocks', 'name':'Miningpools.cloud', 'poolkey':'btcgold', 'fee':'0%', 'cloudflare':'false'}]
  # {'url':'https://btg.poool.io', 'api':'https://btg.poool.io/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Pool.io', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  # {'url':'http://lucky-mining.com.ua', 'api':'http://lucky-mining.com.ua/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Lucky-Mining[RU]', 'poolkey':'bitcoingold', 'fee':'0%', 'cloudflare':'false'},
  # {'url':'https://pool.4miner.me', 'api':'https://pool.4miner.me:8085/api/', 'stats':'stats', 'blocks':':8085blocks/', 'name':'4miner.me', 'poolkey':'bitcoin gold', 'fee':'1%'},
  #{'url':'https://savspool.com', 'api':'http://178.239.54.250/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Savspool', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  # {'url':'http://www.gpucryptopool.com', 'api':'http://138.197.3.37/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'GPUCryptoPool', 'poolkey':'bitcoin gold', 'fee':'0%', 'cloudflare':'false'},
  # {'url':'http://kulturmining.com', 'api':'http://kulturmining.com/api/', 'stats':'stats', 'blocks':'blocks', 'name':'KulturMining', 'poolkey':'bitcoin gold', 'fee':'0.7%', 'cloudflare':'false'},
  # {'url':'http://btg.pool.sexy', 'api':'http://btg.pool.sexy/api3/', 'stats':'stats', 'blocks':'blocks/', 'name':'Pool.sexy', 'poolkey':'bitcoin gold', 'fee':'0%', 'cloudflare':'true'},
  # {'url':'https://gpugold.com', 'api':'https://gpugold.com/api/', 'stats':'stats', 'blocks':'blocks', 'name':'GPU Gold', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  # {'url':'http://btgold.west-pool.org:8080', 'api':'http://btgold.west-pool.org:8080/api/', 'stats':'stats', 'blocks':'blocks', 'name':'WestPool', 'poolkey':'bitcoin gold', 'fee':'1%', 'cloudflare':'false'},
  # {'url':'https://pool.miningspeed.com', 'api':'https://pool.miningspeed.com/api/', 'stats':'stats', 'blocks':'blocks/', 'name':'Miningspeed', 'poolkey':'bitcoingold', 'fee':'0.4%', 'cloudflare':'true'},
  # {'url':'https://gpool.guru', 'api':'https://gpool.guru/api/', 'stats':'stats', 'blocks':'blocks', 'name':'Gpool.guru', 'poolkey':'btg', 'fee': '1%', 'cloudflare':'true'},


for p in poolArray:
    print(p['name'])
    redisServer.sadd('btg:pools', p['name'])


for pool in poolArray:
    try:
        request = urllib2.Request(pool['api']+pool['stats'], headers=headers)
        response = json.loads(urllib2.urlopen(request).read())

        hashrate = response['pools'][pool['poolkey']]['hashrateString']
        hashnum = response['pools'][pool['poolkey']]['hashrate']
        blocks = response['pools'][pool['poolkey']]['poolStats']['validBlocks']
        netblocks = response['pools'][pool['poolkey']]['poolStats']['networkBlocks']
        workers = response['pools'][pool['poolkey']]['workerCount']
        miners = response['pools'][pool['poolkey']]['minerCount']
        # validShares = response['pools'][pool['poolkey']]['poolStats']['validShares'] #btgminers.eu doesn't have
        # shareCount = response['pools'][pool['poolkey']]['shareCount'] #btgminers.eu doesn't have
        percentage = format((hashnum/500000000)/netHashNice, '.2f')
        print(percentage)

        #add to redis
        redisServer.hset("btg:"+pool['name'], 'name', pool['name'])
        redisServer.hset("btg:"+pool['name'], 'hashrate', hashrate)
        redisServer.hset("btg:"+pool['name'], 'hashnum', hashnum)
        redisServer.hset("btg:"+pool['name'], 'hashnumnice', format(hashnum/500000000, '.3f'))
        redisServer.hset("btg:"+pool['name'], 'percentage', percentage)
        redisServer.hset("btg:"+pool['name'], 'blocks', blocks)
        redisServer.hset("btg:"+pool['name'], 'netblocks', netblocks)
        redisServer.hset("btg:"+pool['name'], 'workers', workers)
        redisServer.hset("btg:"+pool['name'], 'validShares',"0")
        redisServer.hset("btg:"+pool['name'], 'shareCount', "0")
        redisServer.hset("btg:"+pool['name'], 'miners', miners)
        redisServer.hset("btg:"+pool['name'], 'status', "Live")
        redisServer.hset("btg:"+pool['name'], 'url', pool['url'])
        redisServer.hset("btg:"+pool['name'], 'fee', pool['fee'])

    except:
        print("no response from "+ pool['name'])
        redisServer.hset("btg:"+pool['name'], 'name', pool['name'])
        redisServer.hset("btg:"+pool['name'], 'hashrate', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'hashnum', 0)
        redisServer.hset("btg:"+pool['name'], 'blocks', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'netblocks', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'workers', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'validShares', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'shareCount', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'miners', 'n/a')
        redisServer.hset("btg:"+pool['name'], 'status', "n/a")
        redisServer.hset("btg:"+pool['name'], 'url', pool['url'])
        redisServer.hset("btg:"+pool['name'], 'fee', pool['fee'])

    #Decode Last Block
    try:
        resBlocks = json.loads(urllib.urlopen(pool['api']+pool['blocks']).read())
        if not resBlocks:
            redisServer.hset("btg:"+pool['name'], 'mined', '0')
            print("no blocks from "+ pool['name'])
        else:
            blockArray = []
            for lb in resBlocks.keys():
                if "b" in lb and "z" not in lb:
                    blockArray.append(lb.encode('ascii','ignore'))
            blockArray.sort(reverse=True)
            str = blockArray[0]
            lastBlock = re.findall(r'\d+', str)
            redisServer.hset("btg:"+pool['name'], 'mined', lastBlock[0])
            print(lastBlock[0])
    except:
        print("no block response from "+ pool['name'])
        redisServer.hset("btg:"+pool['name'], 'mined', 'N/A')

print "main done"
