from game_utils.game import Game
from pygame.event import Event
import logging

logger = logging.getLogger(__name__)


class TestGame(Game):
    def __init__(self):
        super().__init__(
            Game.ScreenSettings(width=600, height=400, bg_color="cyan", no_screen=True)
        )

        self.state = 0.0

    def handler(self, event: Event):
        logger.info(f"state: {self.state}")
        self.state += self.dt
        if self.state > 1:
            self.running = False


def test_run():
    tg = TestGame()

    assert tg.screen_settings.width == 600
    assert tg.screen_settings.bg_color is not None
    assert tg.state == 0

    tg.run(tg.handler)

    assert tg.state > tg.screen_settings.height
