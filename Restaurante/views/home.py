"""Pantalla inicial del MVP."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_HOVER,
    BORDER_COLOR,
    PAGE_BACKGROUND,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    user_session_badge,
)


def module_card(
    title: str,
    description: str,
    href: str,
    icon_tag: str,
    accent: str = ACCENT,
) -> rx.Component:
    return rx.link(
        rx.box(
            rx.vstack(
                rx.box(
                    rx.icon(tag=icon_tag, size=24, color=TEXT_PRIMARY),
                    width="54px",
                    height="54px",
                    border_radius="20px",
                    style={
                        "background": (
                            "linear-gradient(135deg, rgba(249, 115, 22, 0.88) 0%, "
                            "rgba(234, 88, 12, 0.88) 100%)"
                        )
                    },
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 12px 30px rgba(249, 115, 22, 0.22)",
                ),
                rx.heading(title, size="5", color=TEXT_PRIMARY),
                rx.text(description, color=TEXT_MUTED),
                rx.hstack(
                    rx.text("Abrir módulo", color=TEXT_SECONDARY, font_weight="700"),
                    rx.icon(tag="arrow_right", size=16, color=accent),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="start",
                spacing="3",
            ),
            width="100%",
            padding="1.3rem",
            border_radius="28px",
            style={"background": "#0F1826"},
            border=f"1px solid {BORDER_COLOR}",
            box_shadow="0 18px 48px rgba(2, 6, 23, 0.36)",
            _hover={"transform": "translateY(-4px)", "border": f"1px solid {accent}"},
        ),
        href=href,
        width="100%",
        text_decoration="none",
    )


def home_page() -> rx.Component:
    """Página de acceso rápido a módulos."""

    return rx.box(
        rx.container(
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon(
                                        tag="utensils_crossed",
                                        size=24,
                                        color=TEXT_PRIMARY,
                                    ),
                                    width="56px",
                                    height="56px",
                                    border_radius="22px",
                                    style={
                                        "background": (
                                            "linear-gradient(135deg, rgba(249, 115, 22, 0.88) 0%, "
                                            "rgba(234, 88, 12, 0.88) 100%)"
                                        )
                                    },
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
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
                                        "Sistema de Gestion para Restaurantes",
                                        size="8",
                                        color=TEXT_PRIMARY,
                                    ),
                                    rx.text(
                                        "POS offline-first con salon, caja, cocina, mostrador y administracion.",
                                        color=TEXT_MUTED,
                                        max_width="720px",
                                    ),
                                    align="start",
                                    spacing="2",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.cond(
                                RestaurantState.autenticado,
                                user_session_badge(),
                                rx.link(
                                    rx.button(
                                        "Ir a Login",
                                        background=ACCENT,
                                        color=TEXT_PRIMARY,
                                        border_radius="18px",
                                        padding_x="1.2rem",
                                        font_weight="800",
                                        _hover={"background": ACCENT_HOVER},
                                    ),
                                    href="/login",
                                ),
                            ),
                            width="100%",
                            justify="between",
                            align="center",
                            wrap="wrap",
                            gap="1rem",
                        ),
                        rx.box(height="1px", width="100%", background=BORDER_COLOR),
                        rx.grid(
                            module_card(
                                "Mozos",
                                "Toma de pedidos por mesa, seguimiento y solicitud de cuenta.",
                                "/mozos",
                                "layout_grid",
                            ),
                            module_card(
                                "Caja",
                                "Cobro rapido, cierre de cuentas e impresion de ticket.",
                                "/caja",
                                "wallet",
                            ),
                            module_card(
                                "Mostrador",
                                "Venta takeaway con cobro inmediato y entrega al cliente.",
                                "/mostrador",
                                "shopping_bag",
                            ),
                            module_card(
                                "Cocina",
                                "KDS con flujo pendiente, en preparacion y listo.",
                                "/cocina",
                                "chef_hat",
                            ),
                            template_columns=rx.breakpoints(
                                initial="1fr",
                                md="repeat(2, minmax(0, 1fr))",
                            ),
                            gap="1rem",
                            width="100%",
                        ),
                        width="100%",
                        spacing="5",
                    ),
                    width="100%",
                    padding="1.5rem",
                    border_radius="32px",
                    style={"background": "#111B2E"},
                    border=f"1px solid {BORDER_COLOR}",
                    box_shadow="0 22px 60px rgba(2, 6, 23, 0.42)",
                ),
                width="100%",
                spacing="6",
                align="start",
                padding_y="2rem",
            ),
            max_width="1320px",
            padding_x=rx.breakpoints(initial="1rem", md="1.5rem"),
        ),
        min_height="100vh",
        width="100%",
        background=PAGE_BACKGROUND,
    )
