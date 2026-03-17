"""Vista KDS para cocina con flujo de producción por estados."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import CocinaTicketView, RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_HOVER,
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
)


def ticket_item(line: str) -> rx.Component:
    return rx.box(
        line,
        width="100%",
        padding="0.78rem 0.9rem",
        border_radius="16px",
        style={"background": SURFACE_GHOST},
        border=f"1px solid {BORDER_COLOR}",
        color=TEXT_SECONDARY,
        font_weight="600",
    )


def ticket_card(ticket: CocinaTicketView, mode: str) -> rx.Component:
    action = (
        RestaurantState.iniciar_preparacion_ticket(ticket.detalle_ids_csv)
        if mode == "pendiente"
        else RestaurantState.marcar_ticket_listo(ticket.detalle_ids_csv)
    )
    action_label = "Empezar a Preparar" if mode == "pendiente" else "Marcar como Listo"

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        ticket.mesa_label,
                        color=TEXT_PRIMARY,
                        font_weight="800",
                        font_size="1.18rem",
                    ),
                    rx.text(
                        f"Pedido #{ticket.pedido_id}",
                        color=TEXT_MUTED,
                        font_weight="700",
                    ),
                    rx.cond(
                        ticket.mozo_nombre != "",
                        rx.text(
                            f"Mozo: {ticket.mozo_nombre}",
                            color="#FDBA74",
                            font_weight="600",
                            font_size="0.84rem",
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.box(
                        ticket.estado_label,
                        padding="0.3rem 0.75rem",
                        border_radius="999px",
                        style={"background": ticket.estado_bg},
                        color=ticket.estado_color,
                        font_weight="800",
                        font_size="0.78rem",
                    ),
                    rx.text(ticket.hora_texto, color=TEXT_MUTED, font_weight="700"),
                    align="end",
                    spacing="2",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.box(height="1px", width="100%", style={"background": ticket.accent_border}),
            rx.vstack(
                rx.foreach(ticket.items_lines, ticket_item),
                width="100%",
                spacing="3",
            ),
            rx.button(
                action_label,
                on_click=action,
                width="100%",
                background=ACCENT,
                color=TEXT_PRIMARY,
                border_radius="18px",
                padding_y="1.2rem",
                font_weight="800",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        style={"background": ticket.accent_bg},
        border=f"1px solid {ticket.accent_border}",
        border_radius="26px",
        box_shadow="0 18px 44px rgba(2, 6, 23, 0.26)",
        padding="1.15rem",
        width="100%",
    )


def empty_state(title: str, message: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(title, size="5", color=TEXT_PRIMARY),
            rx.text(
                message,
                color=TEXT_MUTED,
                text_align="center",
                max_width="320px",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="2.8rem 1.25rem",
        border_radius="24px",
        style={"background": SURFACE_MUTED},
        border=f"1px dashed {BORDER_COLOR}",
    )


def kds_column(
    eyebrow: str,
    title: str,
    description: str,
    tickets,
    has_tickets,
    mode: str,
    empty_title: str,
    empty_message: str,
) -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    eyebrow,
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading(title, size="6", color=TEXT_PRIMARY),
                rx.text(description, color=TEXT_MUTED),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.cond(
                has_tickets,
                rx.vstack(
                    rx.foreach(tickets, lambda ticket: ticket_card(ticket, mode)),
                    width="100%",
                    spacing="4",
                ),
                empty_state(empty_title, empty_message),
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def cocina_page() -> rx.Component:
    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Los tickets aparecen solos. Cuando un pedido se marca como listo, desaparece del KDS y pasa a sala o mostrador.",
            )
        ),
        rx.grid(
            kpi_card("Nuevos", RestaurantState.cantidad_tickets_nuevos, "Pendientes de iniciar"),
            kpi_card(
                "En preparacion",
                RestaurantState.cantidad_tickets_en_preparacion,
                "Produccion activa",
            ),
            kpi_card(
                "Mesas esperando entrega",
                RestaurantState.mesas_con_alerta_entrega,
                "Listos fuera de cocina",
            ),
            template_columns=rx.breakpoints(
                initial="repeat(2, minmax(0, 1fr))",
                lg="repeat(3, minmax(0, 1fr))",
            ),
            gap="1rem",
            width="100%",
        ),
        rx.grid(
            kds_column(
                "Nuevos",
                "Pendiente de iniciar",
                "Pedidos recien llegados al pase de cocina.",
                RestaurantState.tickets_nuevos,
                RestaurantState.cantidad_tickets_nuevos > 0,
                "pendiente",
                "Sin tickets nuevos",
                "Los nuevos pedidos apareceran aqui automaticamente.",
            ),
            kds_column(
                "En curso",
                "Preparacion activa",
                "Pedidos que ya se estan trabajando y deben pasar a listos.",
                RestaurantState.tickets_en_preparacion,
                RestaurantState.cantidad_tickets_en_preparacion > 0,
                "preparacion",
                "Sin tickets en curso",
                "Cuando un cocinero empiece un ticket se movera aqui.",
            ),
            template_columns=rx.breakpoints(
                initial="1fr",
                md="repeat(2, minmax(0, 1fr))",
            ),
            gap="1.25rem",
            width="100%",
        ),
        width="100%",
        spacing="5",
        align="start",
        padding_bottom="1.5rem",
    )

    return rx.box(
        app_shell(
            active="cocina",
            title="Cocina / KDS",
            subtitle="Kitchen Display System en tiempo real para producir, mover tickets y despachar sin depender del navegador.",
            action=action_button("Actualizar", RestaurantState.refrescar, icon_tag="chef_hat"),
            content=content,
        ),
        on_mount=RestaurantState.start_cocina_polling,
        on_unmount=RestaurantState.stop_cocina_polling,
    )
