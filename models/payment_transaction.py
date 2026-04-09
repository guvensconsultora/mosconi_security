from markupsafe import Markup
from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _build_notification_body(self):
        """Construye el HTML del email de notificacion directamente en Python.
        Sin motor de plantillas: sin riesgo de sintaxis incorrecta (Mako vs Jinja2).
        """
        self.ensure_one()
        o = self

        if o.state == 'pending':
            state_label = 'Pendiente de confirmacion'
            state_color = '#e67e22'
        elif o.state == 'done':
            state_label = 'Pago confirmado'
            state_color = '#27ae60'
        else:
            state_label = o.state or ''
            state_color = '#333'

        body = """
<div style="font-family: Arial, sans-serif; max-width: 600px;">
    <h2 style="color: #875A7B;">Notificacion de Transaccion de Pago</h2>
    <table style="width: 100%%; border-collapse: collapse; margin-top: 10px;">
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Referencia</td>
            <td style="padding: 8px; border: 1px solid #ddd;">%(reference)s</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Estado</td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <span style="color: %(state_color)s;">%(state_label)s</span>
            </td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Monto</td>
            <td style="padding: 8px; border: 1px solid #ddd;">%(amount)s %(currency)s</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Cliente</td>
            <td style="padding: 8px; border: 1px solid #ddd;">%(partner)s</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Proveedor de Pago</td>
            <td style="padding: 8px; border: 1px solid #ddd;">%(provider)s</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Fecha</td>
            <td style="padding: 8px; border: 1px solid #ddd;">%(date)s</td>
        </tr>
    </table>
    <div style="margin-top: 20px;">
        <a href="%(base_url)s/odoo/payment/transactions/%(tx_id)s"
           style="background-color: #875A7B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
            Ver Transaccion
        </a>
    </div>
</div>
""" % {
            'reference': o.reference or '',
            'state_color': state_color,
            'state_label': state_label,
            'amount': o.amount,
            'currency': o.currency_id.name or '',
            'partner': o.partner_id.name or '',
            'provider': o.provider_id.name or '',
            'date': o.last_state_change or '',
            'base_url': o.get_base_url(),
            'tx_id': o.id,
        }
        return body

    def _send_payment_notification(self):
        """Envia email de notificacion a Corina y Carlos sobre el estado de la transaccion.
        Llamado desde la automatizacion en data/automation.xml.
        """
        for rec in self:
            body = rec._build_notification_body()
            subject = 'Transaccion de Pago - %s - %s' % (
                rec.reference or '', rec.state or '')
            self.env['mail.mail'].create({
                'subject': subject,
                'email_to': 'marketing@crazycompras.com.ar,cschmidt@mosconi.com.ar,info@yaguven.com',
                'body_html': Markup(body),
            }).send()
