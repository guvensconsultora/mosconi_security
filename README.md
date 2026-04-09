# Mosconi - Seguridad y Accesos

## Introducción

En Odoo estándar, todos los usuarios del grupo de Ventas ven **todos** los pedidos de venta de todos los sitios web. Esto es un problema cuando una empresa opera múltiples tiendas online (ej: minorista y mayorista) con equipos comerciales separados.

**`mosconi_security`** resuelve esto implementando:
- **Segmentación de pedidos por sitio web** mediante record rules por grupo de usuario
- **Notificaciones automáticas por email** cuando un cliente inicia o confirma un pago online
- **Menú de transacciones de pago** accesible sin modo desarrollador

## Funcionamiento para el usuario final

### Segmentación de pedidos

Cada usuario asignado a un grupo restringido solo ve los pedidos del sitio web que le corresponde:

| Grupo | Sitio web | Usuarios |
|-------|-----------|----------|
| Ventas - Crazy Compras | Crazy Compras (website_id=1) | Corina Sosa |
| Ventas - Tu Compra Digital | Tu Compra Digital (website_id=3) | Micaela Santana |

Los pedidos creados manualmente desde el backend (sin website_id) son visibles para ambos grupos.

Los usuarios administradores o del grupo estándar de Ventas siguen viendo todos los pedidos sin restricción.

### Notificaciones de pago

Cuando un cliente realiza un pago online, el sistema envía automáticamente un email a los responsables comerciales:

1. **Transacción pendiente** — El cliente inició el proceso de pago (estado `pending`)
2. **Transacción confirmada** — El pago fue acreditado (estado `done`)

El email incluye: referencia, estado, monto, cliente, proveedor de pago, fecha y un botón directo para ver la transacción en el backend.

**Destinatarios fijos:** marketing@crazycompras.com.ar, cschmidt@mosconi.com.ar

### Menú de transacciones

Los usuarios de los grupos restringidos tienen acceso al menú **Sitio web > Pedidos > Transacciones de Pago**, que normalmente solo es visible en modo desarrollador.

## Parametrización

### 1. Instalar el módulo
Activar el módulo `mosconi_security` desde Ajustes > Aplicaciones.

### 2. Asignar grupos a usuarios
1. Ir a **Ajustes > Usuarios y compañías > Usuarios**
2. Seleccionar el usuario (ej: Corina Sosa)
3. En la pestaña de permisos, agregar el grupo correspondiente:
   - **Ventas - Crazy Compras** para usuarios que operan el sitio minorista
   - **Ventas - Tu Compra Digital** para usuarios que operan el sitio mayorista

### 3. Verificar notificaciones
Las automatizaciones se activan automáticamente al instalar. Para verificar:
1. Ir a **Ajustes > Técnico > Automatizaciones**
2. Buscar "Notificar transacción pendiente" y "Notificar transacción confirmada"
3. Verificar que estén activas

### 4. Cambiar destinatarios de email
Para modificar los destinatarios de las notificaciones:
1. Ir a **Ajustes > Técnico > Plantillas de email**
2. Buscar "Notificación de Transacción de Pago"
3. Editar el campo **Para (Emails)**

## Referencia técnica

### Arquitectura

El módulo es **100% declarativo** (XML + CSV), sin código Python. Implementa:

```
mosconi_security/
├── __manifest__.py
├── __init__.py
├── security/
│   ├── groups.xml          # Grupos de usuario
│   ├── ir.model.access.csv # ACL de lectura en payment.transaction
│   └── rules.xml           # Record rules por website_id
├── data/
│   ├── mail_templates.xml  # Template de email para notificaciones
│   └── automation.xml      # Acciones automatizadas (pending/done)
└── views/
    └── menus.xml           # Menú de transacciones sin modo dev
```

### Grupos de seguridad

| XML ID | Nombre | Propósito |
|--------|--------|-----------|
| `group_sale_crazycompras` | Ventas - Crazy Compras | Restringe a website_id=1 |
| `group_sale_tucompradigital` | Ventas - Tu Compra Digital | Restringe a website_id=3 |

No heredan de ningún grupo estándar — se asignan como grupos adicionales.

### Record Rules

| XML ID | Modelo | Dominio | Grupos |
|--------|--------|---------|--------|
| `rule_sale_order_crazycompras_only` | sale.order | `[('website_id', 'in', [1, False])]` | group_sale_crazycompras |
| `rule_sale_order_tucompradigital_only` | sale.order | `[('website_id', 'in', [3, False])]` | group_sale_tucompradigital |

`website_id=False` se incluye para que los pedidos creados manualmente desde el backend (sin sitio web asociado) sean visibles para ambos grupos.

### ACL (ir.model.access)

| Grupo | Modelo | Lectura | Escritura | Creación | Eliminación |
|-------|--------|---------|-----------|----------|-------------|
| group_sale_crazycompras | payment.transaction | Si | No | No | No |
| group_sale_tucompradigital | payment.transaction | Si | No | No | No |

### Automatizaciones

Dos `base.automation` que escuchan cambios de estado en `payment.transaction`:

- **`automation_payment_pending_notify`** — Trigger: `state` cambia a `pending`
- **`automation_payment_done_notify`** — Trigger: `state` cambia a `done`

Ambas ejecutan una `ir.actions.server` con `state=code` (no `email`, que no existe en Odoo 18) que invoca `send_mail()` con el template definido.

### Decisiones técnicas

- **`state=code` en vez de `state=email`**: En Odoo 18, `ir.actions.server` eliminó el tipo `email`. Se usa `code` con `template.send_mail()` como reemplazo equivalente.
- **Dominio con `website_id in [X, False]`**: Incluir `False` evita que pedidos manuales queden invisibles para usuarios restringidos.
- **Sin código Python**: Todo se resuelve con XML declarativo, minimizando mantenimiento y riesgo de regresiones.

### Dependencias

```python
'depends': ['sale', 'website_sale', 'payment', 'mail', 'base_automation']
```

### Versión y licencia

- **Versión:** 1.0.0
- **Licencia:** LGPL-3
- **Odoo:** 18
