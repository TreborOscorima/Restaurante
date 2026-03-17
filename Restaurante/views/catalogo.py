"""Vista administrativa para catalogo de categorias y productos."""

from __future__ import annotations

import reflex as rx

from Restaurante.state.app_state import CategoriaView, ProductoView, RestaurantState
from Restaurante.views.shared import (
    ACCENT,
    ACCENT_HOVER,
    BORDER_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    action_button,
    app_shell,
    section_card,
    status_banner,
)


def form_label(text: str) -> rx.Component:
    return rx.text(text, color=TEXT_SECONDARY, font_weight="700")


def form_input(value, on_change, placeholder: str) -> rx.Component:
    return rx.input(
        value=value,
        on_change=on_change,
        placeholder=placeholder,
        width="100%",
        style={"background": "rgba(255,255,255,0.04)"},
        color=TEXT_PRIMARY,
        border=f"1px solid {BORDER_COLOR}",
    )


def form_textarea(value, on_change, placeholder: str) -> rx.Component:
    return rx.text_area(
        value=value,
        on_change=on_change,
        placeholder=placeholder,
        width="100%",
        style={"background": "rgba(255,255,255,0.04)"},
        color=TEXT_PRIMARY,
        border=f"1px solid {BORDER_COLOR}",
    )


def categoria_form() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Categorias",
                        color=ACCENT,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.14em",
                        text_transform="uppercase",
                    ),
                    rx.heading("Formulario de categoria", size="5", color=TEXT_PRIMARY),
                    align="start",
                    spacing="1",
                ),
                rx.button(
                    "Nueva",
                    on_click=RestaurantState.nueva_categoria,
                    background="rgba(255,255,255,0.05)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="16px",
                    font_weight="700",
                ),
                width="100%",
                justify="between",
                align="center",
            ),
            form_label("Nombre"),
            form_input(
                RestaurantState.categoria_form_nombre,
                RestaurantState.set_categoria_form_nombre,
                "Ej. Promociones",
            ),
            form_label("Descripcion"),
            form_textarea(
                RestaurantState.categoria_form_descripcion,
                RestaurantState.set_categoria_form_descripcion,
                "Descripcion interna de la categoria",
            ),
            form_label("Orden"),
            form_input(
                RestaurantState.categoria_form_orden,
                RestaurantState.set_categoria_form_orden,
                "1",
            ),
            rx.button(
                rx.cond(
                    RestaurantState.categoria_form_id > 0,
                    "Guardar cambios",
                    "Crear categoria",
                ),
                on_click=RestaurantState.guardar_categoria,
                width="100%",
                background=ACCENT,
                color=TEXT_PRIMARY,
                border_radius="18px",
                padding_y="1.15rem",
                font_weight="800",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            align="start",
            spacing="3",
        ),
        padding="1.2rem",
    )


def categoria_row(categoria: CategoriaView) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(categoria.nombre, color=TEXT_PRIMARY, font_weight="800"),
                    rx.box(
                        rx.cond(categoria.activa, "Activa", "Oculta"),
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={
                            "background": rx.cond(
                                categoria.activa,
                                "rgba(34, 197, 94, 0.16)",
                                "rgba(148, 163, 184, 0.14)",
                            )
                        },
                        color=rx.cond(categoria.activa, "#BBF7D0", TEXT_MUTED),
                        font_weight="700",
                        font_size="0.75rem",
                    ),
                    spacing="2",
                    wrap="wrap",
                    align="center",
                ),
                rx.text(categoria.descripcion, color=TEXT_MUTED),
                rx.text(
                    f"Orden: {categoria.orden}",
                    color=TEXT_MUTED,
                    font_size="0.84rem",
                ),
                align="start",
                spacing="1",
            ),
            rx.hstack(
                rx.button(
                    "Editar",
                    on_click=RestaurantState.editar_categoria(categoria.id),
                    background="rgba(255,255,255,0.05)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="14px",
                ),
                rx.button(
                    rx.cond(categoria.activa, "Ocultar", "Activar"),
                    on_click=RestaurantState.toggle_categoria_activa(categoria.id),
                    background=rx.cond(
                        categoria.activa,
                        "rgba(239, 68, 68, 0.14)",
                        "rgba(34, 197, 94, 0.14)",
                    ),
                    color=rx.cond(categoria.activa, "#FCA5A5", "#BBF7D0"),
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="14px",
                    font_weight="700",
                ),
                spacing="2",
                wrap="wrap",
            ),
            width="100%",
            justify="between",
            align="center",
            gap="0.8rem",
        ),
        width="100%",
        padding="1rem",
        border_radius="22px",
        style={"background": "rgba(255,255,255,0.03)"},
        border=f"1px solid {BORDER_COLOR}",
    )


