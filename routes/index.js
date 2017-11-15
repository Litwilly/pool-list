var express = require('express');
var router = express.Router();
var fetch = require('node-fetch');
async = require("async");
var redis = require('redis');
var fs = require('fs');
JSON.minify = JSON.minify || require("node-json-minify");

var config = JSON.parse(JSON.minify(fs.readFileSync("config.json", {encoding: 'utf8'})));
var redisConfig = config.redis;

connection = redis.createClient({host:redisConfig.host, port: redisConfig.port, db:redisConfig.db});
connection.auth(redisConfig.password);
connection.on('connect', function() {
    console.log('connected');
});

/* GET home page. */
router.get('/', function(req, res, next) {
var pools = [];
connection.smembers('pools', function(err, poolList) {
  async.each(poolList,
    function(pA, callback){
      connection.hgetall(pA, function(err, stats) {
          pools.push({
            "hash": stats.hashrate,
            "name": stats.name,
            "blocks": stats.blocks,
            "workers": stats.workers,
            "netblocks": stats.netblocks,
            "url": stats.url,
            "status": stats.status
          });
          callback();
      });
  },
  function(err){
      res.render('index',
        { title: 'Express',
          pools: pools});
      });
    });
  }
);

module.exports = router;
