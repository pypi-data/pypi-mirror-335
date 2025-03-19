# Game Utils

>0.1.1

## `game-utils` is a pygame engine.  The engine includes modules to facilitate boilerplate game operations. 

### Installation

`pip install -i https://test.pypi.org/simple/ game-utils`

### Example usage

```python
from game_utils import Game

class MyAwesomeGame(Game):
    def _update_screen(self):
        self.screen_settings.screen.fill(
            self.screen_settings.bg_color or "dodgerblue2"
        )


if __name__ == "__main__":
    game = MyAwesomeGame(
        screen_settings=Game.ScreenSettings(
            bg_color="coral2"
        )
    )

    print("Starting game...")
    game.run()
    print("Thanks for playing!")
```

---

## See Also...

<p><b>My ongoing game projects</b></p>

- Madmadam Games [gitlab](https://gitlab.com/madmadam/games)
