import datetime
import json
import requests
import base64
import re

from odoo import http
from odoo.http import request, JsonRequest, Response
from odoo.exceptions import AccessError, AccessDenied
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,date_utils
from datetime import datetime,timedelta
from odoo import models, fields, api, SUPERUSER_ID, _

def alternative_json_response(self, result=None, error=None):
    if error is not None:
        response = error
    if result is not None:
        response = result
    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)
    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
         headers=[('Content-Type', mime), ('Content-Length', len(body))]
         )

class PrdAPI(http.Controller):

    @http.route("/api/check_prd", type="json",auth='none', methods=["POST"], csrf=False)
    def check_prd(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        pd_key = payload.get("key")
        if pd_key == "@1QWPQv/{5ky#0VF#m%:(ih9.":
            query ="""SELECT name,default_code FROM product_template
            WHERE create_date::DATE BETWEEN (CURRENT_DATE - INTERVAL '1 day')::date and CURRENT_DATE
            AND active = 't'"""
            # request.env.cr.execute(query,(before_date,till_date,'%SURABAYA',before_date,till_date,))
            request.env.cr.execute(query,())
            result  = request.env.cr.dictfetchall()
            if result:
                respond={'status_code':'00','data': result}
            else:
                respond={'status_code':'00','data': "Data tidak ditemukan"}
        else:
            respond={'status_code':'-99','status_message': "Key salah"}
        return respond

class CustAPI(http.Controller):

    @http.route("/api/check_customer", type="json",auth='none', methods=["POST"], csrf=False)
    def check_cst(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        pd_key = payload.get("key")
        if pd_key == "@1QWPQv/{5ky#0VF#m%:(ih9.":
            query ="""SELECT * FROM res_partner
            WHERE create_date::DATE BETWEEN (CURRENT_DATE - INTERVAL '1 day')::date and CURRENT_DATE
            AND active = 't'"""
            # request.env.cr.execute(query,(before_date,till_date,'%SURABAYA',before_date,till_date,))
            request.env.cr.execute(query,())
            result  = request.env.cr.dictfetchall()
            if result:
                respond={'status_code':'00','data': result}
            else:
                respond={'status_code':'00','data': "Data tidak ditemukan"}
        else:
            respond={'status_code':'-99','status_message': "Key salah"}
        return respond

class NewApiPr(http.Controller):

    @http.route("/api/cr_journal", type="json",auth='none', methods=["POST"], csrf=False)
    def cr_jr(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        pd_data = (payload.get("ref"),payload.get("warehouse_id"),payload.get("company_id"))
        validates = all([pd_data])
        inv_line = []
        cr_jr = False
        if len(payload['inv_line'])>0:
            for x in payload['inv_line']:
                inv_line.append(x)
        # print("INVOICE LINE", inv_line)
        if payload and validates:
            try:
                cr_jr = request.env['account.move'].sudo().create({
                    'ref': payload['ref'],
                    'warehouse_id': payload['warehouse_id'],
                    'journal_id': payload['journal_id'],
                    'company_id': payload['company_id'],
                    'date': datetime.strptime(str(payload['date']), "%d/%m/%Y").date(),
                    'line_ids':[(0, 0, line) for line in inv_line],
                    # 'line_ids': [(0,0,
                    #     {
                    #     'account_id': 457,
                    #     'name': 'BAYAR PERDIM',
                    #     'debit': 1000,
                    #     'voucher': 'PERDIM-001'
                    #     }),
                    #     (0,0,{
                    #     'account_id': 2,
                    #     'name': 'BAYAR PERDIM',
                    #     'credit': 1000,
                    #     'voucher': 'PERDIM-001'
                    #     })]
                    })
                a = 0
                for x in cr_jr.line_ids:
                    x.voucher = [y['voucher'] for y in inv_line][a]
                    a = a+1
                if cr_jr:
                    cr_jr.with_context(force_company=payload['company_id']).sudo().action_post()
                    response={'status_code': '00','status_message': 'success'}
                else:
                    response={'status_code': '-99','status_message': 'no data'}
                return response
            except Exception as error:
                if 'Ids:' in str(error):
                    abc = re.findall(r'\d+',str(error))
                    if abc[0]:
                        request.env['account.move'].search([('id','=',abc[0])]).sudo().unlink()
                response={'status_code': '-99','status_message': error}
                return response

    @http.route("/api/get_voucher", type="json",auth='none', methods=["POST"], csrf=False)
    def get_voucher(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        pd_data = (payload.get("id"),payload.get("tgl_statement"),payload.get("journal_id"))
        validates = all([pd_data])
        voucher = []
        v_sort = None
        if payload and validates:
            s_statement = request.env['account.bank.statement'].sudo().search([('journal_id','=',payload['journal_id']),('date','=',datetime.strptime(str(payload['tgl_statement']), "%d/%m/%Y").date()),('company_id','=',payload['company_id'])])
            for x in s_statement.line_ids:
                voucher.append(x.voucher)
            v_sort = sorted(voucher)
            if len(voucher)>0:
                response={'status_code': '00','status_message': 'success','data':v_sort}
            else:
                response={'status_code': '-99','status_message': 'no data','data':v_sort}
            return response

    @http.route("/api/reconcile", type="json",auth='none', methods=["POST"], csrf=False)
    def create_recon(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        pd_data = (payload.get("data"))
        validates = all([pd_data])
        datax = []
        s_statement = request.env['account.bank.statement'].sudo().search([('journal_id','=',payload['journal_id']),('date','=',datetime.strptime(str(payload['tgl_statement']), "%d/%m/%Y").date()),('company_id','=',payload['company_id'])])
        if not s_statement:
            response={'status_code': '-99','status_message': 'Bank statement belum terdaftar di Odoo '}
            return response            
        cr_line = request.env['account.bank.statement.line'].sudo().create({
            'statement_id':s_statement.id,
            'type':payload['type'],
            'date':datetime.strptime(str(payload['tgl_statement']), "%d/%m/%Y").date(),
            'voucher':payload['voucher'],
            'name':payload['name'],
            'amount':payload['amount'],
            'warehouse_id':payload['warehouse'],
            'ref':payload['ref']
            })
        if payload and validates:
            if cr_line.id:
                for x in payload['data']:
                    x['analytic_tag_ids'] = [[6, None, []]]
                    datax.append(x)
                new = request.env['account.move.line']
                action = request.env['account.bank.statement.line'].sudo().search([('id','=',cr_line.id)])
                action.process_reconciliation([], new , datax)
                response={'status_code': '00','status_message': 'success'}
                return response

    @http.route("/api/status_do", type="json",auth='none', methods=["POST"], csrf=False)
    def set_status_do(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        p_state, p_name , company_id , receive_date = (payload.get("status"),payload.get("name"),payload.get("company_id"),payload.get("receive_date"))
        validates = all([p_state, p_name, company_id,receive_date])
        entries = False
        if payload and validates:
            find_do = request.env['stock.picking'].with_context(force_company=payload['company_id']).sudo().search([('name','=',payload['name']),('company_id','=',payload['company_id'])])
            if find_do:
                if payload['type'] == 'ex':
                    find_do.schedule_wa_api_delivered_ex(
                        find_do.name,
                        payload['receive_date'],
                        find_do.partner_id.phone,
                        payload['no_resi'],
                        payload['binary'],
                        payload['penerima'],
                        payload['ekspedisi']
                        )
                    respond={'status_code':00,'status_msg':"Nomor DO ditemukan ..", 'id':find_do.id}
                elif payload['type'] == 'rev_in':
                    find_do.schedule_wa_api_delivered_rev_in(
                        find_do.name,
                        payload['receive_date'],
                        find_do.partner_id.phone,
                        payload['no_resi'],
                        payload['penerima'],
                        payload['ekspedisi'])
                    respond={'status_code':00,'status_msg':"Nomor DO ditemukan ..", 'id':find_do.id}
                elif payload['type'] == 'in':
                    find_do.schedule_wa_api_delivered_in(
                        find_do.name,
                        payload['receive_date'],
                        find_do.partner_id.phone,
                        payload['no_resi'],
                        payload['penerima'],
                        payload['ekspedisi'])
                    respond={'status_code':00,'status_msg':"Nomor DO ditemukan ..", 'id':find_do.id}
                elif payload['type'] == 'rev_ex':
                    find_do.schedule_wa_api_delivered_rev_ex(
                        find_do.name,
                        payload['receive_date'],
                        find_do.partner_id.phone,
                        payload['no_resi'],
                        payload['binary'],
                        payload['penerima'],
                        payload['ekspedisi']
                        )
                    respond={'status_code':00,'status_msg':"Nomor DO ditemukan ..", 'id':find_do.id}
                respond = respond
            else:
                respond={'status_code':-99,'status_msg':"Nomor DO tidak ditemukan .."}
        elif not validates:
            respond={'status_code':-99,'status_msg':'Mandatory tidak boleh kosong!'}
        return respond

class DOApiPr(http.Controller):

    @http.route("/api/check_do", type="json",auth='none', methods=["POST"], csrf=False)
    def check_do(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        hit_date = (payload.get("date"))
        validates = all([hit_date])
        entries = False
        before_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date()-timedelta(days=1)).strftime("%Y-%m-%d")
        till_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date().strftime("%Y-%m-%d"))
        if payload and validates:
            query ="""WITH cek_do AS (SELECT sp.date_done::DATE,sp.name AS "no_do",sp.origin,rp.name AS "customer",sw.name AS nama_warehouse,sw.id AS id_warehouse, sp.titip AS titipan
            FROM stock_picking sp
            LEFT JOIN res_partner rp ON rp.id = sp.partner_id
            LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            LEFT JOIN sale_order so ON so.id = sp.sale_id
            LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
            WHERE sp.date_done::DATE BETWEEN %s AND %s
            AND spt.code = 'outgoing'
            AND sp.state = 'done'
            AND sp.name NOT SIMILAR TO %s
            UNION
            SELECT sjm.date_done::DATE,sjm.name AS "no_do",so.name,rp.name AS "customer",sw.name AS
            nama_warehouse,sw.id AS id_warehouse, NULL AS titipan
            FROM sj_manual sjm
            LEFT JOIN res_partner rp ON rp.id = sjm.partner_id
            LEFT JOIN stock_warehouse sw ON sw.id = sjm.warehouse_id
            LEFT JOIN sale_order so ON so.no_sj_manual = sjm.id
            WHERE sjm.date_done::DATE BETWEEN %s AND %s
            AND sjm.state in ('approved','done'))
            SELECT * FROM cek_do"""
            # request.env.cr.execute(query,(before_date,till_date,'%SURABAYA',before_date,till_date,))
            request.env.cr.execute(query,(before_date,till_date,'%KVS%|%TNS%',before_date,till_date,))
            result  = request.env.cr.dictfetchall()
            for x in result:
                cv_date = str(datetime.strftime(x["date_done"], "%d-%m-%Y"))
                x['date_done'] = cv_date
            if result:
                respond={'status_code':'00','data': result}
            else:
                respond={'status_code':-99,'status_msg':"Data tidak ada ..."}
        elif not validates:
            respond={'status_code':'-99','status_msg':'Mandatory tidak boleh kosong!'}
        return respond

    @http.route("/api/check_do_cancel", type="json",auth='none', methods=["POST"], csrf=False)
    def check_do_cancel(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        hit_date = (payload.get("date"))
        validates = all([hit_date])
        entries = False
        before_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date()-timedelta(days=1)).strftime("%Y-%m-%d")
        till_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date().strftime("%Y-%m-%d"))
        if payload and validates:
            query ="""
            SELECT no_do FROM (
            SELECT no_do,
            (SELECT sum(qty_done) FROM stock_move_line WHERE picking_id in (
            (SELECT id FROM stock_picking WHERE name = no_do))) AS qty_do,
            (SELECT sum(qty_done) FROM stock_move_line WHERE picking_id in (
            (SELECT id FROM stock_picking WHERE origin = CONCAT('Return of',' ',no_do)))) AS qty_retur
            FROM(
            SELECT sp.name AS "no_do"
            FROM stock_picking sp
            LEFT JOIN res_partner rp ON rp.id = sp.partner_id
            LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            LEFT JOIN sale_order so ON so.id = sp.sale_id
            LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
            WHERE sp.date_done::DATE BETWEEN %s AND %s
            AND spt.code = 'outgoing'
            AND sp.state = 'done'
            AND sp.name NOT SIMILAR TO %s
            UNION
            SELECT sjm.name AS "no_do"
            FROM sj_manual sjm
            LEFT JOIN res_partner rp ON rp.id = sjm.partner_id
            LEFT JOIN stock_warehouse sw ON sw.id = sjm.warehouse_id
            LEFT JOIN sale_order so ON so.no_sj_manual = sjm.id
            WHERE sjm.date_done::DATE BETWEEN %s AND %s
            AND sjm.state in ('approved','done')) AS "do_cancel")AS "result" 
            WHERE qty_do = qty_retur
            """
            # request.env.cr.execute(query,(before_date,till_date,'%SURABAYA',before_date,till_date,))
            request.env.cr.execute(query,(before_date,till_date,'%KVS%|%TNS%',before_date,till_date,))
            result  = request.env.cr.dictfetchall()
            if result:
                respond={'status_code':'00','data': result}
            else:
                respond={'status_code':-99,'status_msg':"Data tidak ada ..."}
        elif not validates:
            respond={'status_code':'-99','status_msg':'Mandatory tidak boleh kosong!'}
        return respond

class ReturApiPr(http.Controller):

    @http.route("/api/check_retur", type="json",auth='none', methods=["POST"], csrf=False)
    def check_retur(self, **payload):
        
        request._json_response = alternative_json_response.__get__(request, JsonRequest)
        db_name = request.env['ir.config_parameter'].sudo().search([('key','=','api_db_name')])
        usr_login = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_name')])
        usr_pass = request.env['ir.config_parameter'].sudo().search([('key','=','api_login_pass')])
        db=db_name.value
        login=usr_login.value
        password=usr_pass.value
        request.session.authenticate(db,login,password)
        payload = json.loads(request.httprequest.data)
        hit_date = (payload.get("date"))
        validates = all([hit_date])
        entries = False
        before_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date()-timedelta(days=1)).strftime("%Y-%m-%d")
        till_date = (datetime.strptime(str(payload['date']), "%d/%m/%Y").date().strftime("%Y-%m-%d"))
        if payload and validates:
            query ="""WITH cek_retur AS (SELECT pg.name AS no_so,sp.date_done::DATE,sp.name AS "no_do",sp.origin,sw.name AS nama_warehouse,rp.name AS "customer"
            FROM stock_picking sp
            LEFT JOIN res_partner rp ON rp.id = sp.partner_id
            LEFT JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            LEFT JOIN sale_order so ON so.id = sp.sale_id
            LEFT JOIN stock_warehouse sw ON sw.id = so.warehouse_id
            LEFT JOIN procurement_group pg ON pg.id = sp.group_id
            WHERE sp.date_done::DATE BETWEEN %s AND %s
            AND sp.origin ILIKE %s
            AND spt.code = 'incoming'
            AND sp.batal = 't'
            AND sp.state = 'done')
            SELECT * FROM cek_retur"""
            request.env.cr.execute(query,(before_date,till_date,'%Return of DO%',))
            result  = request.env.cr.dictfetchall()
            for x in result:
                cv_date = str(datetime.strftime(x["date_done"], "%d-%m-%Y"))
                x['date_done'] = cv_date
            if result:
                respond={'status_code':'00','data': result}
            else:
                respond={'status_code':-99,'status_msg':"Data tidak ada ..."}
        elif not validates:
            respond={'status_code':'-99','status_msg':'Mandatory tidak boleh kosong!'}
        return respond
        
class WuInheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            is_return = False
            print("pick.origin : ", pick.origin)
            if(pick.origin == False):
                is_return = True
                print("Found")
            else:       
                if pick.origin and "Return of" in pick.origin:
                    is_return = True
                    print("Found")
                elif pick.origin and "Retur dari" in pick.origin:
                    is_return = True
                    print("Found")  
                elif pick.origin and pick.invisible_update_do == True:
                    is_return = True
                    print("Found")  
                else:
                    is_return = False
                    print("not found")

            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'description_picking': ops.description_picking,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                    'restrict_partner_id': pick.owner_id.id,
                                                    'company_id': pick.company_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now()})
        self._send_confirmation_email()

        if self.sale_id:
            if self.env.context.get('cancel_backorder') == None or self.env.context.get('cancel_backorder') == True:
                # print("NO BACKORDER BRO ATAU VALIDATE BIASA")
                if is_return == False :
                    moves = self.sale_id._create_invoices(final=True)
                    moves.write({'do_names':self.name})
                    for move in moves:
                        # print("CREATE DATE : ", str(move.create_date))
                        dt = datetime.today().date()
                        nrs_data = {}
                        nrs_data['purchase_efaktur_date'] = dt
                        nrs_data['masa_pajak'] = str(dt.month)
                        nrs_data['tahun_pajak'] = str(dt.year)
                        nrs_data['nrs_installment'] = self.sale_id.nrs_installment
                        move.write(nrs_data)
                        move.action_post()
                    moves.schedule_wa_api_tagihan(moves.partner_id.phone,moves.partner_id.name,moves.name,moves.amount_total,moves.invoice_date_due,moves.id)
            # print("ACTION DONE : ", self.env.context.get('cancel_backorder'))
            # print("Name Reference : ", self.name)
            # print("Sale ID : ", self.sale_id)
        return True

        # ===============================================================================================

    def schedule_wa_api_delivered_ex(self,do_name=None,date_do=None,hp_do=None,no_resi=None,binary=None,penerima=None,ekspedisi=None):
        my_date = datetime.combine((datetime.strptime(date_do, '%d/%m/%Y')), datetime.min.time())
        sca = self.env['ir.cron'].sudo().create({
            'name':'SEND WA DELIVERED DO EX %s'%do_name,
            'model_id':315,
            'user_id':1,
            'interval_number':1,
            'interval_type':'minutes',
            'numbercall':1,
            'priority':5,
            'state':'code',
            'nextcall':fields.Datetime.now()-timedelta(hours=7)+timedelta(minutes=60),
            # 'nextcall':my_date-timedelta(hours=7)+timedelta(days=1,hours=8,minutes=25),
            'doall':True
            })
        tokenx = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        datax = {
        'id':sca.id,
        'hp_do':hp_do,
        'token':tokenx,
        'do_name':do_name,
        'no_resi':no_resi,
        'date_do':date_do,
        'binary':binary,
        'penerima':penerima,
        'ekspedisi':ekspedisi,
        }
        sca.sudo().write({'code':'model.post_wa_api_delivered_ex(%s)'%(datax)})


    def post_wa_api_delivered_ex(self,datax=None):
        if datax:
            response = self.image_api(datax['binary'],datax['do_name'][15:],datax['do_name'],datax['hp_do'],datax['date_do'],datax['penerima'],datax['ekspedisi'])
            if response:
                stat_respon = json.loads(response.text)
                if 'success' in stat_respon['status']:
                    print("OK TERKIRIM >>>>>>>>>>>>",stat_respon)
                else:
                    print("MAAF TIDAK TERKIRIM >>>>>>>>>>>>>>>>>>")
                    self.del_post_wa_api_delivered_ex()
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED DO EX %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'date_do':datax['date_do'],
                    'no_resi':datax['no_resi'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi'],
                    'binary':datax['binary'],
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_ex(%s)'%(datay)})
            elif not response:
                self.del_post_wa_api_delivered_ex()
                print("BIKIN ULANG CRON",response)
                task_overdue = self.env['ir.cron'].sudo().search([('name','like',datax['do_name'])])
                if len([x.id for x in task_overdue]) < 6:
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED DO EX %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'date_do':datax['date_do'],
                    'no_resi':datax['no_resi'],
                    'binary':datax['binary'],
                    'ekspedisi':datax['ekspedisi'],
                    'penerima':datax['penerima']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_ex(%s)'%(datay)})
                else:
                    for x in task_overdue:
                        x.sudo().unlink()

    def image_api(self,binary=None,do_name=None,do_full=None,hp_do=None,date_do=None,penerima=None,ekspedisi=None):
        nom_hp = self.env['stock.picking'].sudo().search([('name','=',do_full)]).partner_id.phone
        so_name = self.env['stock.picking'].sudo().search([('name','=',do_full)]).origin
        all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        url_upload_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_upload_image')]).value
        wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian_img')]).value
        channel_id = self.env['ir.config_parameter'].sudo().search([('key','=','channel_id')]).value
        url = url_upload_image
        path = self.env['ir.config_parameter'].sudo().search([('key','=','path_image_wa')]).value
        completeName = path%do_name
        image_64_decode = base64.b64decode(binary)
        file1 = open(completeName , "wb")
        file1.write(image_64_decode)
        file1.close()
        url_u = url_upload_image
        payload = {}
        files=[('file',('abc.jpg',open(completeName,'rb'),'image/jpeg'))]
        headers = {
        'Authorization': 'Bearer '+wa_token
        }
        responses = requests.request("POST", url_u,headers=headers, data=payload,files=files)
        datas = json.loads(responses.text)
        img_id = datas['data']['url']
        print("URL IMG", img_id)
        if img_id:
            print("IMAGEEE ADAAAAAAAAAAAA",img_id)
            url = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_image')]).value
            payload = json.dumps({
                "to_name": all_do.partner_id.name,
                "to_number": nom_hp,
                "message_template_id":tmp_msg,
                "channel_integration_id":channel_id,
                "language": {"code": "id"},
                "parameters": {"header": {
                "format": "IMAGE",
                "params": [{
                    "key": "url",
                    "value":img_id
                    },
                    {
                    "key": "filename",
                    "value":"02707sss.jpg"
                    }
                    ]
                    },
                "body": [{
                    "key": "1",
                    "value_text":all_do.partner_id.name,
                    "value": "aa"
                    },
                    {
                    "key": "2",
                    "value_text":date_do,
                    "value": "bb"
                    },
                    {
                    "key": "3",
                    "value_text":', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing' and x.state == 'done')]),
                    "value": "cc"
                    },
                    # {
                    # "key": "4",
                    # "value_text":penerima,
                    # "value": "dd"
                    # },
                    {
                    "key": "4",
                    "value_text":ekspedisi,
                    "value": "ee"
                    },
                    {
                    "key": "5",
                    "value_text":str("{:,.2f}".format(float(all_do.amount_total))),
                    "value": "ff"
                    }]}})
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+wa_token
                }
            response = requests.request("POST", url,headers=headers, data=payload)
            print(response)
            return response

        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

        # //////////////////////////////////old funct/////////////////////////////////
        # so_name = self.env['stock.picking'].sudo().search([('name','=',do_full)]).origin
        # all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        # text1 = """Dear *"""+all_do.partner_id.name+"""*\nTerimakasih atas pesanannya di *WUJUD UNGGUL*\nBarang pesanan Anda sudah dikirim pada tanggal *"""+date_do+"""* dengan nomor order """+'*'+', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing')])+'*'+""", dan yang menerima adalah *"""+penerima+"""* pengirim an. *""" + ekspedisi+"""* """
        # text2 = """, dengan nominal transaksi sebesar *Rp."""+str("{:,.2f}".format(float(all_do.amount_total)))+"""*"""
        # text3 = """\nMohon pastikan barang pesanan anda sudah sesuai & transaksi dinyatakan sah dengan adanya TTD invoice."""
        # text4 = """\nPertanyaan lebih lanjut dapat menghubungi nomor Customer Care kami :"""
        # text5 = """\nHotline :  0807 1 337799 (office hour)"""
        # text6 = """\nWA CS  :  082143123173 (office hour)"""
        # text7 = """\n\nHormat Kami,"""
        # text8 = """\nCV Wujud Unggul"""
        # text9 = """\n*Pesan ini dikirim secara otomatis melalui sistem ERP wujud unggul dan mohon tidak membalas pesan ini*"""
        # full_text = text1+text2+text3+text4+text5+text6+text7+text8+text9
        # url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        # url = url_send_text
        # payload = json.dumps({
        #     "nohp": hp_do,
        #     "pesan": full_text,
        #     "token": wa_token,
        #     "binary": binary
        #     })
        # headers = {
        # 'Content-Type': 'application/json'
        # }
        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

        # url_upload_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_upload_image')]).value
        # url_send_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_image')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        # path = self.env['ir.config_parameter'].sudo().search([('key','=','path_image_wa')]).value
        # completeName = path%do_name
        # image_64_decode = base64.b64decode(binary)
        # file1 = open(completeName , "wb")
        # file1.write(image_64_decode)
        # file1.close()
        # url_u = url_upload_image
        # payload = {}
        # files=[('file',('abc.jpg',open(completeName,'rb'),'image/jpeg'))]
        # headers = {'x-access-token':wa_token}
        # responses = requests.request("POST", url_u,headers=headers, data=payload,files=files)
        # datas = json.loads(responses.text)
        # img_id = datas['id_message_file']

        # url_s = url_send_image
        # payload = json.dumps({
        #     "destination": hp_do,
        #     "message": tmp_msg,
        #     "id_message_file":img_id})
        # headers = {
        # 'Accept': '*/*',
        # 'Accept-Language': 'en-GB,en;q=0.9,id-ID;q=0.8,id;q=0.7,en-US;q=0.6',
        # 'Connection': 'keep-alive',
        # 'x-access-token':wa_token,
        # 'sendMethod': 'direct to request body',
        # 'Content-Type': 'application/json'}
        # response = requests.request("POST", url_s,headers=headers, data=payload)
        # return response

    def del_post_wa_api_delivered_ex(self):
        task = self.env['ir.cron'].sudo().search([('active', '=', False),('name', 'ilike', 'SEND WA DELIVERED DO EX')])
        if task:
            task.sudo().unlink()
        else:
            None

    # ============================================================================================================

    # ============================================================================================================

    def schedule_wa_api_delivered_rev_ex(self,do_name=None,date_do=None,hp_do=None,no_resi=None,binary=None,penerima=None,ekspedisi=None):
        my_date = datetime.combine((datetime.strptime(date_do, '%d/%m/%Y')), datetime.min.time())
        sca = self.env['ir.cron'].sudo().create({
            'name':'SEND WA DELIVERED REV DO EX %s'%do_name,
            'model_id':315,
            'user_id':1,
            'interval_number':1,
            'interval_type':'minutes',
            'numbercall':1,
            'priority':5,
            'state':'code',
            'nextcall':fields.Datetime.now()-timedelta(hours=7)+timedelta(minutes=60),
            # 'nextcall':my_date-timedelta(hours=7)+timedelta(days=1,hours=8,minutes=25),
            'doall':True
            })
        tokenx = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        datax = {
        'id':sca.id,
        'hp_do':hp_do,
        'token':tokenx,
        'do_name':do_name,
        'no_resi':no_resi,
        'date_do':date_do,
        'binary':binary,
        'penerima':penerima,
        'ekspedisi':ekspedisi,
        }
        sca.sudo().write({'code':'model.post_wa_api_delivered_rev_ex(%s)'%(datax)})


    def post_wa_api_delivered_rev_ex(self,datax=None):
        if datax:
            response = self.image_api_rev(datax['binary'],datax['do_name'][15:],datax['do_name'],datax['hp_do'],datax['date_do'],datax['penerima'],datax['ekspedisi'])
            if response:
                stat_respon = json.loads(response.text)
                if 'success' in stat_respon['status']:
                    print("OK TERKIRIM >>>>>>>>>>>>",stat_respon)
                else:
                    print("MAAF TIDAK TERKIRIM >>>>>>>>>>>>>>>>>>")
                    self.del_post_wa_api_delivered_rev_ex()
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED REV DO EX %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'date_do':datax['date_do'],
                    'no_resi':datax['no_resi'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi'],
                    'binary':datax['binary'],
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_rev_ex(%s)'%(datay)})
            elif not response:
                self.del_post_wa_api_delivered_rev_ex()
                print("BIKIN ULANG CRON",response)
                task_overdue = self.env['ir.cron'].sudo().search([('name','like',datax['do_name'])])
                if len([x.id for x in task_overdue]) < 6:
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED REV DO EX %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'date_do':datax['date_do'],
                    'no_resi':datax['no_resi'],
                    'binary':datax['binary'],
                    'ekspedisi':datax['ekspedisi'],
                    'penerima':datax['penerima']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_rev_ex(%s)'%(datay)})
                else:
                    for x in task_overdue:
                        x.sudo().unlink()

    def image_api_rev(self,binary=None,do_name=None,do_full=None,hp_do=None,date_do=None,penerima=None,ekspedisi=None):
        nom_hp = self.env['stock.picking'].sudo().search([('name','=',do_full)]).partner_id.phone
        so_name = self.env['stock.picking'].sudo().search([('name','=',do_full)]).origin
        all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        url_upload_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_upload_image')]).value
        wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian_img_rev')]).value
        channel_id = self.env['ir.config_parameter'].sudo().search([('key','=','channel_id')]).value
        url = url_upload_image
        path = self.env['ir.config_parameter'].sudo().search([('key','=','path_image_wa')]).value
        completeName = path%do_name
        image_64_decode = base64.b64decode(binary)
        file1 = open(completeName , "wb")
        file1.write(image_64_decode)
        file1.close()
        url_u = url_upload_image
        payload = {}
        files=[('file',('abc.jpg',open(completeName,'rb'),'image/jpeg'))]
        headers = {
        'Authorization': 'Bearer '+wa_token
        }
        responses = requests.request("POST", url_u,headers=headers, data=payload,files=files)
        datas = json.loads(responses.text)
        img_id = datas['data']['url']
        print("URL IMG", img_id)
        if img_id:
            print("IMAGEEE ADAAAAAAAAAAAA",img_id)
            url = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_image')]).value
            payload = json.dumps({
                "to_name": all_do.partner_id.name,
                "to_number": nom_hp,
                "message_template_id":tmp_msg,
                "channel_integration_id":channel_id,
                "language": {"code": "id"},
                "parameters": {"header": {
                "format": "IMAGE",
                "params": [{
                    "key": "url",
                    "value":img_id
                    },
                    {
                    "key": "filename",
                    "value":"02707sss.jpg"
                    }
                    ]
                    },
                "body": [{
                    "key": "1",
                    "value_text":all_do.partner_id.name,
                    "value": "aa"
                    },
                    {
                    "key": "2",
                    "value_text":date_do,
                    "value": "bb"
                    },
                    {
                    "key": "3",
                    "value_text":', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing' and x.state == 'done')]),
                    "value": "cc"
                    },
                    # {
                    # "key": "4",
                    # "value_text":penerima,
                    # "value": "dd"
                    # },
                    {
                    "key": "4",
                    "value_text":ekspedisi,
                    "value": "ee"
                    },
                    {
                    "key": "5",
                    "value_text":str("{:,.2f}".format(float(all_do.amount_total))),
                    "value": "ff"
                    }]}})
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+wa_token
                }
            response = requests.request("POST", url,headers=headers, data=payload)
            print(response)
            return response

        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

        # //////////////////////////////////old funct/////////////////////////////////
        # so_name = self.env['stock.picking'].sudo().search([('name','=',do_full)]).origin
        # all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        # text1 = """Dear *"""+all_do.partner_id.name+"""*\nTerimakasih atas pesanannya di *WUJUD UNGGUL*\nBarang pesanan Anda sudah dikirim pada tanggal *"""+date_do+"""* dengan nomor order """+'*'+', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing')])+'*'+""", dan yang menerima adalah *"""+penerima+"""* pengirim an. *""" + ekspedisi+"""* """
        # text2 = """, dengan nominal transaksi sebesar *Rp."""+str("{:,.2f}".format(float(all_do.amount_total)))+"""*"""
        # text3 = """\nMohon pastikan barang pesanan anda sudah sesuai & transaksi dinyatakan sah dengan adanya TTD invoice."""
        # text4 = """\nPertanyaan lebih lanjut dapat menghubungi nomor Customer Care kami :"""
        # text5 = """\nHotline :  0807 1 337799 (office hour)"""
        # text6 = """\nWA CS  :  082143123173 (office hour)"""
        # text7 = """\n\nHormat Kami,"""
        # text8 = """\nCV Wujud Unggul"""
        # text9 = """\n*Pesan ini dikirim secara otomatis melalui sistem ERP wujud unggul dan mohon tidak membalas pesan ini*"""
        # full_text = text1+text2+text3+text4+text5+text6+text7+text8+text9
        # url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        # url = url_send_text
        # payload = json.dumps({
        #     "nohp": hp_do,
        #     "pesan": full_text,
        #     "token": wa_token,
        #     "binary": binary
        #     })
        # headers = {
        # 'Content-Type': 'application/json'
        # }
        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

        # url_upload_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_upload_image')]).value
        # url_send_image = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_image')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        # path = self.env['ir.config_parameter'].sudo().search([('key','=','path_image_wa')]).value
        # completeName = path%do_name
        # image_64_decode = base64.b64decode(binary)
        # file1 = open(completeName , "wb")
        # file1.write(image_64_decode)
        # file1.close()
        # url_u = url_upload_image
        # payload = {}
        # files=[('file',('abc.jpg',open(completeName,'rb'),'image/jpeg'))]
        # headers = {'x-access-token':wa_token}
        # responses = requests.request("POST", url_u,headers=headers, data=payload,files=files)
        # datas = json.loads(responses.text)
        # img_id = datas['id_message_file']

        # url_s = url_send_image
        # payload = json.dumps({
        #     "destination": hp_do,
        #     "message": tmp_msg,
        #     "id_message_file":img_id})
        # headers = {
        # 'Accept': '*/*',
        # 'Accept-Language': 'en-GB,en;q=0.9,id-ID;q=0.8,id;q=0.7,en-US;q=0.6',
        # 'Connection': 'keep-alive',
        # 'x-access-token':wa_token,
        # 'sendMethod': 'direct to request body',
        # 'Content-Type': 'application/json'}
        # response = requests.request("POST", url_s,headers=headers, data=payload)
        # return response

    def del_post_wa_api_delivered_rev_ex(self):
        task = self.env['ir.cron'].sudo().search([('active', '=', False),('name', 'ilike', 'SEND WA DELIVERED REV DO EX')])
        if task:
            task.sudo().unlink()
        else:
            None

    # ============================================================================================================

    def schedule_wa_api_delivered_in(self,do_name=None,date_do=None,hp_do=None,no_resi=None,penerima=None,ekspedisi=None):
        my_date = datetime.combine((datetime.strptime(date_do, '%d/%m/%Y')), datetime.min.time())
        sca = self.env['ir.cron'].sudo().create({
            'name':'SEND WA DELIVERED DO IN %s'%do_name,
            'model_id':315,
            'user_id':1,
            'interval_number':1,
            'interval_type':'minutes',
            'numbercall':1,
            'priority':5,
            'state':'code',
            'nextcall':fields.Datetime.now()-timedelta(hours=7)+timedelta(minutes=60),
            # 'nextcall':my_date-timedelta(hours=7)+timedelta(days=1,hours=8,minutes=25),
            'doall':True
            })
        tokenx = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        datax = {
        'id':sca.id,
        'hp_do':hp_do,
        'token':tokenx,
        'do_name':do_name,
        'no_resi':no_resi,
        'date_do':date_do,
        'penerima':penerima,
        'ekspedisi':ekspedisi}
        sca.sudo().write({'code':'model.post_wa_api_delivered_in(%s)'%(datax)})


    def post_wa_api_delivered_in(self,datax=None):
        print("DATAXXXXXXXXX DATE", datax['date_do'])
        if datax:
            response = self.text_api(datax['do_name'],datax['hp_do'],datax['date_do'],datax['penerima'],datax['ekspedisi'])
            if response:
                stat_respon = json.loads(response.text)
                if 'success' in stat_respon['status']:
                    print("OK TERKIRIM >>>>>>>>>>>>",stat_respon)
                else:
                    print("MAAF TIDAK TERKIRIM >>>>>>>>>>>>>>>>>>")
                    self.del_post_wa_api_delivered_in()
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED DO IN %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'no_resi':datax['no_resi'],
                    'date_do':datax['date_do'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_in(%s)'%(datay)})
            elif not response:
                self.del_post_wa_api_delivered_in()
                task_overdue = self.env['ir.cron'].sudo().search([('name','like',datax['do_name'])])
                if len([x.id for x in task_overdue]) < 6:
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED DO IN %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'no_resi':datax['no_resi'],
                    'date_do':datax['date_do'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_in(%s)'%(datay)})
                else:
                    for x in task_overdue:
                        x.sudo().unlink()

    def text_api(self,do_name=None,hp_do=None,date_do=None,penerima=None,ekspedisi=None):
        nom_hp = self.env['stock.picking'].sudo().search([('name','=',do_name)]).partner_id.phone
        so_name = self.env['stock.picking'].sudo().search([('name','=',do_name)]).origin
        all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        channel_id = self.env['ir.config_parameter'].sudo().search([('key','=','channel_id')]).value
        url = url_send_text
        payload = json.dumps({
            "to_name": all_do.partner_id.name,
            "to_number": nom_hp,
            "message_template_id":tmp_msg,
            "channel_integration_id": channel_id,
            "language": {
            "code": "id"
            },
            "parameters": {
            "body": [
            {
            "key": "1",
            "value_text": all_do.partner_id.name,
            "value": 'aa'
            },
            {
            "key": "2",
            "value_text": date_do,
            "value": 'bb'
            },
            {
            "key": "3",
            "value_text": ', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing' and x.state == 'done')]),
            "value": 'cc'            
            },
            {
            "key": "4",
            "value_text": penerima,
            "value": 'dd'
            },
            {
            "key": "5",
            "value_text": ekspedisi,
            "value": 'ee'
            },
            {
            "key": "6",
            "value_text": str("{:,.2f}".format(float(all_do.amount_total))),
            "value": 'ff'
            }
            ]
            }
            })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+wa_token
        }
        response = requests.request("POST", url,headers=headers, data=payload)
        stat_respon = json.loads(response.text)
        return response

        # //////////////////////////////////old funct/////////////////////////////
        # so_name = self.env['stock.picking'].sudo().search([('name','=',do_name)]).origin
        # all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        # text1 = """Dear *"""+all_do.partner_id.name+"""*\nTerimakasih atas pesanannya di *WUJUD UNGGUL*\nBarang pesanan Anda sudah dikirim pada tanggal *"""+date_do+"""* dengan nomor order """+'*'+', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing')])+'*'+""", dan yang menerima adalah *"""+penerima+"""* pengirim an. *""" + ekspedisi+"""* """
        # text2 = """, dengan nominal transaksi sebesar *Rp."""+str("{:,.2f}".format(float(all_do.amount_total)))+"""*"""
        # text3 = """\nMohon pastikan barang pesanan anda sudah sesuai & transaksi dinyatakan sah dengan adanya TTD invoice."""
        # text4 = """\nPertanyaan lebih lanjut dapat menghubungi nomor Customer Care kami :"""
        # text5 = """\nHotline :  0807 1 337799 (office hour)"""
        # text6 = """\nWA CS  :  082143123173 (office hour)"""
        # text7 = """\n\nHormat Kami,"""
        # text8 = """\nCV Wujud Unggul"""
        # text9 = """\n*Pesan ini dikirim secara otomatis melalui sistem ERP wujud unggul dan mohon tidak membalas pesan ini*"""
        # full_text = text1+text2+text3+text4+text5+text6+text7+text8+text9
        # url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian')]).value
        # url = url_send_text
        # payload = json.dumps({
        #     "nohp": hp_do,
        #     "pesan": full_text,
        #     "token": wa_token
        #     })
        # headers = {
        # 'Content-Type': 'application/json'
        # }
        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

    def del_post_wa_api_delivered_in(self):
        task = self.env['ir.cron'].sudo().search([('active', '=', False),('name', 'ilike', 'SEND WA DELIVERED DO IN')])
        if task:
            task.sudo().unlink()
        else:
            None

    # ============================================================================================================

    def schedule_wa_api_delivered_rev_in(self,do_name=None,date_do=None,hp_do=None,no_resi=None,penerima=None,ekspedisi=None):
        my_date = datetime.combine((datetime.strptime(date_do, '%d/%m/%Y')), datetime.min.time())
        sca = self.env['ir.cron'].sudo().create({
            'name':'SEND WA DELIVERED REV DO IN %s'%do_name,
            'model_id':315,
            'user_id':1,
            'interval_number':1,
            'interval_type':'minutes',
            'numbercall':1,
            'priority':5,
            'state':'code',
            'nextcall':fields.Datetime.now()-timedelta(hours=7)+timedelta(minutes=60),
            # 'nextcall':my_date-timedelta(hours=7)+timedelta(days=1,hours=8,minutes=25),
            'doall':True
            })
        tokenx = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        datax = {
        'id':sca.id,
        'hp_do':hp_do,
        'token':tokenx,
        'do_name':do_name,
        'no_resi':no_resi,
        'date_do':date_do,
        'penerima':penerima,
        'ekspedisi':ekspedisi}
        sca.sudo().write({'code':'model.post_wa_api_delivered_rev_in(%s)'%(datax)})


    def post_wa_api_delivered_rev_in(self,datax=None):
        print("DATAXXXXXXXXX DATE", datax['date_do'])
        if datax:
            response = self.text_api_rev(datax['do_name'],datax['hp_do'],datax['date_do'],datax['penerima'],datax['ekspedisi'])
            if response:
                stat_respon = json.loads(response.text)
                if 'success' in stat_respon['status']:
                    print("OK TERKIRIM >>>>>>>>>>>>",stat_respon)
                else:
                    print("MAAF TIDAK TERKIRIM >>>>>>>>>>>>>>>>>>")
                    self.del_post_wa_api_delivered_rev_in()
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED REV DO IN %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'no_resi':datax['no_resi'],
                    'date_do':datax['date_do'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_in(%s)'%(datay)})
            elif not response:
                self.del_post_wa_api_delivered_rev_in()
                task_overdue = self.env['ir.cron'].sudo().search([('name','like',datax['do_name'])])
                if len([x.id for x in task_overdue]) < 6:
                    date_plus = fields.Datetime.now()+timedelta(minutes=60)
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND WA DELIVERED REV DO IN %s'%datax['do_name'],
                        'model_id':315,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'minutes',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':date_plus-timedelta(hours=7),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'hp_do':datax['hp_do'],
                    'token':datax['token'],
                    'do_name':datax['do_name'],
                    'no_resi':datax['no_resi'],
                    'date_do':datax['date_do'],
                    'penerima':datax['penerima'],
                    'ekspedisi':datax['ekspedisi']
                    }
                    sca.sudo().write({'code':'model.post_wa_api_delivered_rev_in(%s)'%(datay)})
                else:
                    for x in task_overdue:
                        x.sudo().unlink()

    def text_api_rev(self,do_name=None,hp_do=None,date_do=None,penerima=None,ekspedisi=None):
        nom_hp = self.env['stock.picking'].sudo().search([('name','=',do_name)]).partner_id.phone
        so_name = self.env['stock.picking'].sudo().search([('name','=',do_name)]).origin
        all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian_rev_in')]).value
        channel_id = self.env['ir.config_parameter'].sudo().search([('key','=','channel_id')]).value
        url = url_send_text
        payload = json.dumps({
            "to_name": all_do.partner_id.name,
            "to_number": nom_hp,
            "message_template_id":tmp_msg,
            "channel_integration_id": channel_id,
            "language": {
            "code": "id"
            },
            "parameters": {
            "body": [
            {
            "key": "1",
            "value_text": all_do.partner_id.name,
            "value": 'aa'
            },
            {
            "key": "2",
            "value_text": date_do,
            "value": 'bb'
            },
            {
            "key": "3",
            "value_text": ', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing' and x.state == 'done')]),
            "value": 'cc'            
            },
            {
            "key": "4",
            "value_text": penerima,
            "value": 'dd'
            },
            {
            "key": "5",
            "value_text": ekspedisi,
            "value": 'ee'
            },
            {
            "key": "6",
            "value_text": str("{:,.2f}".format(float(all_do.amount_total))),
            "value": 'ff'
            }
            ]
            }
            })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+wa_token
        }
        response = requests.request("POST", url,headers=headers, data=payload)
        stat_respon = json.loads(response.text)
        return response

        # //////////////////////////////////old funct/////////////////////////////
        # so_name = self.env['stock.picking'].sudo().search([('name','=',do_name)]).origin
        # all_do = self.env['sale.order'].sudo().search([('name','=',so_name)])
        # text1 = """Dear *"""+all_do.partner_id.name+"""*\nTerimakasih atas pesanannya di *WUJUD UNGGUL*\nBarang pesanan Anda sudah dikirim pada tanggal *"""+date_do+"""* dengan nomor order """+'*'+', '.join([str(x.name) for x in all_do.picking_ids.filtered(lambda x:x.picking_type_id.code == 'outgoing')])+'*'+""", dan yang menerima adalah *"""+penerima+"""* pengirim an. *""" + ekspedisi+"""* """
        # text2 = """, dengan nominal transaksi sebesar *Rp."""+str("{:,.2f}".format(float(all_do.amount_total)))+"""*"""
        # text3 = """\nMohon pastikan barang pesanan anda sudah sesuai & transaksi dinyatakan sah dengan adanya TTD invoice."""
        # text4 = """\nPertanyaan lebih lanjut dapat menghubungi nomor Customer Care kami :"""
        # text5 = """\nHotline :  0807 1 337799 (office hour)"""
        # text6 = """\nWA CS  :  082143123173 (office hour)"""
        # text7 = """\n\nHormat Kami,"""
        # text8 = """\nCV Wujud Unggul"""
        # text9 = """\n*Pesan ini dikirim secara otomatis melalui sistem ERP wujud unggul dan mohon tidak membalas pesan ini*"""
        # full_text = text1+text2+text3+text4+text5+text6+text7+text8+text9
        # url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        # wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        # tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_pembelian_rev_in')]).value
        # url = url_send_text
        # payload = json.dumps({
        #     "nohp": hp_do,
        #     "pesan": full_text,
        #     "token": wa_token
        #     })
        # headers = {
        # 'Content-Type': 'application/json'
        # }
        # response = requests.request("POST", url,headers=headers, data=payload)
        # return response

    def del_post_wa_api_delivered_rev_in(self):
        task = self.env['ir.cron'].sudo().search([('active', '=', False),('name', 'ilike', 'SEND WA DELIVERED REV DO IN')])
        if task:
            task.sudo().unlink()
        else:
            None

