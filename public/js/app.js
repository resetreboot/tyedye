// Model definition

var Stat = Backbone.Model.extend({
      urlRoot: '/tyedye/stat/',
      defaults: {
            name: 'New Stat',
            value: 0,
            default_value: 0,
      },
      initialize: function () {
        this.on("change", function(model) {});
      }
});

var Stats = Backbone.Collection.extend({
    model: Stat,
    url: function () {
        if (this.generic) {
            return "/tyedye/stats/";
        } else {
            return "/tyedye/stats/" + this.id;
        }
    },
    initialize: function (models, player_id) {
        this.generic = true;
        if (typeof player_id != 'undefined') {
            this.id = player_id;
            this.generic = false;
        }
        this.fetch({ reset: true });
        if (!this.generic) {
            this.on('reset', function () {
                this.each(function (statistic) {
                    $("#player_stats" + this.id )
                      .append('<label>' + statistic.name + '</label><input type="text" name="' + statistic.name + this.id + '">');
                });
            });
        }
    }
});

var Player = Backbone.Model.extend({
    urlRoot: '/tyedye/player/',
    defaults: {
            name: 'New Player',
            stats: new Stats,
            code: 0,
    },
    initialize: function () {
        // this.on("change", function (model) {});
        if (this.get('code') != 0) {
            var player_stats = new Stats([], this.get('code'));
            this.set('stats', player_stats);
        }
    }
});

var Players = Backbone.Collection.extend({
    model: Player,
    url: "/tyedye/players/",
    initialize: function () {
        this.fetch({ reset: true });
    }
});

var stats = new Stats;
var players = new Players; 

// Routers

var MainRouter = Backbone.Router.extend({
    routes: {
        ""                      : "index",
        "player/:player_id"     : "player_detail",
    },
    index: function () { ;; },
    player_detail: function () { ;; }
});

var main_router = MainRouter;

// History controller

Backbone.history.start({root: '/tyedye'});

// Views definition

var PlayerListView = Backbone.View.extend({
    initialize: function () {
        this.listenTo(this.collection, 'reset', this.render);
    },
    collection: players,
    render: function () {
        // Load and compile the template
        var template = _.template( $("#player_list_template").html(), {});
        // Put the compiled html into our 'el' element, putting in on the webpage
        this.$el.html(template);

        this.collection.each(function (playerItem) {
            $("div#player_ul_list").append('<h3 style="font-size: large;"><a href="/tyedye/#/player/' + playerItem.get('code') + '/">' + playerItem.get('name') + '</a></h3><div id="player_stats' + playerItem.get('code') + '" style="display: none;"></div>');
        });
        $("#player_number").text(this.collection.length);
    }
});

var player_list_view = new PlayerListView({ el: $("#player_list") });
