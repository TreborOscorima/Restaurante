"""Componentes compartidos y shell visual del POS."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import RestaurantState


PAGE_BACKGROUND = (
    "radial-gradient(circle at top right, rgba(249, 115, 22, 0.12), transparent 28%), "
    "radial-gradient(circle at bottom left, rgba(239, 68, 68, 0.06), transparent 22%), "
    "linear-gradient(180deg, #060A10 0%, #0B1220 100%)"
)
SURFACE_BASE = "#0F1826"
SURFACE_ELEVATED = "#111B2E"
SURFACE_SOFT = "#162030"
SURFACE_MUTED = "#0D1520"
BORDER_COLOR = "rgba(148, 163, 184, 0.22)"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#CBD5E1"
TEXT_MUTED = "#94A3B8"
ACCENT = "#F97316"
ACCENT_HOVER = "#EA580C"
ACCENT_SOFT = "rgba(249, 115, 22, 0.16)"
SUCCESS_SOFT = "rgba(34, 197, 94, 0.16)"
DANGER_SOFT = "rgba(239, 68, 68, 0.16)"
GLOW = "0 22px 60px rgba(2, 6, 23, 0.44)"
SOFT_GLOW = "0 14px 36px rgba(2, 6, 23, 0.28)"


def surface_card(*children, **props) -> rx.Component:
    """Tarjeta base para todas las superficies del POS.

    Los backgrounds se pasan via style={} para evitar que Radix Box
    intercepte el prop 'background' como token de escala de color.
    """
    bg = props.pop("background", SURFACE_BASE)
    border = props.pop("border", f"1px solid {BORDER_COLOR}")
    border_radius = props.pop("border_radius", "28px")
    box_shadow = props.pop("box_shadow", GLOW)
    incoming_style = props.pop("style", {})
    final_style = {
        "background": bg,
        "border": border,
        "border_radius": border_radius,
        "box_shadow": box_shadow,
        **incoming_style,
    }
    return rx.box(*children, style=final_style, width="100%", **props)


def section_card(*children, **props) -> rx.Component:
    """Tarjeta secundaria para secciones internas."""
    bg = props.pop("background", SURFACE_SOFT)
    border = props.pop("border", f"1px solid {BORDER_COLOR}")
    border_radius = props.pop("border_radius", "24px")
    box_shadow = props.pop("box_shadow", SOFT_GLOW)
    incoming_style = props.pop("style", {})
    final_style = {
        "background": bg,
        "border": border,
        "border_radius": border_radius,
        "box_shadow": box_shadow,
        **incoming_style,
    }
    return rx.box(*children, style=final_style, width="100%", **props)


def action_button(label: str, on_click, icon_tag: str = "arrow_right") -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(tag=icon_tag, size=16),
            rx.text(label, font_weight="700"),
            spacing="2",
            align="center",
        ),
        on_click=on_click,
        background=ACCENT,
        color=TEXT_PRIMARY,
        border_radius="18px",
        height="44px",
        padding_x="1rem",
        _hover={"background": ACCENT_HOVER},
    )


def status_banner(message) -> rx.Component:
    return section_card(
        rx.hstack(
            rx.box(
                width="10px",
                height="10px",
                border_radius="999px",
                style={"background": ACCENT},
                box_shadow=f"0 0 0 8px {ACCENT_SOFT}",
            ),
            rx.text(
                message,
                color=TEXT_SECONDARY,
                font_weight="600",
            ),
            spacing="4",
            align="center",
        ),
        padding="1rem 1.2rem",
    )


def kpi_card(title: str, value, description: str = "", accent_color: str = ACCENT) -> rx.Component:
    return surface_card(
        rx.vstack(
            rx.text(
                title,
                color=TEXT_MUTED,
                font_size="0.78rem",
                font_weight="800",
                letter_spacing="0.12em",
                text_transform="uppercase",
            ),
            rx.text(
                value,
                color=TEXT_PRIMARY,
                font_weight="800",
                font_size="2rem",
                line_height="1.05",
            ),
            rx.cond(
                description != "",
                rx.text(description, color=TEXT_MUTED, font_size="0.9rem"),
                rx.fragment(),
            ),
            align="start",
            spacing="2",
            width="100%",
        ),
        padding="1.2rem 1.3rem",
        border=f"1px solid {accent_color}",
        background=(
            f"linear-gradient(160deg, #131F33 0%, #0F1826 100%)"
        ),
    )


def _brand(compact: bool = False) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(tag="utensils_crossed", size=20, color=TEXT_PRIMARY),
            width="42px",
            height="42px",
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
            box_shadow="0 10px 22px rgba(249, 115, 22, 0.28)",
        ),
        rx.cond(
            compact,
            rx.fragment(),
            rx.vstack(
                rx.text(
                    "NORKYS LAN POS",
                    color=TEXT_PRIMARY,
                    font_weight="800",
                    letter_spacing="0.12em",
                    font_size="0.78rem",
                    text_transform="uppercase",
                ),
                rx.text(
                    "Restaurante de alto tráfico",
                    color=TEXT_MUTED,
                    font_size="0.86rem",
                ),
                align="start",
                spacing="1",
            ),
        ),
        spacing="3",
        align="center",
    )


def _user_summary() -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(tag="user_round", size=18, color=TEXT_PRIMARY),
            width="42px",
            height="42px",
            border_radius="16px",
            style={"background": "rgba(255,255,255,0.08)"},
            display="flex",
            align_items="center",
            justify_content="center",
            border=f"1px solid {BORDER_COLOR}",
        ),
        rx.vstack(
            rx.text(
                RestaurantState.usuario_nombre,
                color=TEXT_PRIMARY,
                font_weight="800",
                font_size="0.92rem",
                max_width="190px",
                text_overflow="ellipsis",
                overflow="hidden",
                white_space="nowrap",
            ),
            rx.text(
                RestaurantState.usuario_rol,
                color=TEXT_MUTED,
                font_weight="600",
                font_size="0.82rem",
            ),
            align="start",
            spacing="1",
        ),
        spacing="3",
        align="center",
    )


def user_session_badge() -> rx.Component:
    return rx.hstack(
        _user_summary(),
        rx.button(
            rx.hstack(
                rx.icon(tag="log_out", size=16),
                rx.text("Salir", font_weight="700"),
                spacing="2",
                align="center",
            ),
            on_click=RestaurantState.logout,
            background=DANGER_SOFT,
            color="#FCA5A5",
            border=f"1px solid rgba(248, 113, 113, 0.20)",
            border_radius="16px",
            height="42px",
            padding_x="0.95rem",
            _hover={"background": "rgba(239, 68, 68, 0.22)"},
        ),
        spacing="3",
        align="center",
    )


_NAV_DESCRIPTIONS = {
    "Mozos": "Mesas y comanda",
    "Caja": "Cobro y tickets",
    "Mostrador": "Takeaway rapido",
    "Cocina": "KDS / Produccion",
    "Catalogo": "Carta y precios",
    "Reportes": "Ventas del dia",
}


def _desktop_nav_item(label: str, href: str, icon_tag: str, active: bool) -> rx.Component:
    description = _NAV_DESCRIPTIONS.get(label, "Modulo operativo")
    return rx.link(
        rx.box(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon_tag, size=18, color=TEXT_PRIMARY),
                    width="40px",
                    height="40px",
                    border_radius="14px",
                    style={
                        "background": rx.cond(
                            active,
                            "rgba(255,255,255,0.12)",
                            "rgba(255,255,255,0.04)",
                        )
                    },
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.cond(
                    RestaurantState.sidebar_collapsed,
                    rx.fragment(),
                    rx.vstack(
                        rx.text(label, color=TEXT_PRIMARY, font_weight="700"),
                        rx.text(
                            description,
                            color=TEXT_MUTED,
                            font_size="0.74rem",
                        ),
                        align="start",
                        spacing="1",
                    ),
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            width="100%",
            padding=rx.cond(
                RestaurantState.sidebar_collapsed,
                "0.6rem",
                "0.7rem 0.8rem",
            ),
            border_radius="20px",
            style={
                "background": rx.cond(
                    active,
                    "linear-gradient(135deg, rgba(249, 115, 22, 0.24) 0%, rgba(234, 88, 12, 0.10) 100%)",
                    "transparent",
                )
            },
            border=rx.cond(
                active,
                "1px solid rgba(249, 115, 22, 0.34)",
                "1px solid transparent",
            ),
            _hover={"background": "rgba(255,255,255,0.06)"},
        ),
        href=href,
        width="100%",
        text_decoration="none",
    )


def _mobile_nav_item(label: str, href: str, icon_tag: str, active: bool) -> rx.Component:
    return rx.link(
        rx.box(
            rx.hstack(
                rx.icon(tag=icon_tag, size=18, color=TEXT_PRIMARY),
                rx.text(label, color=TEXT_PRIMARY, font_weight="700"),
                width="100%",
                spacing="3",
                align="center",
            ),
            width="100%",
            padding="0.85rem 1rem",
            border_radius="18px",
            style={
                "background": rx.cond(
                    active,
                    "rgba(249, 115, 22, 0.18)",
                    "rgba(255,255,255,0.03)",
                )
            },
            border=rx.cond(
                active,
                "1px solid rgba(249, 115, 22, 0.32)",
                f"1px solid {BORDER_COLOR}",
            ),
        ),
        href=href,
        width="100%",
        text_decoration="none",
    )


def _nav_stack(active: str, mobile: bool = False) -> rx.Component:
    nav_item = _mobile_nav_item if mobile else _desktop_nav_item
    return rx.vstack(
        rx.cond(
            RestaurantState.puede_ver_mozos,
            nav_item("Mozos", "/mozos", "layout_grid", active == "mozos"),
            rx.fragment(),
        ),
        rx.cond(
            RestaurantState.puede_ver_caja,
            nav_item("Caja", "/caja", "wallet", active == "caja"),
            rx.fragment(),
        ),
        rx.cond(
            RestaurantState.puede_ver_mostrador,
            nav_item("Mostrador", "/mostrador", "shopping_bag", active == "mostrador"),
            rx.fragment(),
        ),
        rx.cond(
            RestaurantState.puede_ver_cocina,
            nav_item("Cocina", "/cocina", "chef_hat", active == "cocina"),
            rx.fragment(),
        ),
        rx.cond(
            RestaurantState.puede_ver_catalogo,
            nav_item("Catalogo", "/catalogo", "book_open", active == "catalogo"),
            rx.fragment(),
        ),
        rx.cond(
            RestaurantState.puede_ver_admin_ventas,
            nav_item(
                "Reportes",
                "/admin/ventas",
                "receipt_text",
                active == "admin_ventas",
            ),
            rx.fragment(),
        ),
        width="100%",
        spacing="3",
        align="stretch",
    )


def module_nav(active: str) -> rx.Component:
    """Compatibilidad con vistas previas."""

    return _nav_stack(active, mobile=False)


def _desktop_sidebar(active: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.cond(
                    RestaurantState.sidebar_collapsed,
                    _brand(compact=True),
                    _brand(compact=False),
                ),
                rx.icon_button(
                    rx.icon(tag="menu", size=18),
                    on_click=RestaurantState.toggle_sidebar,
                    background="rgba(255,255,255,0.06)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="16px",
                    _hover={"background": "rgba(255,255,255,0.10)"},
                ),
                width="100%",
                justify="between",
                align="center",
            ),
            rx.box(height="1px", width="100%", background=BORDER_COLOR),
            _nav_stack(active, mobile=False),
            rx.spacer(),
            rx.cond(
                RestaurantState.sidebar_collapsed,
                rx.fragment(),
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Operacion en LAN",
                            color=TEXT_PRIMARY,
                            font_weight="700",
                        ),
                        rx.text(
                            "UI optimizada para tablets, caja, cocina y control administrativo.",
                            color=TEXT_MUTED,
                            font_size="0.84rem",
                        ),
                        align="start",
                        spacing="2",
                    ),
                    width="100%",
                    padding="1rem",
                    border_radius="20px",
                    style={"background": "rgba(255,255,255,0.04)"},
                    border=f"1px solid {BORDER_COLOR}",
                ),
            ),
            height="100%",
            width="100%",
            spacing="5",
            align="start",
        ),
        width=rx.cond(RestaurantState.sidebar_collapsed, "96px", "280px"),
        min_width=rx.cond(RestaurantState.sidebar_collapsed, "96px", "280px"),
        height="calc(100vh - 2rem)",
        position="sticky",
        top="1rem",
        padding="1rem",
        background=SURFACE_ELEVATED,
        border=f"1px solid {BORDER_COLOR}",
        border_radius="30px",
        box_shadow=GLOW,
        display=rx.breakpoints(initial="none", lg="block"),
    )


def _mobile_nav_drawer(active: str) -> rx.Component:
    return rx.box(
        rx.drawer.root(
            rx.drawer.trigger(
                rx.icon_button(
                    rx.icon(tag="menu", size=18),
                    background="rgba(255,255,255,0.08)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="16px",
                    _hover={"background": "rgba(255,255,255,0.12)"},
                )
            ),
            rx.drawer.portal(
                rx.drawer.overlay(),
                rx.drawer.content(
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                _brand(compact=False),
                                rx.drawer.close(
                                    rx.icon_button(
                                        rx.icon(tag="menu", size=18),
                                        background="rgba(255,255,255,0.06)",
                                        color=TEXT_PRIMARY,
                                        border=f"1px solid {BORDER_COLOR}",
                                        border_radius="16px",
                                    )
                                ),
                                width="100%",
                                justify="between",
                                align="center",
                            ),
                            rx.box(height="1px", width="100%", background=BORDER_COLOR),
                            _nav_stack(active, mobile=True),
                            rx.box(height="1px", width="100%", background=BORDER_COLOR),
                            user_session_badge(),
                            width="100%",
                            align="start",
                            spacing="5",
                        ),
                        width="320px",
                        max_width="88vw",
                        height="100%",
                        padding="1.1rem",
                        background=SURFACE_ELEVATED,
                        border_right=f"1px solid {BORDER_COLOR}",
                    ),
                    justify_content="flex-start",
                ),
            ),
            direction="left",
        ),
        display=rx.breakpoints(initial="block", lg="none"),
    )


def _page_header(
    active: str,
    title: str,
    subtitle: str,
    action: rx.Component | None = None,
) -> rx.Component:
    return surface_card(
        rx.vstack(
            # Fila 1: hamburguesa + título + usuario/acción
            rx.hstack(
                rx.hstack(
                    _mobile_nav_drawer(active),
                    rx.vstack(
                        rx.text(
                            "NORKYS LAN POS",
                            color=ACCENT,
                            font_size="0.75rem",
                            font_weight="800",
                            letter_spacing="0.16em",
                            text_transform="uppercase",
                        ),
                        rx.heading(
                            title,
                            size=rx.breakpoints(initial="5", md="7"),
                            color=TEXT_PRIMARY,
                            line_height="1.1",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    spacing="3",
                    align="center",
                    flex="1",
                    min_width="0",
                ),
                rx.hstack(
                    action if action is not None else rx.fragment(),
                    # Usuario y logout: solo visible en desktop
                    rx.cond(
                        RestaurantState.autenticado,
                        rx.box(
                            user_session_badge(),
                            display=rx.breakpoints(initial="none", lg="block"),
                        ),
                        rx.fragment(),
                    ),
                    spacing="3",
                    align="center",
                    flex_shrink="0",
                ),
                width="100%",
                justify="between",
                align="center",
                gap="0.75rem",
            ),
            # Fila 2: subtítulo — solo en desktop
            rx.box(
                rx.text(
                    subtitle,
                    color=TEXT_MUTED,
                    font_size="0.9rem",
                    max_width="760px",
                ),
                display=rx.breakpoints(initial="none", md="block"),
                width="100%",
            ),
            width="100%",
            spacing="2",
            align="start",
        ),
        padding=rx.breakpoints(initial="0.95rem 1rem", md="1.35rem"),
        background="linear-gradient(160deg, #131F33 0%, #0F1826 100%)",
    )


def app_shell(
    *,
    active: str,
    title: str,
    subtitle: str,
    content: rx.Component,
    action: rx.Component | None = None,
) -> rx.Component:
    """Shell visual compartido para módulos operativos y administrativos."""

    return rx.box(
        rx.hstack(
            _desktop_sidebar(active),
            rx.box(
                rx.vstack(
                    _page_header(active, title, subtitle, action),
                    content,
                    width="100%",
                    align="start",
                    spacing="6",
                ),
                width="100%",
                min_height="100vh",
                padding=rx.breakpoints(initial="1rem", md="1.25rem", xl="1.5rem"),
            ),
            width="100%",
            align="start",
            gap="1rem",
        ),
        min_height="100vh",
        width="100%",
        background=PAGE_BACKGROUND,
        color=TEXT_PRIMARY,
    )
