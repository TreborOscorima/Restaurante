"""Vista principal para caja en la PC del local."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import HistorialItem, MesaView, RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_BG,
    ACCENT_HOVER,
    BORDER_ACCENT,
    BORDER_COLOR,
    SURFACE_GHOST,
    SURFACE_MUTED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    action_button,
    app_shell,
    kpi_card,
    section_card,
    status_banner,
    surface_card,
)


def mesa_row(mesa: MesaView) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(f"#{mesa.id}", color=TEXT_SECONDARY, font_weight="700")
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(mesa.label, color=TEXT_PRIMARY, font_weight="800"),
                rx.text(mesa.estado_label, color=TEXT_MUTED, font_size="0.82rem"),
                align="start",
                spacing="1",
            )
        ),
        rx.table.cell(
            rx.text(mesa.total_abierto_texto, color="#FDBA74", font_weight="800")
        ),
        rx.table.cell(
            rx.button(
                "Generar Ticket",
                on_click=RestaurantState.seleccionar_mesa(mesa.id),
                background=rx.cond(
                    RestaurantState.mesa_seleccionada_id == mesa.id,
                    ACCENT,
                    SURFACE_GHOST,
                ),
                color=TEXT_PRIMARY,
                border=rx.cond(
                    RestaurantState.mesa_seleccionada_id == mesa.id,
                    f"1px solid {BORDER_ACCENT}",
                    f"1px solid {BORDER_COLOR}",
                ),
                border_radius="14px",
                font_weight="700",
                _hover={"background": ACCENT_BG},
            )
        ),
        style={
            "background": rx.cond(
                RestaurantState.mesa_seleccionada_id == mesa.id,
                ACCENT_BG,
                "transparent",
            )
        },
    )


def mesas_table() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Pendientes de cobro",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading(
                    "Mesas esperando cuenta",
                    size="6",
                    color=TEXT_PRIMARY,
                ),
                rx.text(
                    "Selecciona una mesa para revisar el consumo y generar el ticket final.",
                    color=TEXT_MUTED,
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.cond(
                RestaurantState.cantidad_mesas_abiertas > 0,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Mesa"),
                                rx.table.column_header_cell("Total"),
                                rx.table.column_header_cell("Accion"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(RestaurantState.mesas_abiertas, mesa_row)
                        ),
                        width="100%",
                        variant="surface",
                        size="3",
                    ),
                    width="100%",
                    overflow_x="auto",
                    padding="0.2rem",
                    border_radius="22px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    rx.vstack(
                        rx.heading("Sin mesas pendientes", size="5", color=TEXT_PRIMARY),
                        rx.text(
                            "Cuando el salon solicite cuenta, las mesas apareceran aqui.",
                            color=TEXT_MUTED,
                            text_align="center",
                            max_width="340px",
                        ),
                        align="center",
                        spacing="3",
                        width="100%",
                    ),
                    width="100%",
                    padding="3rem 1.25rem",
                    border_radius="24px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px dashed {BORDER_COLOR}",
                ),
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def cuenta_row(item: HistorialItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(item.cantidad, color=TEXT_SECONDARY, font_weight="700")),
        rx.table.cell(
            rx.vstack(
                rx.text(item.nombre, color=TEXT_PRIMARY, font_weight="700"),
                rx.cond(
                    item.nota != "",
                    rx.text(f"Nota: {item.nota}", color=TEXT_MUTED, font_size="0.82rem"),
                    rx.fragment(),
                ),
                align="start",
                spacing="1",
            )
        ),
        rx.table.cell(
            rx.text(item.precio_unitario_texto, color=TEXT_SECONDARY, font_weight="700")
        ),
        rx.table.cell(
            rx.text(item.subtotal_texto, color="#FDBA74", font_weight="800")
        ),
    )


def cuenta_panel() -> rx.Component:
    return surface_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Ticket actual",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading(
                    RestaurantState.mesa_seleccionada_label,
                    size="6",
                    color=TEXT_PRIMARY,
                ),
                rx.text(
                    "Verifica consumo, genera comprobante y libera la mesa.",
                    color=TEXT_MUTED,
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Atendido por", color=TEXT_MUTED, font_size="0.82rem"),
                    rx.text(
                        rx.cond(
                            RestaurantState.mesa_atendida_por_nombre != "",
                            RestaurantState.mesa_atendida_por_nombre,
                            "Sin asignar",
                        ),
                        color=TEXT_PRIMARY,
                        font_weight="800",
                        font_size="1.1rem",
                    ),
                    align="start",
                    spacing="1",
                ),
                width="100%",
                padding="1rem",
                border_radius="20px",
                style={"background": SURFACE_GHOST},
                border=f"1px solid {BORDER_COLOR}",
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "TOTAL DE LA VENTA",
                        color=TEXT_MUTED,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.14em",
                        text_transform="uppercase",
                    ),
                    rx.text(
                        RestaurantState.mesa_seleccionada_total_texto,
                        color=TEXT_PRIMARY,
                        font_weight="800",
                        font_size=rx.breakpoints(initial="2.4rem", md="3rem"),
                        line_height="1",
                    ),
                    align="start",
                    spacing="2",
                ),
                width="100%",
                padding="1.1rem",
                border_radius="24px",
                style={
                    "background": (
                        "linear-gradient(135deg, #3D1A06 0%, #1E0D03 100%)"
                    )
                },
                border=f"1px solid {BORDER_ACCENT}",
            ),
            rx.cond(
                RestaurantState.hay_historial_pedido,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Cant."),
                                rx.table.column_header_cell("Producto"),
                                rx.table.column_header_cell("P. Unit."),
                                rx.table.column_header_cell("Subtotal"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(RestaurantState.historial_pedido, cuenta_row)
                        ),
                        width="100%",
                        variant="surface",
                        size="2",
                    ),
                    width="100%",
                    overflow_x="auto",
                    padding="0.2rem",
                    border_radius="22px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    "Selecciona una mesa para ver el ticket detallado.",
                    width="100%",
                    padding="1.2rem",
                    border_radius="20px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px dashed {BORDER_COLOR}",
                    color=TEXT_MUTED,
                    text_align="center",
                ),
            ),
            rx.button(
                "Cobrar / Cerrar Mesa",
                on_click=RestaurantState.cobrar_mesa(RestaurantState.mesa_seleccionada_id),
                width="100%",
                background=ACCENT,
                color=TEXT_PRIMARY,
                border_radius="18px",
                padding_y="1.35rem",
                font_weight="800",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
        background="linear-gradient(160deg, #131F33 0%, #0F1826 100%)",
        # Sticky: el panel de cobro permanece visible mientras scrollea la tabla
        position=rx.breakpoints(initial="static", xl="sticky"),
        top="1.5rem",
        max_height=rx.breakpoints(initial="none", xl="calc(100vh - 3rem)"),
        overflow_y=rx.breakpoints(initial="visible", xl="auto"),
    )


def caja_page() -> rx.Component:
    """Módulo de caja para cobro y cierre."""

    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Caja actualizada automaticamente. Selecciona una mesa, revisa el ticket y finaliza el cobro.",
            )
        ),
        rx.grid(
            kpi_card(
                "Mesas abiertas",
                RestaurantState.cantidad_mesas_abiertas,
                "Cobros en cola",
            ),
            kpi_card(
                "Total por cobrar",
                RestaurantState.total_pendiente_caja_texto,
                "Importe acumulado pendiente",
            ),
            template_columns=rx.breakpoints(
                initial="1fr",
                lg="repeat(2, minmax(0, 1fr))",
            ),
            gap="1rem",
            width="100%",
        ),
        rx.grid(
            mesas_table(),
            cuenta_panel(),
            template_columns=rx.breakpoints(
                initial="1fr",
                xl="minmax(0, 1.3fr) 420px",
            ),
            gap="1.25rem",
            width="100%",
            align_items="start",
        ),
        width="100%",
        spacing="5",
        align="start",
        padding_bottom="1.5rem",
    )

    return rx.box(
        app_shell(
            active="caja",
            title="Caja / Cobro",
            subtitle="Vista de PC para cierre de cuentas, generacion de ticket y liberacion rapida de mesas.",
            action=action_button("Actualizar", RestaurantState.refrescar, icon_tag="wallet"),
            content=content,
        ),
        on_mount=RestaurantState.start_caja_polling,
        on_unmount=RestaurantState.stop_caja_polling,
    )
