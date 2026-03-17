"""Pantalla de acceso por PIN para tablets y puestos operativos."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_GLOW,
    ACCENT_HOVER,
    BORDER_COLOR,
    BORDER_STRONG,
    DANGER_BG,
    DANGER_TEXT,
    PAGE_BACKGROUND,
    SURFACE_ELEVATED,
    SURFACE_GHOST,
    SURFACE_HOVER,
    SURFACE_MUTED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def keypad_button(
    label: str,
    on_click,
    background: str = SURFACE_GHOST,
    color: str = TEXT_PRIMARY,
) -> rx.Component:
    return rx.button(
        label,
        on_click=on_click,
        width="100%",
        height=rx.breakpoints(initial="64px", md="72px"),
        border_radius="20px",
        background=background,
        color=color,
        font_size=rx.breakpoints(initial="1.15rem", md="1.35rem"),
        font_weight="800",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="0 2px 8px rgba(2, 6, 23, 0.30)",
        _hover={"transform": "translateY(-1px)", "background": SURFACE_HOVER},
    )


def login_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.hstack(
                            rx.box(
                                rx.icon(tag="utensils_crossed", size=22, color=TEXT_PRIMARY),
                                width="48px",
                                height="48px",
                                border_radius="18px",
                                style={
                                    "background": (
                                        "linear-gradient(135deg, #C85A08 0%, #A04806 100%)"
                                    )
                                },
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                box_shadow=ACCENT_GLOW,
                            ),
                            rx.vstack(
                                rx.text(
                                    "NORKYS LAN POS",
                                    text_transform="uppercase",
                                    letter_spacing="0.18em",
                                    font_size="0.78rem",
                                    font_weight="800",
                                    color=ACCENT,
                                ),
                                rx.heading(
                                    "Ingreso por PIN",
                                    size="7",
                                    color=TEXT_PRIMARY,
                                ),
                                align="start",
                                spacing="1",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        width="100%",
                    ),
                    rx.text(
                        "Accede rápido a tu módulo operativo con un PIN de 4 a 6 dígitos.",
                        color=TEXT_MUTED,
                        text_align="center",
                        max_width="320px",
                    ),
                    # Campo PIN: read_only porque el numpad maneja el input.
                    # on_key_down habilita la tecla Enter desde teclado físico.
                    rx.input(
                        value=RestaurantState.login_pin_input,
                        type="password",
                        read_only=True,
                        placeholder="••••",
                        width="100%",
                        height="68px",
                        text_align="center",
                        font_size="1.9rem",
                        font_weight="800",
                        letter_spacing="0.3em",
                        style={"background": SURFACE_ELEVATED},
                        color=TEXT_PRIMARY,
                        border=f"1px solid {BORDER_STRONG}",
                        border_radius="20px",
                        on_key_down=rx.cond(
                            rx.Var.create("event.key") == "Enter",
                            RestaurantState.submit_login_pin,
                            rx.noop(),
                        ),
                    ),
                    rx.grid(
                        keypad_button("1", RestaurantState.append_login_digit("1")),
                        keypad_button("2", RestaurantState.append_login_digit("2")),
                        keypad_button("3", RestaurantState.append_login_digit("3")),
                        keypad_button("4", RestaurantState.append_login_digit("4")),
                        keypad_button("5", RestaurantState.append_login_digit("5")),
                        keypad_button("6", RestaurantState.append_login_digit("6")),
                        keypad_button("7", RestaurantState.append_login_digit("7")),
                        keypad_button("8", RestaurantState.append_login_digit("8")),
                        keypad_button("9", RestaurantState.append_login_digit("9")),
                        keypad_button(
                            "Borrar",
                            RestaurantState.backspace_login_pin,
                            background=DANGER_BG,
                            color=DANGER_TEXT,
                        ),
                        keypad_button("0", RestaurantState.append_login_digit("0")),
                        keypad_button(
                            "Entrar",
                            RestaurantState.submit_login_pin,
                            background=ACCENT,
                            color=TEXT_PRIMARY,
                        ),
                        template_columns="repeat(3, minmax(0, 1fr))",
                        gap="0.8rem",
                        width="100%",
                    ),
                    rx.button(
                        "Limpiar PIN",
                        on_click=RestaurantState.clear_login_pin,
                        width="100%",
                        height="52px",
                        border_radius="18px",
                        background=SURFACE_GHOST,
                        color=TEXT_SECONDARY,
                        border=f"1px solid {BORDER_COLOR}",
                        font_weight="700",
                        _hover={"background": SURFACE_HOVER},
                    ),
                    rx.box(
                        rx.text(
                            "Ingresa tu PIN y toca Entrar",
                            color=TEXT_MUTED,
                            font_size="0.82rem",
                            text_align="center",
                        ),
                        width="100%",
                        padding="0.85rem 1rem",
                        border_radius="18px",
                        style={"background": SURFACE_MUTED},
                        border=f"1px solid {BORDER_COLOR}",
                    ),
                    width="100%",
                    align="center",
                    spacing="5",
                ),
                width=rx.breakpoints(initial="100%", sm="420px"),
                max_width="420px",
                padding=rx.breakpoints(initial="1.2rem", sm="1.6rem", md="2rem"),
                border_radius="32px",
                style={"background": "linear-gradient(160deg, #131F33 0%, #0F1826 100%)"},
                border=f"1px solid {BORDER_COLOR}",
                box_shadow="0 28px 80px rgba(2, 6, 23, 0.60)",
            ),
            min_height="100vh",
            width="100%",
            padding=rx.breakpoints(initial="1rem", md="2rem"),
        ),
        min_height="100vh",
        width="100%",
        style={"background": PAGE_BACKGROUND},
    )
