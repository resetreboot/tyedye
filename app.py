#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import web

render = web.template.render('views/')
db = web.database(dbn = 'sqlite', db = 'game.db')

urls = (
    '/app/', 'summary',
)

app = web.application(urls, globals())

def render_html(game_name, main_block):
    sidebar = render.sidebar()
    return render.layout(main_block, sidebar, game_name)


class summary(object):
    def GET(self):
        game_name = "My Game"
        player_num = 3
        stats_num = 10
        players = ['Reset', 'Logan', 'Estela']

        summary = render.summary(game_name, player_num, stats_num, players)
        return render_html(game_name, summary)

if __name__ == "__main__":
    app.run()
