"""Vista administrativa para historial de ventas cerradas."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import RestaurantState, VentaHistorialView
from Restaurante.views.shared import (
    ACCENT,
    BORDER_COLOR,
    SURFACE_MUTED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    action_button,
    app_shell,
    kpi_card,
    section_card,
    status_banner,
)


def venta_row(item: VentaHistorialView) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(f"#{item.pedido_id}", color=TEXT_PRIMARY, font_weight="800")
        ),
        rx.table.cell(rx.text(item.mesa_label, color=TEXT_SECONDARY, font_weight="700")),
        rx.table.cell(rx.text(item.total_texto, color="#FDBA74", font_weight="800")),
        rx.table.cell(rx.text(item.mozo_nombre, color=TEXT_SECONDARY)),
        rx.table.cell(rx.text(item.cajero_nombre, color=TEXT_SECONDARY)),
    )


def sales_table() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Historial",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading("Ventas cerradas", size="6", color=TEXT_PRIMARY),
                rx.text(
                    "Reporte consolidado con mozo y cajero responsables de cada venta.",
                    color=TEXT_MUTED,
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.cond(
                RestaurantState.hay_historial_ventas,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID Pedido"),
                                rx.table.column_header_cell("Mesa"),
                                rx.table.column_header_cell("Total"),
                                rx.table.column_header_cell("Atendido por"),
                                rx.table.column_header_cell("Cobrado por"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(RestaurantState.historial_ventas, venta_row)
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
                        rx.heading("Sin ventas cerradas", size="5", color=TEXT_PRIMARY),
                        rx.text(
                            "Cuando se registren cobros, apareceran aqui con trazabilidad completa.",
                            color=TEXT_MUTED,
                            text_align="center",
                            max_width="420px",
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


def admin_ventas_page() -> rx.Component:
    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Panel de control para dueño o administrador con foco en recaudacion y responsables por venta.",
            )
        ),
        rx.grid(
            kpi_card(
                "Total recaudado",
                RestaurantState.total_recaudado_texto,
                "Suma de pedidos cerrados",
            ),
            kpi_card(
                "Mesas atendidas",
                RestaurantState.total_mesas_atendidas,
                "Cobros confirmados",
            ),
            template_columns=rx.breakpoints(
                initial="1fr",
                lg="repeat(2, minmax(0, 1fr))",
            ),
            gap="1rem",
            width="100%",
        ),
        sales_table(),
        width="100%",
        spacing="5",
        align="start",
        padding_bottom="1.5rem",
    )

    return rx.box(
        app_shell(
            active="admin_ventas",
            title="Reportes / Ventas",
            subtitle="Historial administrativo de ventas cerradas con trazabilidad de mozos y caja.",
            action=action_button(
                "Actualizar",
                RestaurantState.cargar_historial_ventas,
                icon_tag="receipt_text",
            ),
            content=content,
        ),
        on_mount=RestaurantState.cargar_historial_ventas,
    )
