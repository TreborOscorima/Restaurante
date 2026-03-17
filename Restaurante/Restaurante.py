"""Aplicación principal del MVP de gestión para restaurantes."""

import reflex as rx

from Restaurante.db.session import init_db
from Restaurante.state.app_state import RestaurantState
from Restaurante.views.admin_ventas import admin_ventas_page
from Restaurante.views.caja import caja_page
from Restaurante.views.catalogo import catalogo_page
from Restaurante.views.cocina import cocina_page
from Restaurante.views.home import home_page
from Restaurante.views.login import login_page
from Restaurante.views.mostrador import mostrador_page
from Restaurante.views.mozos import mozos_page

init_db()

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="orange",
        gray_color="slate",
        radius="large",
        panel_background="solid",
        has_background=False,
    ),
    style={
        "font_family": "Segoe UI, system-ui, sans-serif",
    },
)
app.add_page(
    home_page,
    route="/",
    title="Restaurante MVP",
    on_load=RestaurantState.on_load_root,
)
app.add_page(
    login_page,
    route="/login",
    title="Login",
    on_load=RestaurantState.on_load_login,
)
app.add_page(
    mozos_page,
    route="/mozos",
    title="Mozos",
    on_load=RestaurantState.on_load_mozos,
)
app.add_page(
    caja_page,
    route="/caja",
    title="Caja",
    on_load=RestaurantState.on_load_caja,
)
app.add_page(
    mostrador_page,
    route="/mostrador",
    title="Mostrador",
    on_load=RestaurantState.on_load_mostrador,
)
app.add_page(
    cocina_page,
    route="/cocina",
    title="Cocina",
    on_load=RestaurantState.on_load_cocina,
)
app.add_page(
    catalogo_page,
    route="/catalogo",
    title="Catalogo",
    on_load=RestaurantState.on_load_catalogo,
)
app.add_page(
    admin_ventas_page,
    route="/admin/ventas",
    title="Ventas / Historial",
    on_load=RestaurantState.on_load_admin_ventas,
)
