"""Vista de venta rápida para pedidos de mostrador y para llevar."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import (
    CarritoItem,
    CategoriaView,
    MostradorEntregaView,
    MostradorEntregadoView,
    ProductoView,
    RestaurantState,
)
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_BG,
    ACCENT_GLOW,
    ACCENT_HOVER,
    BORDER_ACCENT,
    BORDER_COLOR,
    SURFACE_ELEVATED,
    SURFACE_GHOST,
    SURFACE_HOVER,
    SURFACE_MUTED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    action_button,
    app_shell,
    section_card,
    status_banner,
    surface_card,
)


def category_button(categoria: CategoriaView) -> rx.Component:
    is_active = RestaurantState.mostrador_categoria_activa_id == categoria.id
    return rx.button(
        categoria.nombre,
        on_click=RestaurantState.seleccionar_mostrador_categoria(categoria.id),
        background=rx.cond(is_active, ACCENT, SURFACE_GHOST),
        color=TEXT_PRIMARY,
        border=rx.cond(
            is_active,
            f"1px solid {BORDER_ACCENT}",
            f"1px solid {BORDER_COLOR}",
        ),
        border_radius="999px",
        padding_x="1rem",
        padding_y="0.95rem",
        font_weight="700",
        _hover={"background": rx.cond(is_active, ACCENT_HOVER, SURFACE_HOVER)},
    )


def all_categories_button() -> rx.Component:
    is_active = RestaurantState.mostrador_categoria_activa_id == 0
    return rx.button(
        "Todas",
        on_click=RestaurantState.seleccionar_mostrador_categoria(0),
        background=rx.cond(is_active, ACCENT, SURFACE_GHOST),
        color=TEXT_PRIMARY,
        border=rx.cond(
            is_active,
            f"1px solid {BORDER_ACCENT}",
            f"1px solid {BORDER_COLOR}",
        ),
        border_radius="999px",
        padding_x="1rem",
        padding_y="0.95rem",
        font_weight="700",
        _hover={"background": rx.cond(is_active, ACCENT_HOVER, SURFACE_HOVER)},
    )


def producto_card(producto: ProductoView) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(tag="shopping_bag", size=22, color="#FDBA74"),
                width="76px",
                height="76px",
                border_radius="22px",
                style={
                    "background": (
                        "linear-gradient(135deg, #3D1A06 0%, #2A1208 100%)"
                    )
                },
                border=f"1px solid {BORDER_ACCENT}",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(producto.nombre, color=TEXT_PRIMARY, font_weight="800"),
                    rx.box(
                        producto.categoria_nombre,
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={"background": SURFACE_GHOST},
                        color=TEXT_MUTED,
                        font_size="0.74rem",
                        font_weight="700",
                    ),
                    spacing="2",
                    wrap="wrap",
                    align="center",
                ),
                rx.text(
                    producto.descripcion,
                    color=TEXT_MUTED,
                    font_size="0.9rem",
                    min_height="40px",
                ),
                rx.text(
                    producto.precio_texto,
                    color="#FDBA74",
                    font_weight="800",
                    font_size="1.12rem",
                ),
                width="100%",
                align="start",
                spacing="2",
            ),
            rx.button(
                "+",
                on_click=RestaurantState.agregar_producto_mostrador(producto.id),
                width="56px",
                height="56px",
                border_radius="20px",
                background=ACCENT,
                color=TEXT_PRIMARY,
                font_size="1.6rem",
                font_weight="800",
                flex_shrink="0",
                box_shadow=ACCENT_GLOW,
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            spacing="4",
            align="center",
        ),
        width="100%",
        padding="1rem",
        style={"background": "#1A2438"},
        border=f"1px solid {BORDER_COLOR}",
        border_radius="26px",
        box_shadow="0 12px 28px rgba(2, 6, 23, 0.22)",
    )


def carrito_row(item: CarritoItem) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(item.nombre, color=TEXT_PRIMARY, font_weight="700"),
                rx.text(item.subtotal_texto, color=TEXT_PRIMARY, font_weight="800"),
                width="100%",
                justify="between",
            ),
            rx.hstack(
                rx.button(
                    "-",
                    on_click=RestaurantState.restar_producto_mostrador(item.producto_id),
                    width="34px",
                    height="34px",
                    border_radius="12px",
                    background=SURFACE_GHOST,
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    item.cantidad,
                    min_width="38px",
                    text_align="center",
                    color=TEXT_PRIMARY,
                    font_weight="800",
                ),
                rx.button(
                    "+",
                    on_click=RestaurantState.agregar_producto_mostrador(item.producto_id),
                    width="34px",
                    height="34px",
                    border_radius="12px",
                    background=ACCENT,
                    color=TEXT_PRIMARY,
                    _hover={"background": ACCENT_HOVER},
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            align="start",
            spacing="3",
        ),
        width="100%",
        padding="0.9rem",
        border_radius="20px",
        style={"background": SURFACE_MUTED},
        border=f"1px solid {BORDER_COLOR}",
    )


def carrito_panel() -> rx.Component:
    return surface_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Venta rapida",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading("Pedido para llevar", size="5", color=TEXT_PRIMARY),
                rx.text(
                    "Cobra, imprime y manda a cocina desde una sola pantalla.",
                    color=TEXT_MUTED,
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.input(
                value=RestaurantState.mostrador_cliente_nombre,
                on_change=RestaurantState.set_mostrador_cliente_nombre,
                placeholder="Nombre del cliente",
                width="100%",
                size="3",
                style={"background": SURFACE_ELEVATED},
                color=TEXT_PRIMARY,
                border=f"1px solid {BORDER_COLOR}",
            ),
            rx.hstack(
                rx.box(
                    rx.text("Items", color=TEXT_MUTED, font_size="0.78rem"),
                    rx.text(
                        RestaurantState.cantidad_items_mostrador,
                        color=TEXT_PRIMARY,
                        font_size="1.25rem",
                        font_weight="800",
                    ),
                    width="100%",
                    padding="0.85rem",
                    border_radius="18px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                rx.box(
                    rx.text("Total", color=TEXT_MUTED, font_size="0.78rem"),
                    rx.text(
                        RestaurantState.total_mostrador_texto,
                        color=TEXT_PRIMARY,
                        font_size="1.25rem",
                        font_weight="800",
                    ),
                    width="100%",
                    padding="0.85rem",
                    border_radius="18px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px solid {BORDER_COLOR}",
                ),
                width="100%",
                spacing="3",
            ),
            rx.cond(
                RestaurantState.cantidad_items_mostrador > 0,
                rx.vstack(
                    rx.foreach(RestaurantState.mostrador_carrito, carrito_row),
                    width="100%",
                    spacing="3",
                ),
                rx.box(
                    "Todavia no agregaste productos al pedido de mostrador.",
                    width="100%",
                    padding="1.15rem",
                    border_radius="20px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px dashed {BORDER_COLOR}",
                    color=TEXT_MUTED,
                    text_align="center",
                ),
            ),
            rx.vstack(
                rx.button(
                    "Cobrar y Enviar",
                    on_click=RestaurantState.cobrar_y_enviar_mostrador,
                    width="100%",
                    background=ACCENT,
                    color=TEXT_PRIMARY,
                    border_radius="18px",
                    padding_y="1.35rem",
                    font_weight="800",
                    _hover={"background": ACCENT_HOVER},
                ),
                rx.button(
                    "Limpiar carrito",
                    on_click=RestaurantState.limpiar_carrito_mostrador,
                    width="100%",
                    background=SURFACE_GHOST,
                    color=TEXT_SECONDARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="18px",
                    padding_y="1.15rem",
                    font_weight="700",
                ),
                width="100%",
                spacing="3",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        width=rx.breakpoints(initial="100%", xl="380px"),
        min_width=rx.breakpoints(initial="100%", xl="380px"),
        padding="1.2rem",
        background="linear-gradient(160deg, #131F33 0%, #0F1826 100%)",
    )


def pedido_item(line: str) -> rx.Component:
    return rx.box(
        line,
        width="100%",
        padding="0.72rem 0.85rem",
        border_radius="16px",
        style={"background": SURFACE_GHOST},
        border=f"1px solid {BORDER_COLOR}",
        color=TEXT_SECONDARY,
        font_weight="600",
    )


def pedido_listo_card(pedido: MostradorEntregaView) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Cliente listo",
                        color=ACCENT,
                        font_size="0.76rem",
                        font_weight="800",
                        letter_spacing="0.12em",
                        text_transform="uppercase",
                    ),
                    rx.heading(pedido.cliente_nombre, size="5", color=TEXT_PRIMARY),
                    rx.text(
                        f"Pedido #{pedido.pedido_id} · {pedido.hora_texto}",
                        color=TEXT_MUTED,
                        font_weight="600",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.box(
                    f"{pedido.items_count} item(s)",
                    padding="0.3rem 0.75rem",
                    border_radius="999px",
                    style={"background": ACCENT_BG},
                    color="#FDBA74",
                    font_weight="800",
                    font_size="0.8rem",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.vstack(
                rx.foreach(pedido.items_lines, pedido_item),
                width="100%",
                spacing="3",
            ),
            rx.button(
                "Entregar al Cliente",
                on_click=RestaurantState.entregar_pedido_mostrador(pedido.pedido_id),
                width="100%",
                background=ACCENT,
                color=TEXT_PRIMARY,
                border_radius="16px",
                padding_y="1.15rem",
                font_weight="800",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        width="100%",
        padding="1.1rem",
        style={"background": ACCENT_BG},
        border=f"1px solid {BORDER_ACCENT}",
        border_radius="24px",
    )


def pedidos_listos_panel() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Entrega",
                        color=ACCENT,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.14em",
                        text_transform="uppercase",
                    ),
                    rx.heading(
                        "Pedidos Listos para Entregar",
                        size="4",
                        color=TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Llama al cliente apenas cocina deje el pedido listo.",
                        color=TEXT_MUTED,
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.box(
                    RestaurantState.cantidad_pedidos_mostrador_listos,
                    min_width="44px",
                    text_align="center",
                    padding="0.55rem 0.85rem",
                    border_radius="999px",
                    style={"background": ACCENT_BG},
                    color="#FDBA74",
                    font_weight="800",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.cond(
                RestaurantState.hay_pedidos_mostrador_listos,
                rx.vstack(
                    rx.foreach(RestaurantState.pedidos_mostrador_listos, pedido_listo_card),
                    width="100%",
                    spacing="3",
                ),
                rx.box(
                    "Todavia no hay pedidos takeaway listos para entregar.",
                    width="100%",
                    padding="1.15rem",
                    border_radius="20px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px dashed {BORDER_COLOR}",
                    color=TEXT_MUTED,
                    text_align="center",
                ),
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.15rem",
    )


def pedido_entregado_card(pedido: MostradorEntregadoView) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        pedido.cliente_nombre,
                        color=TEXT_SECONDARY,
                        font_weight="700",
                    ),
                    rx.text(
                        f"Pedido #{pedido.pedido_id} · {pedido.hora_texto}",
                        color=TEXT_MUTED,
                        font_size="0.82rem",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.text(
                    pedido.total_texto,
                    color="#FDBA74",
                    font_weight="800",
                    font_size="0.95rem",
                ),
                width="100%",
                justify="between",
                align="start",
            ),
            rx.text(pedido.items_resumen, color=TEXT_MUTED, font_size="0.86rem"),
            width="100%",
            align="start",
            spacing="2",
        ),
        width="100%",
        padding="0.95rem 1rem",
        border_radius="18px",
        style={"background": SURFACE_MUTED},
        border=f"1px solid {BORDER_COLOR}",
        opacity="0.92",
    )


def pedidos_entregados_panel() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Historial corto",
                    color=TEXT_MUTED,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading("Ultimos Entregados", size="4", color=TEXT_PRIMARY),
                rx.text(
                    "Ultimos 10 pedidos entregados desde mostrador.",
                    color=TEXT_MUTED,
                ),
                align="start",
                spacing="1",
                width="100%",
            ),
            rx.cond(
                RestaurantState.hay_pedidos_mostrador_entregados,
                rx.vstack(
                    rx.foreach(
                        RestaurantState.pedidos_mostrador_entregados,
                        pedido_entregado_card,
                    ),
                    width="100%",
                    spacing="3",
                ),
                rx.box(
                    "Aun no hay entregas recientes registradas.",
                    width="100%",
                    padding="1.1rem",
                    border_radius="18px",
                    style={"background": SURFACE_MUTED},
                    border=f"1px dashed {BORDER_COLOR}",
                    color=TEXT_MUTED,
                    text_align="center",
                ),
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.15rem",
        background="#0F1826",
    )


def catalog_section() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.vstack(
                rx.text(
                    "Takeaway",
                    color=ACCENT,
                    font_size="0.78rem",
                    font_weight="800",
                    letter_spacing="0.14em",
                    text_transform="uppercase",
                ),
                rx.heading("Catalogo de mostrador", size="6", color=TEXT_PRIMARY),
                rx.text(
                    "Toma pedidos sin mesa y manten el flujo rapido en horas punta.",
                    color=TEXT_MUTED,
                ),
                align="start",
                spacing="1",
            ),
            rx.flex(
                all_categories_button(),
                rx.foreach(RestaurantState.categorias_activas, category_button),
                wrap="wrap",
                gap="0.75rem",
                width="100%",
            ),
            rx.grid(
                rx.foreach(RestaurantState.productos_filtrados_mostrador, producto_card),
                template_columns=rx.breakpoints(
                    initial="1fr",
                    xl="repeat(2, minmax(0, 1fr))",
                ),
                gap="1rem",
                width="100%",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def mostrador_page() -> rx.Component:
    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Mostrador en modo rapido: cobra primero, despacha despues y sigue el ciclo de entrega sin salir de la pantalla.",
            )
        ),
        rx.grid(
            catalog_section(),
            rx.vstack(
                carrito_panel(),
                pedidos_listos_panel(),
                pedidos_entregados_panel(),
                width=rx.breakpoints(initial="100%", xl="380px"),
                min_width=rx.breakpoints(initial="100%", xl="380px"),
                spacing="4",
            ),
            template_columns=rx.breakpoints(
                initial="1fr",
                xl="minmax(0, 1.45fr) 380px",
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
            active="mostrador",
            title="Mostrador / Takeaway",
            subtitle="Venta rapida para llevar con cobro inmediato, impresion automatica y seguimiento de entrega.",
            action=action_button(
                "Actualizar",
                RestaurantState.refrescar_mostrador,
                icon_tag="shopping_bag",
            ),
            content=content,
        ),
        on_mount=RestaurantState.start_mostrador_polling,
        on_unmount=RestaurantState.stop_mostrador_polling,
    )
