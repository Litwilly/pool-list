var mappings = require('./mappings');
var pools = require('./pools');
var redis = require('redis');
var request = require('request');
var fs = require('fs');
var path = require('path');

var config = JSON.parse(JSON.minify(fs.readFileSync("config.json", {encoding: 'utf8'})));

var redisClient = redis.createClient(config.redis);

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

redisClient.on("error", function (err) {
    console.error("Error:", JSON.stringify(err));
});

redisClient.del("pools");

module.exports = function () {
    
    pools.forEach(function (pool) {
        console.log("INFO: Retrieving pool '" + pool.name + "' information.");
        var uri = pool.api + (pool.stats || 'stats');
        request.get(uri, function (err, response, body) {
            if (err) {
                reportDeadPool(pool);
                return console.error(err);
            }
            if (response.statusCode != 200) {
                reportDeadPool(pool);
                return console.warn("WARN: Cannot retrieve stats for pool '" + pool.name + "'. HTTP Status Code: " + response.statusCode);
            }

            var data = JSON.parse(body);

            var map = pool.mapping || 'znomp';
            var stats = mappings.stats[map](data, pool.poolkey);
            if (!stats) {            
                return reportDeadPool(pool);
            }
            addStatsToRedis(pool, stats);
            console.log("INFO: Pool '" + pool.name + "' stats successfully retrieved and saved.");

            console.log("INFO: Retrieving pool '" + pool.name + "' mined blocks.");
            var uri = pool.api + (pool.blocks || 'blocks');
            request.get(uri, function (err, response, body) {
                if (err) {
                    return console.error(err);
                }
                if (response.statusCode != 200) {
                    return console.warn("WARN: Cannot retrieve blocks for pool '" + pool.name + "'. HTTP Status Code: " + response.statusCode);
                }
                
                var data = JSON.parse(body);

                var map = pool.mapping || 'znomp';
                var lastMinedBlock = mappings.block[map](data, pool.poolkey);
                addLastMinedBlockToRedis(pool, lastMinedBlock || "None");
                console.log("INFO: Pool '" + pool.name + "' blocks successfully retrieved and saved.");
            });
        });
    });
}

function reportDeadPool(pool) {
    var commands = [
        [ "sadd", "pools", pool.name ],
        [ "hset", pool.name, 'name', pool.name ],
        [ "hset", pool.name, 'hashrate', "N/A" ],
        [ "hset", pool.name, 'hashnum', "N/A" ],
        [ "hset", pool.name, 'blocks', "N/A" ],
        [ "hset", pool.name, 'netblocks', "N/A" ],
        [ "hset", pool.name, 'workers', "N/A" ],
        [ "hset", pool.name, 'miners', "N/A" ],
        [ "hset", pool.name, 'status', "Unknown" ],
        [ "hset", pool.name, 'api', pool.url ],
        [ "hset", pool.name, 'fee', pool.fee >= 0 ? pool.fee + "%" : "N/A" ]
    ];
    redisClient.multi(commands).exec();
}

function addLastMinedBlockToRedis(pool, lastMinedBlock) {
    redisClient.hset(pool.name, 'mined', lastMinedBlock);
}

function addStatsToRedis(pool, stats) {
    var commands = [
        [ "sadd", "pools", pool.name ],
        [ "hset", pool.name, 'name', pool.name ],
        [ "hset", pool.name, 'hashrate', stats.hashrate ],
        [ "hset", pool.name, 'hashnum', stats.hashnum ],
        [ "hset", pool.name, 'blocks', stats.blocks ],
        [ "hset", pool.name, 'netblocks', stats.netblocks ],
        [ "hset", pool.name, 'workers', stats.workers ],
        [ "hset", pool.name, 'miners', stats.miners ],
        [ "hset", pool.name, 'status', "Live" ],
        [ "hset", pool.name, 'api', pool.url ],
        [ "hset", pool.name, 'fee', pool.fee >= 0 ? pool.fee + "%" : "N/A" ]
    ]
    redisClient.multi(commands).exec();
}
