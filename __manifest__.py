{
    'name': 'Mosconi - Seguridad y Accesos',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Record rules para restringir pedidos por sitio web',
    'description': 'Restringe usuarios del grupo Ventas Crazycompras a ver solo pedidos del website_id=1',
    'depends': ['sale', 'website_sale', 'payment', 'mail', 'base_automation'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/automation.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