def categorias_list() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.text(
                "Listado",
                color=ACCENT,
                font_size="0.78rem",
                font_weight="800",
                letter_spacing="0.14em",
                text_transform="uppercase",
            ),
            rx.heading("Categorias registradas", size="5", color=TEXT_PRIMARY),
            rx.vstack(
                rx.foreach(RestaurantState.categorias, categoria_row),
                width="100%",
                spacing="3",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def disponibilidad_selector() -> rx.Component:
    return rx.hstack(
        rx.button(
            "Disponible",
            on_click=RestaurantState.set_producto_form_disponible(True),
            background=rx.cond(
                RestaurantState.producto_form_disponible,
                ACCENT,
                "rgba(255,255,255,0.05)",
            ),
            color=TEXT_PRIMARY,
            border=f"1px solid {BORDER_COLOR}",
            border_radius="14px",
            font_weight="700",
        ),
        rx.button(
            "No disponible",
            on_click=RestaurantState.set_producto_form_disponible(False),
            background=rx.cond(
                RestaurantState.producto_form_disponible,
                "rgba(255,255,255,0.05)",
                "rgba(239, 68, 68, 0.14)",
            ),
            color=rx.cond(
                RestaurantState.producto_form_disponible,
                TEXT_PRIMARY,
                "#FCA5A5",
            ),
            border=f"1px solid {BORDER_COLOR}",
            border_radius="14px",
            font_weight="700",
        ),
        spacing="2",
        wrap="wrap",
    )


def producto_form() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Productos",
                        color=ACCENT,
                        font_size="0.78rem",
                        font_weight="800",
                        letter_spacing="0.14em",
                        text_transform="uppercase",
                    ),
                    rx.heading("Formulario de producto", size="5", color=TEXT_PRIMARY),
                    align="start",
                    spacing="1",
                ),
                rx.button(
                    "Nuevo",
                    on_click=RestaurantState.nuevo_producto,
                    background="rgba(255,255,255,0.05)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="16px",
                    font_weight="700",
                ),
                width="100%",
                justify="between",
                align="center",
            ),
            form_label("Categoria"),
            rx.cond(
                RestaurantState.hay_categorias,
                rx.select(
                    RestaurantState.categoria_opciones,
                    value=RestaurantState.producto_form_categoria_nombre,
                    on_change=RestaurantState.set_producto_form_categoria_nombre,
                    width="100%",
                    style={"background": "rgba(255,255,255,0.04)"},
                    color=TEXT_PRIMARY,
                ),
                rx.box(
                    "Primero crea una categoria.",
                    width="100%",
                    padding="0.9rem 1rem",
                    border_radius="16px",
                    style={"background": "rgba(239, 68, 68, 0.12)"},
                    color="#FCA5A5",
                ),
            ),
            form_label("Nombre"),
            form_input(
                RestaurantState.producto_form_nombre,
                RestaurantState.set_producto_form_nombre,
                "Ej. 1/4 de Pollo a la Brasa",
            ),
            form_label("Descripcion"),
            form_textarea(
                RestaurantState.producto_form_descripcion,
                RestaurantState.set_producto_form_descripcion,
                "Descripcion breve del producto",
            ),
            form_label("Precio"),
            form_input(
                RestaurantState.producto_form_precio,
                RestaurantState.set_producto_form_precio,
                "0.00",
            ),
            form_label("Disponibilidad"),
            disponibilidad_selector(),
            rx.button(
                rx.cond(
                    RestaurantState.producto_form_id > 0,
                    "Guardar cambios",
                    "Crear producto",
                ),
                on_click=RestaurantState.guardar_producto,
                width="100%",
                background=ACCENT,
                color=TEXT_PRIMARY,
                border_radius="18px",
                padding_y="1.15rem",
                font_weight="800",
                _hover={"background": ACCENT_HOVER},
            ),
            width="100%",
            align="start",
            spacing="3",
        ),
        padding="1.2rem",
    )


