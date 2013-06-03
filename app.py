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
    '/app/stats', 'statistics',
    '/app/stats/', 'statistics',
    '/app/stats/add', 'stat_add',
    '/app/stats/remove/(.+)', 'remove_stat',
    '/app/stats/edit/(.+)', 'edit_stat',
    '/app/register', 'register',
    '/app/register/', 'register',
    '/app/player/(.+)', 'player',
    '/app/player_remove/(.+)', 'remove_player',
    '/app/player_edit/(.+)', 'edit_player',
    '/app/config', 'config',
    '/app/config/', 'config',
)

# Forms used by the app
# See dynamic_register_form for the
# character sheet configuration
add_stat = form.Form(
    form.Textbox('stat_name',
                 description = 'Stat name:'),
    form.Textbox('default_value',
                 description = 'Default value:',
                 value = 0),
    form.Button('OK')
)

config_form = form.Form(
    form.Textbox('game_name',
                 description = 'Game name'),
    form.Button('Send'))

app = web.application(urls, globals())

# Auxiliary functions

def render_web(main_block):
    """
    Cobbles together all the pieces we've broken our
    templates, so we can have a kind of modular design
    """
    game_name = get_game_name()
    sidebar = render.sidebar()
    return render.layout(main_block, sidebar, game_name)

def get_game_name():
    """
    Gets the name of the game
    """
    try:
        for e in db.select('game_config'):
            name = e.game_name

        if name == '':
            return "My Game"

        else:
            return name

    except:
        return "My Game"

def dynamic_register_form(player_name = 'New Player'):
    """
    Creates a register new player dynamicly
    """
    if player_name == 'New Player':
        reg_elems = [form.Textbox('name',
                                  description = 'Player name:',
                                  value = player_name)]

    else:
        reg_elems = [form.Textbox('name',
                                  description = 'Player name:',
                                  value = player_name,
                                  readonly = 'on')]


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
        game_name = get_game_name()

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
        return render_web(summary)


class statistics(object):
    def GET(self):
        game_name = get_game_name()
        stats = []
        for stat in db.select("stats"):
            stats.append(stat)

        add_stat_form = add_stat.render()

        config = render.statistics(game_name,
                                   stats,
                                   add_stat_form)

        return render_web(config)


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
        try:
            index = int(index_to_remove)

            for s in db.select('stats', where = 'id = $index', vars = locals()):
                stat_info = s

            edit_form = add_stat()
            edit_stat_form = edit_form.render() 
            edit_stat = render.edit_stat(stat_info, edit_stat_form)

            return render_web(edit_stat)

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
        form = dynamic_register_form()
        register_block = render.register(form.render(), True)
        return render_web(register_block)

    def POST(self):
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

        result_render = render.player(name, code, stats, False)
        return render_web(result_render)


class player(object):
    def GET(self, player_name):
        for p in db.select('players', where = 'name = $player_name', vars = locals()):
            player_data = p

        stats = {}
        for s in db.select('sheet', where = 'player_name = $player_name', vars = locals()):
            try:
                stat_name, def_val = get_stat_info_by_id(s.stat_id)
                stats[stat_name] = s.value

            except Exception as e:
                continue

        result_render = render.player(player_data.name, player_data.code, stats, True)
        return render_web(result_render)


class edit_player(object):
    def GET(self, player_name):
        form = dynamic_register_form(player_name)
        edit_block = render.register(form.render(), False)
        return render_web(edit_block)

    def POST(self, player_name):
        stats = {}
        form = dict(web.input())
        name = form['name']
        code = generate_uuid(name)

        for key in form:
            if key != 'name' and key != 'Register Player' and key != 'Modify Player':
                stat_id, default_value = get_stat_info(key)
                if form[key] != '' and form[key] != '0':
                    final_value = form[key]
                
                else:
                    final_value = default_value

                db.update('sheet', 
                          where = 'stat_id = $stat_id AND player_name = $name',
                          value = final_value,
                          vars = locals())
                stats[key] = final_value

        result_render = render.player(name, code, stats, False)
        return render_web(result_render)


class remove_player(object):
    def GET(self, player_name):
        try:
            db.delete('players', where = 'name = $player_name', vars = locals())
            db.delete('sheet', where = 'player_name = $player_name', vars = locals())

        except:
            pass

        raise web.seeother('/app')


class config(object):
    def GET(self):
        form = config_form()
        config = render.config(form.render())
        return render_web(config)

    def POST(self):
        form = config_form()
        if form.validates():
            new_game_name = form.d.game_name
            db.delete('game_config', where = 'game_name = game_name')
            db.insert('game_config', game_name = new_game_name)
            raise web.seeother('/app')

        else:
            return "Ooops! Something went wrong."


if __name__ == "__main__":
    app.run()