class InhritAccountMove(models.Model):
    _inherit = 'account.move'

    def schedule_wa_api_tagihan(self,no_hp=None,customer=None,nm_inv=None,total=None,due_date=None,id_move=None):
        print("JALANNNN schedule_wa_api_tagihan>>>>>>>>>>>>>>>>>>>>>>>>>>")
        top_tagihan = self.env['ir.config_parameter'].sudo().search([('key','=','top_tagihan %s'
            %self.invoice_payment_term_id.line_ids.filtered(lambda x:x.value=='balance').days)]).value
        if top_tagihan:
            top = top_tagihan.split(',')
            my_date = datetime.combine(due_date, datetime.min.time())
            for x in tuple(top):
                # print("111111111111111111111111",fields.Datetime.now())
                # print("22222222222222222222",my_date-timedelta(days=int(x)))
                sca = self.env['ir.cron'].sudo().create({
                    'name':'SEND TAGIHAN %s'%self.name,
                    'model_id':240,
                    'user_id':1,
                    'interval_number':1,
                    'interval_type':'days',
                    'numbercall':1,
                    'priority':5,
                    'state':'code',
                    'nextcall':my_date-timedelta(days=int(x)),
                    'doall':True
                    })
                print("DUEEEE DATEEEE", due_date)
                datax = {
                'id':sca.id,
                'no_hp':no_hp,
                'customer':customer,
                'nm_inv':nm_inv,
                'total':total,
                'due_date':due_date,
                'nextcall':sca.nextcall,
                'id_move':id_move
                }
                if datetime.strftime(my_date-timedelta(days=int(x)), "%Y-%m-%d") < str(fields.Datetime.now().date()):
                    sca.active = False
                print("SCA",datetime.strftime(my_date-timedelta(days=int(x)), "%Y-%m-%d"),str(fields.Datetime.now().date()))
                sca.write({'code':'model.post_wa_api_tagihan(%s)'%(datax)})


    def post_wa_api_tagihan(self,datax=None):
        state_move = self.env['account.move'].sudo().search([('id','=',datax['id_move'])])
        if datax and state_move.invoice_payment_state != 'paid' and state_move.state != 'cancel':
            response = self.text_api_tagihan(datax['no_hp'],datax['customer'],datax['nm_inv'],datax['total'],datax['due_date'].strftime("%d/%m/%y"),datax['id_move'])
            if response:
                stat_respon = json.loads(response.text)
                if 'success' in stat_respon['status']:
                    print("OK TERKIRIM >>>>>>>>>>>>",stat_respon)
                else:
                    print("MAAF TIDAK TERKIRIM >>>>>>>>>>>>>>>>>>")
                    self.del_post_wa_api_tagihan()
                    sca = self.env['ir.cron'].sudo().create({
                        'name':'SEND TAGIHAN %s'%datax['nm_inv'],
                        'model_id':240,
                        'user_id':1,
                        'interval_number':1,
                        'interval_type':'days',
                        'numbercall':1,
                        'priority':5,
                        'state':'code',
                        'nextcall':datax['nextcall']+timedelta(minutes=5),
                        'doall':True
                        })
                    datay = {
                    'id':sca.id,
                    'no_hp':datax['no_hp'],
                    'customer':datax['customer'],
                    'nm_inv':datax['nm_inv'],
                    'total':datax['total'],
                    'due_date':datax['due_date'],
                    'nextcall':datax['nextcall'],
                    'id_move':id_move
                    }
                    sca.write({'code':'model.post_wa_api_tagihan(%s)'%(datay)})
            elif not response:
                self.del_post_wa_api_tagihan()
                print("BIKIN ULANG CRON",response)
                sca = self.env['ir.cron'].sudo().create({
                    'name':'SEND TAGIHAN %s'%datax['nm_inv'],
                    'model_id':240,
                    'user_id':1,
                    'interval_number':1,
                    'interval_type':'days',
                    'numbercall':1,
                    'priority':5,
                    'state':'code',
                    'nextcall':datax['nextcall']+timedelta(minutes=5),
                    'doall':True
                    })
                datay = {
                    'id':sca.id,
                    'no_hp':datax['no_hp'],
                    'customer':datax['customer'],
                    'nm_inv':datax['nm_inv'],
                    'total':datax['total'],
                    'due_date':datax['due_date'],
                    'nextcall':datax['nextcall'],
                    'id_move':id_move
                    }
                sca.write({'code':'model.post_wa_api_tagihan(%s)'%(datay)})

    def text_api_tagihan(self,no_hp=None,customer=None,nm_inv=None,total=None,due_date=None,id_move=None):
        nom_hp = self.env['account.move'].sudo().search([('id','=',id_move)]).partner_id.phone
        amount_due = self.env['account.move'].sudo().search([('id','=',id_move)]).amount_residual
        url_send_text = self.env['ir.config_parameter'].sudo().search([('key','=','url_send_text')]).value
        wa_token = self.env['ir.config_parameter'].sudo().search([('key','=','wa_token')]).value
        tmp_msg = self.env['ir.config_parameter'].sudo().search([('key','=','template_tagihan')]).value
        channel_id = self.env['ir.config_parameter'].sudo().search([('key','=','channel_id_finance')]).value
        url = url_send_text
        payload = json.dumps({
            "to_name": customer,
            "to_number": nom_hp,
            "message_template_id":tmp_msg,
            "channel_integration_id": channel_id,
            "language": {
            "code": "id"
            },
            "parameters": {
            "body": [
            {
            "key": "1",
            "value_text": customer,
            "value": 'aa'
            },
            {
            "key": "2",
            "value_text": nm_inv,
            "value": 'bb'
            },
            {
            "key": "3",
            "value_text": str("{:,.2f}".format(float(amount_due))),
            "value": 'cc'            
            },
            {
            "key": "4",
            "value_text": due_date,
            "value": 'dd'
            }
            ]
            }
            })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+wa_token
        }
        response = requests.request("POST", url,headers=headers, data=payload)
        stat_respon = json.loads(response.text)
        return response

    def del_post_wa_api_tagihan(self):
        task = self.env['ir.cron'].sudo().search([('active', '=', False),('name', 'ilike', 'SEND TAGIHAN')])
        if task:
            task.sudo().unlink()
        else:
            None