def producto_row(producto: ProductoView) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(producto.nombre, color=TEXT_PRIMARY, font_weight="800"),
                    rx.box(
                        producto.categoria_nombre,
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={"background": "rgba(255,255,255,0.05)"},
                        color=TEXT_MUTED,
                        font_size="0.75rem",
                        font_weight="700",
                    ),
                    rx.box(
                        rx.cond(producto.disponible, "Visible", "Oculto"),
                        padding="0.25rem 0.65rem",
                        border_radius="999px",
                        style={
                            "background": rx.cond(
                                producto.disponible,
                                "rgba(34, 197, 94, 0.16)",
                                "rgba(148, 163, 184, 0.14)",
                            )
                        },
                        color=rx.cond(producto.disponible, "#BBF7D0", TEXT_MUTED),
                        font_weight="700",
                        font_size="0.75rem",
                    ),
                    spacing="2",
                    wrap="wrap",
                    align="center",
                ),
                rx.text(producto.descripcion, color=TEXT_MUTED),
                rx.text(producto.precio_texto, color="#FDBA74", font_weight="800"),
                align="start",
                spacing="1",
            ),
            rx.hstack(
                rx.button(
                    "Editar",
                    on_click=RestaurantState.editar_producto(producto.id),
                    background="rgba(255,255,255,0.05)",
                    color=TEXT_PRIMARY,
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="14px",
                ),
                rx.button(
                    rx.cond(producto.disponible, "Ocultar", "Activar"),
                    on_click=RestaurantState.toggle_producto_disponible(producto.id),
                    background=rx.cond(
                        producto.disponible,
                        "rgba(239, 68, 68, 0.14)",
                        "rgba(34, 197, 94, 0.14)",
                    ),
                    color=rx.cond(producto.disponible, "#FCA5A5", "#BBF7D0"),
                    border=f"1px solid {BORDER_COLOR}",
                    border_radius="14px",
                    font_weight="700",
                ),
                spacing="2",
                wrap="wrap",
            ),
            width="100%",
            justify="between",
            align="center",
            gap="0.8rem",
        ),
        width="100%",
        padding="1rem",
        border_radius="22px",
        style={"background": "rgba(255,255,255,0.03)"},
        border=f"1px solid {BORDER_COLOR}",
    )


def productos_list() -> rx.Component:
    return section_card(
        rx.vstack(
            rx.text(
                "Menu",
                color=ACCENT,
                font_size="0.78rem",
                font_weight="800",
                letter_spacing="0.14em",
                text_transform="uppercase",
            ),
            rx.heading("Productos registrados", size="5", color=TEXT_PRIMARY),
            rx.vstack(
                rx.foreach(RestaurantState.productos, producto_row),
                width="100%",
                spacing="3",
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        padding="1.2rem",
    )


def catalogo_page() -> rx.Component:
    content = rx.vstack(
        status_banner(
            rx.cond(
                RestaurantState.mensaje != "",
                RestaurantState.mensaje,
                "Administra categorias y productos con una interfaz coherente con el resto del POS.",
            )
        ),
        rx.grid(
            categoria_form(),
            categorias_list(),
            template_columns=rx.breakpoints(
                initial="1fr",
                xl="minmax(360px, 420px) minmax(0, 1fr)",
            ),
            gap="1.25rem",
            width="100%",
        ),
        rx.grid(
            producto_form(),
            productos_list(),
            template_columns=rx.breakpoints(
                initial="1fr",
                xl="minmax(360px, 420px) minmax(0, 1fr)",
            ),
            gap="1.25rem",
            width="100%",
        ),
        width="100%",
        spacing="5",
        align="start",
        padding_bottom="1.5rem",
    )

    return app_shell(
        active="catalogo",
        title="Catalogo / Menu",
        subtitle="Gestion del catalogo con formularios oscuros, edicion rapida y visibilidad de disponibilidad.",
        action=action_button("Actualizar", RestaurantState.refrescar, icon_tag="book_open"),
        content=content,
    )
