import sys
from log import init_logger, DEBUG
from server import game, ui

logger = init_logger('wam', DEBUG)
ui_controller = ui.UIController(logger)
game_manager = game.GameManager(logger, ui=ui_controller)
app = ui.WamApp(ui_controller=ui_controller)
if __name__ == '__main__':
    app.run()
