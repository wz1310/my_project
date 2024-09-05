odoo.define('wu_sale_order_v1.wzr', function (require){
"use strict";

var ActionManager = require('web.ActionManager');
var session = require('web.session');

ActionManager.include({
    ir_actions_report: function (action, options) {
        var self = this;
        return $.when(this._super.apply(this, arguments), session.is_bound).then(function() {
            if (action && action.report_type === 'qweb-pdf' && action.close_on_report_download) {
                return self.do_action({ type: 'ir.actions.act_window_close' });
            }
        });
    },
});

}