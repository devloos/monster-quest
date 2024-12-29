from src.settings import *


def draw_bar(
    surface: pg.Surface, rect: pg.FRect, value: float, max_value: float,
    bg_color: str, progress_color: str, border_radius=0,
    border_bottom_left_radius=1, border_bottom_right_radius=1,
    border_top_left_radius=1, border_top_right_radius=1
) -> None:
    ratio = rect.width / max_value

    progress = max(0, min(rect.width, ratio * value))
    progress_rect = pg.FRect(rect.topleft, (progress, rect.height))

    if bool(border_radius):
        pg.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        pg.draw.rect(surface, progress_color, progress_rect, border_radius=border_radius)
    else:
        pg.draw.rect(
            surface, bg_color, rect, border_radius=border_radius,
            border_bottom_left_radius=border_bottom_left_radius,
            border_bottom_right_radius=border_bottom_right_radius,
            border_top_left_radius=border_top_left_radius,
            border_top_right_radius=border_top_right_radius
        )
        pg.draw.rect(
            surface, progress_color, progress_rect, border_radius=border_radius,
            border_bottom_left_radius=border_bottom_left_radius,
            border_bottom_right_radius=border_bottom_right_radius,
            border_top_left_radius=border_top_left_radius,
            border_top_right_radius=border_top_right_radius
        )
