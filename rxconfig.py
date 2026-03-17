import reflex as rx

config = rx.Config(
    app_name="Restaurante",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)