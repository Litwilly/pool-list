var express = require('express');
var router = express.Router();
var fetch = require('node-fetch');
async = require("async");
var redis = require('redis');
var fs = require('fs');
JSON.minify = JSON.minify || require("node-json-minify");

var config = JSON.parse(JSON.minify(fs.readFileSync("config.json", {encoding: 'utf8'})));
var redisConfig = config.redis;

connection2 = redis.createClient({host:redisConfig.host, port: redisConfig.port, db:redisConfig.db});
connection2.auth(redisConfig.password);
connection2.on('connect', function() {
    console.log('connected');
});

/* GET home page. */
router.get('/', function(req, res, next) {
var pools = [];
connection2.smembers('btg:pools', function(err, poolList) {
  async.each(poolList,
    function(pA, callback){
      connection2.hgetall('btg:'+pA, function(err, stats) {
          pools.push({
            "hash": stats.hashrate,
            "hashnum": stats.hashnum,
            "name": stats.name,
            "blocks": stats.blocks,
            "workers": stats.workers,
            "miners": stats.miners,
            "netblocks": stats.netblocks,
            "url": stats.url,
            "fee": stats.fee,
            "mined": stats.mined,
            "status": stats.status,
            "validShares": stats.validShares,
            "shareCount": stats.shareCount
          });
          callback();
      });
  },
  function(err){
      res.render('extra',
        { title: 'Express',
          pools: pools});
      });
    });
  }
);

module.exports = router;
