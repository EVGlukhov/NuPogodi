"""Initialize the window and run the Pygame application loop."""

import pygame

import config
from game import Game


def main() -> None:
    """Run the game until the player closes the window or presses Escape."""
    pygame.init()
    screen = pygame.display.set_mode(
        (config.WIDTH, config.HEIGHT),
        pygame.RESIZABLE,
    )
    pygame.display.set_caption(config.TITLE)

    canvas = pygame.Surface((config.GAME_WIDTH, config.GAME_HEIGHT)).convert()
    game = Game()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(event)

        game.update(clock.tick(config.FPS) / 1000)
        game.draw(canvas)

        scale = min(
            screen.get_width() / config.GAME_WIDTH,
            screen.get_height() / config.GAME_HEIGHT,
        )
        scaled_size = (
            round(config.GAME_WIDTH * scale),
            round(config.GAME_HEIGHT * scale),
        )
        frame = pygame.transform.smoothscale(canvas, scaled_size)
        screen.fill(config.WINDOW_BACKGROUND)
        screen.blit(frame, frame.get_rect(center=screen.get_rect().center))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
