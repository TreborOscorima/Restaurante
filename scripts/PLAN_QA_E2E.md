# Plan de Pruebas Manuales E2E — TuWaykiApp POS

> **Convención:** `[ ]` = pendiente · `[x]` = aprobado · `[!]` = falla encontrada
> Anotar en cada falla: **qué pasó**, **en qué dispositivo**, **hora**.

---

## 0. Preparación del entorno

- [ ] Ejecutar `.\venv\Scripts\python seed.py` con DB vacía.
- [ ] Abrir `Arrancar_Sistema.bat` y esperar `App running at http://0.0.0.0:3000`.
- [ ] Conectar **al menos 2 dispositivos** (PC + celular/tablet) a la misma red LAN.
- [ ] Tener listos los 4 PINs de prueba: `1111`, `2222`, `3333`, `4444`.

---

## 1. Autenticación

### 1.1 Happy Path
- [ ] Navegar a `/login` → se muestra el numpad táctil.
- [ ] Ingresar `2222` (Juan Mozo) → redirige a `/mozos`.
- [ ] Hacer logout → redirige a `/login` y limpia sesión.
- [ ] Ingresar `3333` (Ana Caja) → redirige a `/caja`.
- [ ] Ingresar `4444` (Luis Cocina) → redirige a `/cocina`.
- [ ] Ingresar `1111` (Admin) → redirige a `/catalogo`.

### 1.2 Flujos alternativos
- [ ] PIN de 3 dígitos (`123`) → mensaje de error, no redirige.
- [ ] PIN incorrecto (`9999`) → `window_alert` "PIN incorrecto", campo se vacía.
- [ ] Acceder a `/mozos` sin sesión → redirige a `/login`.
- [ ] Logueado como Mozo, intentar ir a `/caja` manualmente → `window_alert` + redirige a `/mozos`.
- [ ] Logueado como Caja, intentar ir a `/cocina` manualmente → rechazado.

---

## 2. Flujo de Salón — Mozo (Happy Path completo)

> Loguear como `2222` en una ventana. Abrir `/cocina` como `4444` en otra pestaña.

- [ ] Mapa de mesas carga correctamente (15 mesas, todas Libres).
- [ ] Hacer clic en **Mesa 1** → panel lateral muestra "Mesa 1" activa y carta disponible.
- [ ] Agregar **2x Pollo a la Brasa** al carrito → subtotal correcto en S/.
- [ ] Agregar **1x Chicha Morada** → carrito muestra 3 items.
- [ ] Quitar 1 unidad de Chicha → carrito actualiza a 2 items.
- [ ] Hacer clic en **"Enviar a Cocina"** → mensaje de confirmación, Mesa 1 cambia a estado Ocupada (badge rojo).
- [ ] En `/cocina`: el ticket de Mesa 1 aparece en columna **Pendiente** antes del siguiente poll (≤ 5 s).
- [ ] En cocina: clic **"Empezar a Preparar"** → ítem pasa a columna **En preparación**.
- [ ] En cocina: clic **"Marcar como Listo"** → ítem desaparece del KDS.
- [ ] En `/mozos`: historial muestra el ítem con badge **"Listo para entregar"**.
- [ ] En mozos: clic **"Entregar"** en el ítem → estado cambia a "Entregado al cliente".
- [ ] Comanda vacía de items listos → Mesa 1 limpia en historial.

---

## 3. Flujo de Caja

> Continuar con la Mesa 1 con pedido activo del paso 2.

- [ ] Loguear como `3333` (Ana Caja) en otra pestaña.
- [ ] En `/caja`: Mesa 1 aparece con total correcto.
- [ ] Hacer clic en Mesa 1 → ver detalle de cuenta con ítems y subtotales.
- [ ] Intentar cobrar con ítems **no entregados** → sistema bloquea y muestra advertencia.
- [ ] (Volver a mozos, entregar todos los ítems pendientes.)
- [ ] En caja: volver a intentar cobrar → flujo permitido.
- [ ] Confirmar cobro → Mesa 1 pasa a **Libre** (verde), pedido aparece en `/admin/ventas`.
- [ ] Verificar ticket ESC/POS (si hay impresora) o revisar log de consola para confirmar "Error de impresora" si no hay hardware.

---

## 4. Flujo de Mostrador (Takeaway)

> Loguear como `3333` en `/mostrador`.

- [ ] Ingresar nombre cliente: "Pedro García".
- [ ] Agregar **1x Causa Rellena** desde la carta.
- [ ] Clic **"Cobrar y Enviar a Cocina"** → pedido aparece en KDS (cocina) en ≤ 5 s.
- [ ] En KDS: marcar como listo.
- [ ] En `/mostrador`: pedido aparece en sección **"Listos para Entregar"** con el nombre correcto.
- [ ] Clic **"Entregar"** → pedido baja a **"Últimos Entregados"**.
- [ ] Verificar en `/admin/ventas` que la venta figura como cobrada.
- [ ] Intentar cobrar con carrito vacío → mensaje de error, sin crash.

