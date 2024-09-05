# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date


class report_account_aged_partner(models.AbstractModel):
    _name = "account.aged.receivable.custom"
    _description = "Aged Receivable Custom"
    _inherit = 'account.report'

    filter_date = {'mode': 'single', 'filter': 'today'}
    filter_unfold_all = False
    filter_partner = True
    order_selected_column = {'default': 0}

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _("Due Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("Journal"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Account"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Exp. Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("As of: %s") % format_date(self.env, options['date']['date_to']), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("1 - 30"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("31 - 60"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("61 - 90"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("91 - 120"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Older"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Total"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
        ]
        return columns

    def _get_templates(self):
        templates = super(report_account_aged_partner, self)._get_templates()
        templates['main_template'] = 'wu_wz_age_receivable_query.template_aged_receivable_custom'
        try:
            self.env['ir.ui.view'].get_view_id('wu_wz_age_receivable_query.template_aged_receivable_custom_line_report')
            templates['line_template'] = 'wu_wz_age_receivable_query.template_aged_receivable_custom_line_report'
        except ValueError:
            pass
        return templates

    @api.model
    def _get_lines(self, options, line_id=None):
        m_comp = None
        coa = None
        partners = None
        if len(options['partner_ids'])>1:
            partners = "AND aml.partner_id in %s"%str(tuple(x for x in options['partner_ids']))
        elif len(options['partner_ids'])==1:
            partners = "AND aml.partner_id = %s"%str(options['partner_ids'][0])
        else:
            partners = "-- AND aml.partner_id = aml.partner_id"
        if len(tuple(self.env.context['allowed_company_ids']))>1:
            m_comp = "aml.company_id in %s" % str(tuple(self.env.context['allowed_company_ids']))
            coa = "aml.account_id in (11,172)"
        else:
            m_comp = "aml.company_id = %s" % str(self.env.company.id)
            if self.env.company.id == 1:
                coa = "aml.account_id = %s" % 11
            else:
                coa = "aml.account_id = %s" % 172
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        context = {'include_nullified_amount': True}
        if line_id and 'partner_' in line_id:
            # we only want to fetch data about this partner because we are expanding a line
            partner_id_str = line_id.split('_')[1]
            partners = "AND aml.partner_id = %s"%str(partner_id_str) if partner_id_str.isnumeric() else "AND aml.partner_id IS NULL"
        # results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(**context)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
        query = """SELECT query.partner_id AS "partner_id",query.name,sum(query."direction")AS "direction",SUM(query."4")AS"4",
        sum(query."3") AS "3",sum(query."2") AS "2",sum(query."1") AS "1",
        sum(query."0") AS "0", SUM("direction"+"4"+"3"+"2"+"1"+"0") AS "total"
        FROM
        (SELECT CASE WHEN rp.id IS NOT NULL
        THEN rp.id ELSE (SELECT rps.id FROM res_partner rps WHERE rps.id = am.partner_id) END AS "partner_id",
        CASE WHEN rp.name IS NOT NULL
        THEN rp.name ELSE (SELECT rps.name FROM res_partner rps WHERE rps.id = am.partner_id) END AS "name",
        am.invoice_date_due,
        aa.name AS "account_id",
        aml.move_name,
        CASE WHEN aml.date_maturity >= %s::DATE
        OR aml.date >= %s::DATE AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "direction",
        CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '30 day')::DATE AND (%s::DATE - INTERVAL '1day')::DATE
        OR aml.date BETWEEN (%s::DATE - INTERVAL '30 day')::DATE AND (%s::DATE - INTERVAL '1day')::DATE
        AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "4",
        CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '60 day')::DATE AND (%s::DATE - INTERVAL '31day')::DATE
        OR aml.date BETWEEN (%s::DATE - INTERVAL '60 day')::DATE AND (%s::DATE - INTERVAL '31day')::DATE
        AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "3",
        CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '90 day')::DATE AND (%s::DATE - INTERVAL '61day')::DATE
        OR aml.date BETWEEN (%s::DATE - INTERVAL '90 day')::DATE AND (%s::DATE - INTERVAL '61day')::DATE
        AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "2",
        CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '120 day')::DATE AND (%s::DATE - INTERVAL '91day')::DATE
        OR aml.date BETWEEN (%s::DATE - INTERVAL '120 day')::DATE AND (%s::DATE - INTERVAL '91day')::DATE
        AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "1",
        CASE WHEN aml.date_maturity < (%s::DATE - INTERVAL '120 day')::DATE
        OR aml.date < (%s::DATE - INTERVAL '120 day')::DATE
        AND aml.date_maturity IS NULL
        THEN aml.amount_residual ELSE 0 END AS "0",
        aml.amount_residual FROM account_move_line aml
        LEFT JOIN account_move am ON am.id = aml.move_id
        LEFT JOIN res_partner rp ON rp.id = aml.partner_id
        LEFT JOIN account_account aa ON aa.id = aml.account_id
        LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        WHERE """+coa+"""
        AND """+m_comp+"""
        """+partners+"""
        AND am.state ='posted'
        AND aml.reconciled = 'f'
        ORDER BY rp.name)AS "query"
        GROUP BY query.name,query.partner_id
        ORDER BY query.name"""
        cr= self.env.cr
        cr.execute(query,(
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            str(self._context['date_to']),
            ))
        results= cr.dictfetchall()

        total = [
        sum([x['direction'] for x in results]),
        sum([x['4'] for x in results]),
        sum([x['3'] for x in results]),
        sum([x['2'] for x in results]),
        sum([x['1'] for x in results]),
        sum([x['0'] for x in results]),
        sum([x['total'] for x in results])
        ]
        for values in results:
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v}
                                                 for v in [values['direction'], values['4'],
                                                           values['3'], values['2'],
                                                           values['1'], values['0'], values['total']]],
                'trust': 'normal',
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                'partner_id': values['partner_id'],
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                m_partner = "a.partner_id =%s" % str(values['partner_id'])
                if values['partner_id'] == None:
                    m_partner = "a.partner_id IS NULL"
                qry = """
                WITH a AS(SELECT CASE WHEN rp.id IS NOT NULL
                THEN rp.id ELSE (SELECT rps.id FROM res_partner rps WHERE rps.id = am.partner_id) END AS "partner_id",
                CASE WHEN rp.name IS NOT NULL
                THEN rp.name ELSE (SELECT rps.name FROM res_partner rps WHERE rps.id = am.partner_id) END AS "name",
                am.invoice_date_due,
                aml.payment_id AS "aml.payment_id",
                aml.ref AS "aml.ref",
                am.id AS "am.id",
                aml.name AS "aml.name",
                aa.name AS "aml.account_id.display_name",
                aml.move_name AS "aml.move_id.name",
                aml.id AS "aml.id",
                aml.date AS "aml.date",
                aj.code AS "aml.journal_id.code",
                aml.date_maturity AS "aml.date_maturity",
                am.type AS "aml.move_id.type",
                am.journal_id AS "aml.move_id.journal_id.id",
                CASE WHEN aml.date_maturity >= %s::DATE
                OR aml.date >= %s::DATE AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "direction",
                CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '30 day')::DATE AND (%s::DATE - INTERVAL '1day')::DATE
                OR aml.date BETWEEN (%s::DATE - INTERVAL '30 day')::DATE AND (%s::DATE - INTERVAL '1day')::DATE
                AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "4",
                CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '60 day')::DATE AND (%s::DATE - INTERVAL '31day')::DATE
                OR aml.date BETWEEN (%s::DATE - INTERVAL '60 day')::DATE AND (%s::DATE - INTERVAL '31day')::DATE
                AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "3",
                CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '90 day')::DATE AND (%s::DATE - INTERVAL '61day')::DATE
                OR aml.date BETWEEN (%s::DATE - INTERVAL '90 day')::DATE AND (%s::DATE - INTERVAL '61day')::DATE
                AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "2",
                CASE WHEN aml.date_maturity BETWEEN (%s::DATE - INTERVAL '120 day')::DATE AND (%s::DATE - INTERVAL '91day')::DATE
                OR aml.date BETWEEN (%s::DATE - INTERVAL '120 day')::DATE AND (%s::DATE - INTERVAL '91day')::DATE
                AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "1",
                CASE WHEN aml.date_maturity < (%s::DATE - INTERVAL '120 day')::DATE
                OR aml.date < (%s::DATE - INTERVAL '120 day')::DATE
                AND aml.date_maturity IS NULL
                THEN aml.amount_residual ELSE 0 END AS "0",
                aml.amount_residual FROM account_move_line aml
                LEFT JOIN account_journal aj ON aml.journal_id = aj.id
                LEFT JOIN account_move am ON am.id = aml.move_id
                LEFT JOIN res_partner rp ON rp.id = aml.partner_id
                LEFT JOIN account_account aa ON aa.id = aml.account_id
                LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                WHERE """+coa+"""
                AND """+m_comp+"""
                AND am.state ='posted'
                AND aml.reconciled = 'f'
                ORDER BY rp.name)SELECT
                a."aml.payment_id",
                a."am.id",
                a."aml.id",
                a."aml.move_id.name",
                a."aml.date_maturity",
                a."aml.date",
                a."aml.journal_id.code",
                a."aml.account_id.display_name",
                a."direction",
                a."4",
                a."3",
                a."2",
                a."1",
                a."0",
                a."aml.move_id.type",
                a."aml.move_id.journal_id.id",
                a."aml.name",
                a."aml.ref",
                a."partner_id",
                a."aml.move_id.name"
                FROM a
                WHERE """+m_partner+""""""
                cd= self.env.cr
                cd.execute(qry,(
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    str(self._context['date_to']),
                    ))
                resultx= cd.dictfetchall()
                # for line in values['partner_id']:
                for line in resultx:
                    print("LINE_ID",line_id)
                    # aml = line['line']
                    if self.env['account.move'].search([('id','=',line['am.id'])]).is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif self.env['account.move'].search([('id','=',line['am.id'])]).is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif line['aml.payment_id']:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    # line_date = aml.date_maturity or aml.date
                    # if not self._context.get('no_format'):
                    #     line_date = format_date(self.env, line_date)
                    vals = {
                        'id': line['aml.id'],
                        'name': line['aml.move_id.name'],
                        'class': 'date',
                        # 'caret_options': caret_type,
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [format_date(self.env, line['aml.date_maturity'] or line['aml.date']), line['aml.journal_id.code'], line['aml.account_id.display_name'], ""]] +
                                   [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['direction'], line['4'], line['3'], line['2'], line['1'], line['0']]],
                        'action_context': {
                            'default_type': line['aml.move_id.type'],
                            'default_journal_id': line['aml.move_id.journal_id.id'],
                        },
                        'title_hover': self._format_aml_name(line['aml.name'], line['aml.ref'], line['aml.move_id.name']),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v} for v in [total[0], total[1], total[2], total[3], total[4], total[5], total[6]]],
            }
            lines.append(total_line)
        return lines