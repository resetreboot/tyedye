#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import web
import hashlib, time
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
    '/app/player/(.+)', 'player',
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

def dynamic_register_form(player_name = 'New Player'):
    """
    Creates a register new player dynamicly
    """
    reg_elems = [form.Textbox('name',
                              description = 'Player name:',
                              value = player_name)]

    if player_name == 'New Player':
        for stat in db.select('stats'):
            reg_elems.append(form.Textbox(stat.name,
                                   value = stat.default_value))

    else:
        for stat in db.select('sheet', where = 'player_name = $player_name', vars = locals()):
            stat_name, df_value = get_stat_info_by_id(stat.stat_id)
            reg_elems.append(form.Textbox(stat_name,
                                          value = stat.value))


    if player_name == 'New Player':
        reg_elems.append(form.Button('Register Player'))

    else:
        reg_elems.append(form.Button('Modify Player'))

    reg_form = form.Form(*reg_elems)
    return reg_form

def generate_uuid(player_name):
    """
    Generates a unique id
    """
    full_string = str(time.time()) + "::" + player_name
    hasher = hashlib.sha256()
    hasher.update(full_string)
    return hasher.hexdigest()

def get_stat_info(stat_name):
    """
    Gets stat id and default value
    """
    for s in db.select('stats', where = "name = $stat_name", vars = locals()):
        stat = s

    return stat.id, stat.default_value

def get_stat_info_by_id(stat_id):
    """
    Gets stat id and default value
    """
    for s in db.select('stats', where = "id = $stat_id", vars = locals()):
        stat = s

    return stat.name, stat.default_value

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


class register(object):
    def GET(self):
        game_name = "My Game"
        form = dynamic_register_form()
        register_block = render.register(form.render())
        return render_web(game_name, register_block)

    def POST(self):
        game_name = "My Game"
        stats = {}
        form = dict(web.input())
        name = form['name']
        code = generate_uuid(name)
        db.insert('players', name = name, code = code)

        for key in form:
            if key != 'name' and key != 'Register Player':
                stat_id, default_value = get_stat_info(key)
                if form[key] != '' and form[key] != '0':
                    final_value = form[key]
                
                else:
                    final_value = default_value

                db.insert('sheet', 
                          player_name = name,
                          stat_id = stat_id,
                          value = final_value)
                stats[key] = final_value

        result_render = render.player(name, code, stats)
        return render_web(game_name, result_render)


if __name__ == "__main__":
    app.run()
