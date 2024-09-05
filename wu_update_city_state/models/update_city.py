from datetime import datetime
import logging
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UpdateCS(models.TransientModel):
    """Wizard form view of generate E-Faktur"""

    _name = 'update.cs'

    def btn_confirm(self):
        active_ids = str(self.get_active_ids())
        self.env.cr.execute("""
            UPDATE sale_order set customer_city = (SELECT rp.city FROM res_partner rp
            WHERE rp.id = sale_order.partner_id)
            WHERE sale_order.id in """+active_ids+"""
            """)
        self.env.cr.execute("""
            UPDATE sale_order set customer_state = (
            SELECT rcs.name FROM res_country_state rcs
            LEFT JOIN res_partner rp on rp.id = sale_order.partner_id
            WHERE rcs.id = rp.state_id)
            WHERE sale_order.id in """+active_ids+"""
            """)

    def get_active_ids(self):
        active_ids = ''
        context = self.env.context
        model_name = context.get('active_model')
        if model_name == 'sale.order':
            move_ids = self.env[model_name].browse(context.get('active_ids'))
            # print("ID MOVE",tuple(move_ids))
            if len(move_ids)>1:
                active_ids = tuple(move_ids.ids)
            elif len(move_ids)==1:
                active_ids = "(%s)" % move_ids.id
        return active_ids


class SaleOrdervLine1(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # add validation
        for x in self.order_line:
            if x.product_id.type == 'product':
                if x.virtual_available_at_date < x.product_uom_qty:
                    raise UserError("Remaining stock of %s -> %s "%(x.product_id.name,x.virtual_available_at_date))
        return super(SaleOrdervLine1, self).action_confirm()


    def delete_qty(self):
        for x in self.order_line:
            x.product_uom_qty = 0.0

    @api.model
    def create(self, vals):
        res = super(SaleOrdervLine1, self).create(vals)
        for item in res:
            for x in item.order_line:
                if not x.analytic_account_so.id:
                    raise UserError("Analytic account for product %s must be filled in"%(x.product_id.name))
        return res