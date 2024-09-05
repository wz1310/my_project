# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)
import base64
from datetime import date
from io import BytesIO
from calendar import monthrange
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import format_date
try:
	from odoo.tools.misc import xlsxwriter
except ImportError:
	import xlsxwriter

class WizardAgedReport(models.TransientModel):
	_name = 'wizard.aged.report'
	_description = 'Wizard Aged Report'

	date = fields.Date(string='Start Date', required=True)
	company_id = fields.Many2one('res.company',string='Company', default=lambda self: self.env.company)
	data_file = fields.Binary(string="File", readonly=True)
	customer_ids = fields.Many2many('res.partner', string="Customer")
	name = fields.Char(string="Filename", readonly=True)
	
	def button_print(self):
		data = self._get_data_sale()
		if not data :
			raise ValidationError(_("Data Tidak ditemukan, Silahkan coba dengan Filter lainnya"))
		return self.generate_excel(data)

	def _get_data_sale(self):
		customer_filter = ""
		if self.customer_ids:
			if len(self.customer_ids) == 1:
				data_tuple = "(%s)" % self.customer_ids.id
			else:
				data_tuple = tuple(self.customer_ids.ids)
			customer_filter = ("AND so.partner_id IN %s") % (str(data_tuple))
		res = self._get_lines()
		return res

	def generate_excel(self,data):
		""" Generate excel based from sale.order record. """
		fp = BytesIO()
		workbook = xlsxwriter.Workbook(fp)
		worksheet = workbook.add_worksheet()
		
		# ========== Format ==============
		header_table = workbook.add_format({'bold':True,'valign':'vcenter','align':'center','text_wrap':True})
		header_table.set_font_size(12)
		header_table.set_font_name('Times New Roman')
		header_partner_table = workbook.add_format({'bold':True,'valign':'vcenter','align':'left','text_wrap':True})
		header_partner_table.set_font_size(10)
		header_partner_table.set_font_name('Times New Roman')

		body_table = workbook.add_format()
		body_table.set_align('left')
		body_table.set_align('vcenter')
		body_table.set_font_size(10)
		body_table.set_font_name('Times New Roman')

		body_right_table = workbook.add_format()
		body_right_table.set_align('right')
		body_right_table.set_align('vcenter')
		body_right_table.set_font_size(10)
		body_right_table.set_font_name('Times New Roman')
		body_right_table.set_num_format('#,##0.00')

		header_right_table = workbook.add_format({'bold':True,'valign':'vcenter','align':'center','text_wrap':True})
		header_right_table.set_align('right')
		header_right_table.set_align('vcenter')
		header_right_table.set_font_size(12)
		header_right_table.set_font_name('Times New Roman')
		header_right_table.set_num_format('#,##0.00')

		# ========== Header ==============
		worksheet.merge_range('A2:H2',self.company_id.name,header_table)
		worksheet.merge_range('A3:H3','Laporan Aged Receivable ',header_table)
		worksheet.merge_range('A4:H4','Per Tanggal %s'%(self.date.strftime("%d %b %Y")),header_table)

		# worksheet.merge_range('B6:G6', 'No. Pesanan',header_table)
		# worksheet.write('C7', 'Tgl Pesan',header_table)
		# worksheet.merge_range('E7:G7', 'Deskripsi Barang',header_table)
		# worksheet.write('I7', 'Qty. Pesan',header_table)
		# worksheet.write('K7', 'Harga Satuan',header_table)
		# worksheet.write('M7', 'Total Qty. Diterima',header_table)
		# worksheet.write('O7', 'Saldo Qty.',header_table)
		# worksheet.merge_range('Q7:R7', 'Status Pesanan',header_table)

