var express = require('express');
var router = express.Router();
var fetch = require('node-fetch');
async = require("async");
var redis = require('redis');
var fs = require('fs');

// var Web3 = require('web3');
// var web3 = new Web3();
// web3.setProvider(new web3.providers.HttpProvider('http://localhost:8545'));
//
// var coinbase = web3.eth.coinbase;
// console.log(coinbase);
//
// var balance = web3.eth.getBalance(coinbase);
// console.log(balance.toString(10));

JSON.minify = JSON.minify || require("node-json-minify");

var config = JSON.parse(JSON.minify(fs.readFileSync("config.json", {encoding: 'utf8'})));
var redisConfig = config.redis;

connection = redis.createClient({host:redisConfig.host, port: redisConfig.port, db: redisConfig.db});
connection.auth(redisConfig.password);
connection.on('connect', function() {
    console.log('connected');
});

/* GET home page. */
router.get('/', function(req, res, next) {
var pools = [];
connection.smembers('btg:pools', function(err, poolList) {
  async.each(poolList,
    function(pA, callback){
      connection.hgetall('btg:'+pA, function(err, stats) {
          pools.push({
            "hashnum": stats.hashnumnice,
            "name": stats.name,
            "blocks": stats.blocks,
            "workers": stats.workers,
            "miners": stats.miners,
            "netblocks": stats.netblocks,
            "url": stats.url,
            "fee": stats.fee,
            "mined": stats.mined,
            "percentage": stats.percentage,
            "status": stats.status
          });
          callback();
      });
  },
  function(err){
    var dbixPool = [];
    connection.smembers('dbix:pools', function(err, poolList) {
      async.each(poolList,
        function(pA, callback){
          connection.hgetall('dbix:'+pA, function(err, stats) {
              dbixPool.push({
                "hash": stats.hashrate,
                "name": stats.name,
                "blocks": stats.blocks,
                "miners": stats.miners,
                "netblocks": stats.netblocks,
                "url": stats.url,
                "fee": stats.fee,
                "status": stats.status
              });
              callback();
          });
      },
      function(err){
        var pirlPool = [];
        connection.smembers('pirl:pools', function(err, poolList) {
          async.each(poolList,
            function(pA, callback){
              connection.hgetall('pirl:'+pA, function(err, stats) {
                  pirlPool.push({
                    "hash": stats.hashrate,
                    "name": stats.name,
                    "blocks": stats.blocks,
                    "miners": stats.miners,
                    "netblocks": stats.netblocks,
                    "url": stats.url,
                    "fee": stats.fee,
                    "status": stats.status,
                    "percentage": stats.percentage
                  });
                  callback();
              });
          },
          function(err){
            var pegaPool = [];
            connection.smembers('pega:pools', function(err, poolList) {
              async.each(poolList,
                function(pA, callback){
                  connection.hgetall('pega:'+pA, function(err, stats) {
                      pegaPool.push({
                        "hash": stats.hashrate,
                        "name": stats.name,
                        "blocks": stats.blocks,
                        "miners": stats.miners,
                        "netblocks": stats.netblocks,
                        "url": stats.url,
                        "fee": stats.fee,
                        "percentage": stats.percentage,
                        "status": stats.status
                      });
                      callback();
                  });
              },
              function(err){
                var crcPool = [];
                connection.smembers('crc:pools', function(err, poolList) {
                  async.each(poolList,
                    function(pA, callback){
                      connection.hgetall('crc:'+pA, function(err, stats) {
                          crcPool.push({
                            "hash": stats.hash,
                            "name": stats.name,
                            // "blocks": stats.block,
                            // "miners": stats.miners,
                            "netblocks": stats.block,
                            // "url": stats.url,
                            "fee": stats.fee,
                            "percentage": stats.percent,
                            "ttf": stats.ttf
                          });
                          callback();
                      });
                  },
                  function(err){
                    var empty = ["one"];
                    var pirlPoolStats = [];
                    var btgPoolStats = [];
                    var pegaPoolStats = [];
                    var crcPoolStats = [];
                    connection.hgetall('stats', function(err, stats) {
                      async.each(empty,
                        function(pA, callback){
                              pirlPoolStats.push({
                                "blocktime": stats.pirlblocktime,
                                "coinHash": stats.pirlcoinHash,
                                "price": stats.pirlprice
                              });
                              btgPoolStats.push({
                                "coinHash": stats.btgcoinHash,
                                "btgprice": stats.btgprice,
                                "netDiff": stats.btgnetDiff
                              });
                              pegaPoolStats.push({
                                "coinHash": (stats.pegaHashNice)
                              });
                              crcPoolStats.push({
                                "coinHash": (stats.crcnethash),
                                "coinDiff": (stats.crcdiff)
                              });
                              callback();

                      },
                      function(err){
                          res.render('index',
                            { title: 'Express',
                              pools: pools,
                              dbixPool: dbixPool,
                              pirlPool: pirlPool,
                              crcPool: crcPool,
                              pirlPoolStats: pirlPoolStats,
                              btgPoolStats: btgPoolStats,
                              pegaPoolStats: pegaPoolStats,
                              crcPoolStats: crcPoolStats,
                              pegaPool: pegaPool});
                          });
                        });
                      });
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  }
);

module.exports = router;