---

## 5. Catálogo — Admin

> Loguear como `1111`.

- [ ] En `/catalogo`: listar categorías y productos existentes.
- [ ] Crear categoría nueva "Postres" con orden 4 → aparece en la lista.
- [ ] Crear producto "Torta de Chocolate" en "Postres", precio S/ 12.50 → aparece disponible.
- [ ] Editar precio a S/ 14.00 → se refleja en la lista.
- [ ] Desactivar producto → desaparece de la carta en `/mozos` (verificar).
- [ ] Reactivar producto → reaparece en `/mozos`.
- [ ] Intentar crear categoría con nombre duplicado → error controlado, sin crash.

---

## 6. Reportes — Admin

> En `/admin/ventas`.

- [ ] Historial lista las ventas del paso 3 y 4.
- [ ] Total recaudado coincide con la suma de los pedidos pagados.
- [ ] Columnas "Mozo" y "Cajero" muestran los nombres correctos.

---

## 7. Pruebas de concurrencia (2 mozos simultáneos)

> Abrir 2 navegadores/pestañas, cada uno logueado como un usuario diferente.
> Ambos logueados como `2222` (o uno como mozo, otro como admin).

- [ ] **Mozo A** selecciona Mesa 3 y arma carrito.
- [ ] **Mozo B** selecciona Mesa 3 al mismo tiempo.
- [ ] Solo **un pedido** debe crearse para Mesa 3 (verificar en DB o en `/admin/ventas`).
- [ ] El polling de 5 s sincroniza ambas pantallas mostrando el mismo estado de mesa.
- [ ] **Mozo A** envía a cocina. **Mozo B** (con la misma mesa abierta) ve los ítems en historial en ≤ 10 s sin recargar manualmente.

---

## 8. Pruebas de resiliencia

### 8.1 Falla de impresora
- [ ] Configurar `PRINTER_KITCHEN_HOST` a una IP inexistente (ej. `192.168.1.254`).
- [ ] Enviar pedido a cocina → la app **no lanza excepción 500**, el pedido se guarda correctamente.
- [ ] Consola del servidor muestra `Error de impresora: ...` (no silencia el error).
- [ ] Restaurar la IP correcta y verificar que la impresión funciona.

### 8.2 Recarga de página
- [ ] Loguear como mozo, seleccionar mesa, recargar (`F5`) → sesión persiste, datos se mantienen.
- [ ] Loguear como caja, cobrar una mesa, recargar → historial de ventas sigue correcto.

### 8.3 Navegación directa a URL restringida
- [ ] Sin sesión, ir a `http://servidor:3000/caja` → redirige a `/login`.
- [ ] Sesión como Cocina, ir a `/caja` → alerta de permisos + redirige a `/cocina`.

---

## 9. Prueba de backup

- [ ] Ejecutar `scripts\Backup_DB.bat` → archivo `restaurante_YYYYMMDD_HHMMSS.db` creado en `C:\Backups_Norkys\`.
- [ ] Ejecutar 15 veces el bat (o correr `python scripts/backup_db.py` 15 veces) → con `--keep 14` el archivo más antiguo se elimina automáticamente.
- [ ] Copiar el backup a otra carpeta, renombrarlo a `restaurante.db` y arrancar la app → datos intactos.

---

## 10. Prueba de rendimiento básica (6 tablets simuladas)

> Usando el navegador con 6 pestañas abiertas en el mismo equipo (o 6 dispositivos en LAN).

- [ ] Abrir 6 pestañas: 3× `/mozos`, 1× `/cocina`, 1× `/caja`, 1× `/mostrador`.
- [ ] Todas polleando simultáneamente durante 5 minutos sin acción del usuario.
- [ ] Ninguna pestaña muestra error `database is locked` ni spinner infinito.
- [ ] Ejecutar una operación de escritura (enviar a cocina) mientras las otras pestañas pollan → operación completa en < 2 s.

---

## Registro de defectos encontrados

| # | Módulo | Descripción | Severidad | Estado |
|---|--------|-------------|-----------|--------|
|   |        |             |           |        |

---

## Criterios de aceptación para producción

- [ ] Todos los ítems del Happy Path (secciones 2, 3, 4) pasan sin errores.
- [ ] Ningún `500 Internal Server Error` durante las pruebas de resiliencia.
- [ ] Backup genera archivo legible y restaurable.
- [ ] Sin `database is locked` con 6 pestañas simultáneas (sección 10).
