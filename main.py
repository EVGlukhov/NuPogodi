from pygame.surface import Surface
import pygame
import config


def draw_game(
    surface: pygame.Surface,
    title_font: pygame.font.Font
) -> None:
    surface.fill(config.BACKGROUND_COLOR)

    pygame.draw.rect(
        surface,
        config.CONSOLE_COLOR,
        config.CONSOLE_RECT,
        border_radius=config.CONSOLE_RADIUS
    )

    pygame.draw.rect(
        surface,
        config.SCREEN_FRAME_COLOR,
        config.SCREEN_FRAME_RECT,
        border_radius=config.SCREEN_FRAME_RADIUS,
    )

    pygame.draw.rect(
        surface,
        config.PLAYFIELD_COLOR,
        config.PLAYFIELD_RECT
    )

    title: Surface = title_font.render(config.TITLE, True, config.TITLE_COLOR)
    surface.blit(title, title.get_rect(center=config.TITLE_POSITION))


def main() -> None:
    pygame.init()

    screen: Surface = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    title_font = pygame.font.Font(None, config.TITLE_FONT_SIZE)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_game(screen, title_font)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
