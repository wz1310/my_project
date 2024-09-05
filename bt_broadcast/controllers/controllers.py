import json

from odoo import http
from odoo.http import request


class BroadcastController(http.Controller):
    @http.route(['/broadcast'], type='http', auth="public", methods=['GET'], website=True, sitemap=False)
    def broadcast(self, broadcast=""):
        broadcast = request.env['bt_broadcast.broadcast'].search([('is_notification','=',True)], limit=1)

        return json.dumps({
            'name': broadcast.name,
            'description': broadcast.description,
            'type_notification': broadcast.type_notification,
            'is_notification': broadcast.is_notification,
        }, ensure_ascii=False)