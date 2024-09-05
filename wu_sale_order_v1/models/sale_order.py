# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError,RedirectWarning,AccessError
from datetime import timedelta
import re
import datetime,json

import logging,base64
_logger = logging.getLogger(__name__)

# ///////////test push git////////////////

class SaleOrderv1(models.Model):
    _inherit = 'sale.order'

    down_pay = fields.Float(string="Down Payment")
    stat_download = fields.Boolean(default=False, copy=False)
    customer_state = fields.Char()
    customer_city = fields.Char()

    @api.onchange('partner_id')
    def onchange_partner_id_state(self):
        for x in self:
            x.customer_state = x.partner_id.state_id.name
            x.customer_city = x.partner_id.city

    def set_download(self):
        self.stat_download = True

    def action_wizard_commit(self):
        pdf = self.env.ref('wu_sale_order_v1.action_commit_letter').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        ir_values ={
        'name': "Commitment Letter.pdf",
        'type': 'binary',
        'datas': b64_pdf,
        'store_fname': b64_pdf,
        'mimetype': 'application/x-pdf',
        }
        self.export_file = b64_pdf
        context = dict(self.env.context or {})
        context.update({
            'active_id':self.id,
            'active_ids':self.ids,
            })
        wizard_id = self.env['show.commit.wizard'].create({
            'export_file': b64_pdf
            })
        form = self.env.ref('wu_sale_order_v1.open_commit_wizard_view')
        action = {
        'name': "%s" % (_('Commitment Letter')),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'show.commit.wizard',
        'view_id': form.id,
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        # 'context': context,
        'target': 'new'
        }
        return action

    def action_confirm(self):
        res = super(SaleOrderv1, self).action_confirm()
        for w in self.order_line:
            # if 'MESIN' in w.name and not self.stat_download:
            if w.product_id.nrs_product_mesin and not self.stat_download:
                if self.payment_term_id.line_ids.filtered(lambda x:x.value == 'balance').days >=90:
                    return self.action_wizard_commit()
        return res


class Showcmt(models.TransientModel):
    _name = 'show.commit.wizard'

    export_file_create_date = fields.Date(string='Generation Date', default=fields.Date.today, readonly=True, help="Creation date of the related export file.")
    export_file = fields.Binary(string='File', help="Export file related to this batch")
    export_filename = fields.Char(string='File Name', help="Name of the export file generated for this batch", store=True)
    # so_id = fields.Many2one('sale.order', string="SO ID")


    def confirm(self):
        res_id = self._context.get('active_id')
        model = self._context.get('active_model')
        if not res_id or not model:
            raise UserError("Require to get context active id and active model!")
        
        Env = self.env[model]
        Record = Env.sudo().browse(res_id)
        # print("WIZARDDDDD ID", self.id)
        self.env.cr.execute("""UPDATE sale_order SET stat_download='t' WHERE id=%s""",(res_id,))
        self.env.cr.execute("""DELETE FROM show_commit_wizard WHERE id=%s""",(self.id,))
        # return self.env.ref('wu_sale_order_v1.action_commit_letter').report_action(res_id)
        action = self.env.ref('wu_sale_order_v1.action_commit_letter').report_action(res_id)
        action.update({'close_on_report_download': True})
        return action

        # try:
        #     self.env.ref('wu_sale_order_v1.action_commit_letter').report_action(res_id)
        # except:
        #     None

        # return {
        # 'type': 'ir.actions.act_url',
        # 'name': 'contract',
        # 'url': '/web/content/sale.order/%s/wu_sale_order_v1.commitment_letter/commitment_letter.pdf?download=true' %res_id,
        # }

        # self.env['show.commit.wizard'].create({
        #   'export_file':self.export_file,
        #   'export_file_create_date':self.export_file_create_date
        #   })

class SaleOrderv2(models.Model):
    _inherit = 'purchase.order.line'

    nrs_qty_received_fixed = fields.Boolean()