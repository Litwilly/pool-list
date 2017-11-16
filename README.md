# pool-list

Requires Node, Redis-Server, and getStats.py to be setup with a cron-job to refresh stats.

### Cron Example
```
*/5  *  *  *  * /usr/bin/python [location of script]/getStats.py
```

Add redis connection to config.json and getStats.py

```
git clone https://github.com/litwi1rm/pool-list.git
cd pool-list
npm install
npm start
```

Reload file changes
```
npm install -g nodemon
npm run nodemon
```

Reload file changes and forever
```
npm install -g nodemon
npm install -g forever
npm run fnodemon
```

## TO-DO
1. Migrate getStats.py to node script with something like node-schedule
2. Move Pool list to config.JSON
3. Fix Tablesorter
