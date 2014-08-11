Character = Backbone.Model.extend({
    urlRoot: '/tyedye/player',
    defaults: {
            name: 'New Player',
            stats: new Stats,
    }
    initialize: function(){
    }
});

var character = new Character;
