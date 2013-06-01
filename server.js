/*
 *   This file is part of TyeDye.
 *
 *   TyeDye is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   TyeDye is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with TyeDye.  If not, see <http://www.gnu.org/licenses/>. 
 *
 *   TyeDye by Jose Carlos Cuevas Albadalejo <reset.reboot@gmail.com>
 *
 */

var express = require('express')
    , stylus = require('stylus')
    , nib = require('nib')
    , sqlite = require('sqlite3');

var app = express();

var database = new sqlite.Database('/home/reset/tyedye/game.db');

// Custom compile function for using nib alongside stylus
function compile(str, path) {
    return stylus(str)
        .set('filename', path)
        .use(nib());
}

app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.logger('dev'))
app.use(stylus.middleware(
            { src: __dirname + '/public',
              compile: compile
            }
            ));

// Let express serve static files
app.use(express.static(__dirname + '/public'));

// Simple test call
// app.get('/', function (req, res) {
//     res.send('Hi there!!');
// });

app.get('/', function (req, res) {
    var player_number = 0;
    var stats_number = 0;
    var players = new Array();

    console.log('Serializing');
    database.serialize(function() {
        console.log('Querying players');
        database.each("SELECT * FROM players", function(err, row) {
            console.log('Received a player row! Weheeeee!');
            var nextElement = players.length;
            players[nextElement] = row.name;
            console.log(players);
        });

        database.get("SELECT COUNT(*) FROM players", function (err, row) {
            player_number = row;
        });
        database.get("SELECT COUNT(*) FROM stats", function (err, row) {
            stats_number = row;
        });

        res.render('index',
            {
                title: 'My Game',
                player_num: player_number,
                stats_num: stats_number,
                player_list: players
            });
    });
});

app.listen(3000);
