// Model definition

var Stat = Backbone.Model.extend({
      urlRoot: '/tyedye/stat',
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
    url: "/tyedye/stats/",
    initialize: function () {
        this.fetch();
    }
});

var Player = Backbone.Model.extend({
    urlRoot: '/tyedye/player/',
    defaults: {
            name: 'New Player',
            stats: new Stats,
    },
    initialize: function () {
        this.on("change", function (model) {});
    }
});

var Players = Backbone.Collection.extend({
    model: Player,
    url: "/tyedye/players/",
    initialize: function () {
        this.fetch();
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
        this.listenTo(this.collection, 'add', this.render);
    },
    collection: players,
    render: function () {
        // Load and compile the template
        var template = _.template( $("#player_list_template").html(), { 'player_collection' : players,
                                                                        'player_num' : this.collection.length,
                                                                        'stats_num' : stats.length } );
        // Put the compiled html into our 'el' element, putting in on the webpage
        this.$el.html(template);
    }
});

var player_list_view = new PlayerListView({ el: $("#player_list") });

function listUlPlayer (listPlayers) {
    var html = '';
    listPlayers.each(function (item) {
      html += '<li><a href="/tyedye/player/' + item.code '">' + item.name + '</a></li>';
    };
    return html;
    }

