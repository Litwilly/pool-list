module.exports = 
{

    /* Contract

    {
        hashrate,
        hashnum,
        blocks,
        netblocks,
        workers,
        miners
    }

    */

    stats: {
        znomp: function (data, poolKey) {
            return {
                hashrate: data.pools[poolKey].hashrateString,
                hashnum: data.pools[poolKey].hashrate,
                blocks: data.pools[poolKey].poolStats.validBlocks,
                netblocks: data.pools[poolKey].poolStats.networkBlocks,
                workers: data.pools[poolKey].workerCount,
                miners: data.pools[poolKey].minerCount
            }
        },
        btgminers: function (data) {
            return {
                hashrate: data.solrate.total,
                hashnum: data.hashrate.total,
                blocks: data.stats.validBlocks,
                netblocks: data.stats.networkBlocks,
                workers: data.totalWorkers,
                miners: data.totalMiners
            }
        }
    },

    block: {
        znomp: function (data, poolKey) {
            var blocks = [];
            Object.keys(data).forEach(function (id) {
                if (id.indexOf(poolKey) == 0) {
                    blocks.push(parseInt(id.substring(poolKey.length + 1)));
                }
            });
            // get last mined block
            return blocks.sort().pop();
        },
        btgminers: function (data) {
            // TODO: will implement when first block is found :)
        }
    }
};
