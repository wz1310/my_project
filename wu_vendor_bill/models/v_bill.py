# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError,RedirectWarning,AccessError
from datetime import timedelta
import re
import datetime,json

import logging,base64
_logger = logging.getLogger(__name__)

class inherit_vbill(models.Model):
    _inherit = 'account.move'

    date_of_pay = fields.Text(compute='find_date')
    voucher = fields.Char(string="Voucher",compute='find_vcr')
    types = fields.Char(string="Type",compute='find_vcr')

    def find_date(self):
        for x in self:
            x_data = []
            if 'title' in x.invoice_payments_widget:
                n_data = json.loads(x.invoice_payments_widget).get('content')
                for y in n_data:
                    x_data.append((datetime.datetime.strptime(str(y['date']), "%Y-%m-%d").date()).strftime("%d-%m-%Y"))
            x.date_of_pay = ', '.join(x_data) if x_data else False

    def find_vcr(self):
        for x in self:
            x.voucher = False
            x.types = False
            tp = False
            find = x.env['account.bank.statement.line'].sudo().search([('move_name','=',x.name)])
            if find.type == 'out':
                tp = 'Out'
            if find.type == 'in':
                tp = 'In'
            x.voucher = find.voucher
            x.types = tp