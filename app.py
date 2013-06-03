#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import web
from web import form

# Framework initialization

render = web.template.render('views/')
db = web.database(dbn = 'sqlite', db = 'game.db')

urls = (
    '/app', 'summary',
    '/app/', 'summary',
    '/app/config', 'config',
    '/app/config/', 'config',
    '/app/config/add', 'stat_add',
    '/app/config/remove/(.+)', 'remove_stat',
    '/app/config/edit/(.+)', 'edit_stat',
    '/app/register', 'register',
    '/app/register/', 'register',
)

# Forms used by the app
add_stat = form.Form(
    form.Textbox('stat_name',
                 description = 'Stat name:'),
    form.Textbox('default_value',
                 description = 'Default value:',
                 value = 0),
    form.Button('Add Stat')
)

app = web.application(urls, globals())

# Auxiliary functions

def render_web(game_name, main_block):
    """
    Cobbles together all the pieces we've broken our
    templates, so we can have a kind of modular design
    """
    sidebar = render.sidebar()
    return render.layout(main_block, sidebar, game_name)

def dynamic_register_form():
    """
    Creates a register new player dynamicly
    """
    reg_elems = [form.Textbox('name',
                              description = 'Player name:')]

    for stat in db.select('stats'):
        textbox = form.Textbox(stat.name,
                               value = stat.default_value)

    

# Server calls

class summary(object):
    def GET(self):
        # TODO: Get from main configuration file
        game_name = "My Game"

        # Variable initialization
        player_num = 0
        stats_num = 0
        players = []
        for player in db.select("players"):
            player_num +=1
            players.append(player['name'])

        # I know, this is pretty clumsy...
        for stat in db.select("stats"):
            stats_num += 1

        # We render our main block and feed it to our 
        # Web renderer
        summary = render.summary(game_name, 
                                 player_num, 
                                 stats_num, 
                                 players)
        return render_web(game_name, summary)


class config(object):
    def GET(self):
        game_name = "My Game"
        stats = []
        for stat in db.select("stats"):
            stats.append(stat)

        add_stat_form = add_stat.render()

        config = render.config(game_name,
                               stats,
                               add_stat_form)

        return render_web(game_name, config)


class stat_add(object):
    def POST(self):
        form = add_stat()
        if form.validates():
            db.insert('stats', name = form.d.stat_name, default_value = form.d.default_value)

        raise web.seeother('/app/config')


class remove_stat(object):
    def GET(self, index_to_remove):
        try:
            index = int(index_to_remove)

        except Exception as e:
            return "Ooops! Wrong index!"

        db.delete('stats', where = 'id = $index', vars = locals())
        raise web.seeother('/app/config')


class edit_stat(object):
    def GET(self, index_to_remove):
        game_name = "My Game"
        try:
            index = int(index_to_remove)

            for s in db.select('stats', where = 'id = $index', vars = locals()):
                stat_info = s

            edit_form = add_stat()
            edit_stat_form = edit_form.render() 
            edit_stat = render.edit_stat(stat_info, edit_stat_form)

            return render_web(game_name, edit_stat)

        except Exception as e:
            return "Ooops! Wrong index!"

    def POST(self, index_to_edit):
        try:
            if "/" in index_to_edit:
                final_index = index_to_edit.split("/")[-1]
            
            else:
                final_index = index_to_edit

            index = int(final_index)
            form = add_stat()
            if form.validates():
                db.update('stats', 
                          where = 'id = $index', 
                          name = form.d.stat_name, 
                          default_value = form.d.default_value, 
                          vars = locals())

            raise web.seeother('/app/config')

        except Exception as e:
            return "Ooops! Wrong index! %s" % str(e)



if __name__ == "__main__":
    app.run()
