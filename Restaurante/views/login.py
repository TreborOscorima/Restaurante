"""Pantalla de acceso por PIN para tablets y puestos operativos."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_HOVER,
    ACCENT_SOFT,
    BORDER_COLOR,
    PAGE_BACKGROUND,
    SOFT_GLOW,
    SURFACE_BASE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def keypad_button(
    label: str,
    on_click,
    background: str = "rgba(255,255,255,0.06)",
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
        box_shadow=SOFT_GLOW,
        _hover={"transform": "translateY(-1px)", "opacity": "0.96"},
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
                                        "linear-gradient(135deg, rgba(249, 115, 22, 0.88) 0%, "
                                        "rgba(234, 88, 12, 0.88) 100%)"
                                    )
                                },
                                display="flex",
                                align_items="center",
                                justify_content="center",
                                box_shadow=f"0 12px 28px {ACCENT_SOFT}",
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
                        style={"background": "rgba(255,255,255,0.04)"},
                        color=TEXT_PRIMARY,
                        border=f"1px solid {BORDER_COLOR}",
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
                            background="rgba(239, 68, 68, 0.14)",
                            color="#FCA5A5",
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
                        background="rgba(255,255,255,0.04)",
                        color=TEXT_SECONDARY,
                        border=f"1px solid {BORDER_COLOR}",
                        font_weight="700",
                        _hover={"background": "rgba(255,255,255,0.08)"},
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
                        style={"background": "rgba(255,255,255,0.03)"},
                        border=f"1px solid {BORDER_COLOR}",
                    ),
                    width="100%",
                    align="center",
                    spacing="5",
                ),
                width="100%",
                max_width="400px",
                padding=rx.breakpoints(initial="1.2rem", md="1.5rem"),
                border_radius="32px",
                style={"background": "linear-gradient(160deg, #131F33 0%, #0F1826 100%)"},
                border=f"1px solid {BORDER_COLOR}",
                box_shadow="0 28px 80px rgba(2, 6, 23, 0.48)",
            ),
            min_height="100vh",
            width="100%",
            padding="1rem",
        ),
        min_height="100vh",
        width="100%",
        background=PAGE_BACKGROUND,
    )