# No barang	NO PO	NO SJ customer	Tanggal SJ	Desk Barang	Nama Pembeli	Kts	Satuan	Harga satuan	Jml Valas	Mata uang	Biaya rata2

		row = 6
		worksheet.write(row,0, 'Customer', header_table)
		worksheet.write(row,1, 'Source', header_table)
		worksheet.write(row,2, 'Due Date', header_table)
		worksheet.write(row,3, 'Journal', header_table)
		worksheet.write(row,4, 'Account', header_table)		
		worksheet.write(row,5, 'Exp. Date', header_table)
		worksheet.write(row,6, 'As of: %s'%(self.date.strftime("%d %b %Y")), header_table)
		worksheet.write(row,7, '1-30', header_table)
		worksheet.write(row,8, '31-60', header_table)
		worksheet.write(row,9, '61-90', header_table)
		worksheet.write(row,10, '91-120', header_table)
		worksheet.write(row,11, 'Older', header_table)
		
		
		row = 7
		for rec in data:		
			worksheet.write(row, 0, (rec.get('partner_id')),body_table)
			worksheet.write(row, 1, (rec.get('source')),body_table)
			worksheet.write(row, 2, (rec.get('due_date')),body_table)
			worksheet.write(row, 3, rec.get('journal') ,body_table)
			worksheet.write(row, 4, (rec.get('account')),body_table)
			worksheet.write(row, 5, (rec.get('exp_date') or rec.get('no_sj_wim')),body_table)
			worksheet.write(row, 6, (rec.get('direction')),body_table)		
			worksheet.write(row, 7, (rec.get('5') or '0'),body_right_table)
			worksheet.write(row, 8, (rec.get('4')),body_table)
			worksheet.write(row, 9, (rec.get('3')),body_table)	
			worksheet.write(row, 10, (rec.get('2')),body_table)	
			worksheet.write(row, 11, (rec.get('1')),body_table)	
			
			


			row = row + 1
		
	
		workbook.close()
		out = base64.b64encode(fp.getvalue())
		fp.close()
		filename = ('Laporan Aged Receivable.xlsx')
		return self.set_data_excel(out, filename)

	def set_data_excel(self, out, filename):
		""" Update data_file and name based from previous process output. And return action url for download excel. """
		self.write({'data_file': out, 'name': filename})

		return {
			'type':
			'ir.actions.act_url',
			'name':
			filename,
			'url':'/web/content?model=wizard.aged.report&field=data_file&filename_field=name&id=%s&download=true&filename=%s' % (self.id, filename,),
			'target': 'self'
		}

	def _get_lines(self):
		sign = -1.0 if self.env.context.get('aged_balance') else 1.0
		lines = []
		account_types = ['receivable']
		context = {'include_nullified_amount': True}
		data_pars = []
		results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(**context)._get_partner_move_lines(account_types, self.date, 'posted', 30)

		for values in results:
			for line in amls[values['partner_id']]:
				# print("-------------",line)
				aml = line['line']
				if aml.move_id.is_purchase_document():
				    caret_type = 'account.invoice.in'
				elif aml.move_id.is_sale_document():
				    caret_type = 'account.invoice.out'
				elif aml.payment_id:
				    caret_type = 'account.payment'
				else:
				    caret_type = 'account.move'

				line_date = aml.date_maturity or aml.date
				if not self._context.get('no_format'):
				    line_date = format_date(self.env, line_date)
				vals = {
						'period':line['period'],
						'due_date':[v for v in [format_date(self.env, aml.date_maturity or aml.date)]][0],
						'partner_id':values['name'],
						'source':aml.move_id.name,
						'journal':aml.journal_id.code,
						'account':aml.account_id.display_name,
						'exp_date':format_date(self.env, aml.expected_pay_date),
						'direction':line['amount'] if line['period'] == 6 else 0,
						'5':line['amount'] if line['period'] == 5 else 0,
						'4':line['amount'] if line['period'] == 4 else 0,
						'3':line['amount'] if line['period'] == 3 else 0,
						'2':line['amount'] if line['period'] == 2 else 0,
						'1':line['amount'] if line['period'] == 1 else 0,
						'0':line['amount'] if line['period'] == 0 else 0,
						}
				data_pars.append(vals)
		return data_pars

	def format_value(self, amount, currency=False, blank_if_zero=False):
	    currency_id = currency or self.env.company.currency_id
	    if currency_id.is_zero(amount):
	        if blank_if_zero:
	            return ''
	        # don't print -0.0 in reports
	        amount = abs(amount)

	    if self.env.context.get('no_format'):
	        return amount
	    return formatLang(self.env, amount, currency_obj=currency_id)