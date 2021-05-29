##########################################################################

import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _
from odoo.addons.payment_paytabs_wk.controllers.main import WebsiteSale
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request


class AcquirerPayTabs(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paytabs', 'PayTabs')],ondelete={'paytabs': 'set default'})
    paytabs_client_id = fields.Char('PayTabs Client Profile Id', required_if_provider='paytabs', groups='base.group_user' )
    paytabs_client_secret = fields.Char('PayTabs Client Secret API Key', required_if_provider='paytabs', groups='base.group_user'  )



    # @api.model
    # def get_paytabs_params(self, values):
    #     _logger.info('------------values-------------%r',values)

# methoda called by form of paytabs for pass the form value
    def paytabs_form_generate_values(self, values):
        paytabs_tx_values = dict(values)
        paytabs_tx_values.update({
            'amount': values['amount'],
            'reference':str(values['reference']),
            'currency_code': values['currency'] and values['currency'].name or '',
        })
        return paytabs_tx_values

# methods of form action redirection of paytabs
    # def paytabs_get_form_action_url(self):
    #     self.ensure_one()
    #     return WebsiteSale._paytabs_feedbackUrl

    def detail_payment_acquire(self):
        return{
        "paytabs_client_secret":self.paytabs_client_secret,
        "paytabs_client_id":self.paytabs_client_id,
        }



# transaction url for paytabs
    def paytabs_url(self):
        base_url = request.httprequest.host_url
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return{
        "pay_page_url"      : "https://secure.paytabs.sa/payment/request",
        "verify_payment"    : 'https://secure.paytabs.sa/payment/query',
        'base_url' : base_url,
        'return_url': base_url+'paytabs/feedback',
        }


    def create_paytabs_params(self,partner,post):
        # def create_paytabs_params(self,partner,post):
        sale_order_detail = None
        products = ""
        qty = ""
        price_unit = ""
        order_line = []
        billing_address = ""
        address_shipping = ""

        if  "S0" in  post.get("reference")  :
            sale_order_detail = self.env['sale.order'].sudo().search([('name','=',post.get("reference").split('-')[0])])
            order_line = [sale_order_detail.order_line,True]
            billing_address =  sale_order_detail.partner_invoice_id
            address_shipping = sale_order_detail.partner_shipping_id

        elif  "INV"  in post.get("reference"):
            invoice_obj = self.env['account.move'].sudo().search([('name','=',post.get("reference").split('-')[0])])
            sale_order_detail = invoice_obj
            order_line = [invoice_obj.invoice_line_ids,False]
            billing_address = partner
            address_shipping = sale_order_detail.partner_shipping_id

        if not sale_order_detail:
            sale_order_detail = partner.last_website_so_id

        for i in order_line[0]:
            products = products +  i.product_id.name +" || "
            price_unit = price_unit +   str(i.price_unit) +" || "
            if order_line[1]:
                qty = qty + str(int(i.product_uom_qty)) +" || "

            else:
                qty = qty + str(int(i.quantity)) +" || "

        return products[0:len(products)-4],qty[0:len(qty)-4],price_unit[0:len(price_unit)-4],sale_order_detail,billing_address,address_shipping



class TransactionPayTabs(models.Model):
    _inherit = 'payment.transaction'


    paytabs_txn_id = fields.Char('Transaction ID')


    @api.model
    def _paytabs_form_get_tx_from_data(self,  data):
        reference = data.get('cart_id')
        tx = self.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('PayTabs: received data with missing reference (%s)') % (reference)
            if not tx.ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            raise ValidationError(error_msg)
        return tx

    def _paytabs_form_validate(self, data):
        res = {}
        payment_data = data.get('payment_result')
        tx = data.get("paytabs_transaction_id")
        if payment_data.get("response_message") == 'Authorised' and payment_data.get("response_status") == "A":
            res = {
            'date':fields.datetime.now(),
            'acquirer_reference': tx,
            'paytabs_txn_id': tx,
            }
            self.write(res)
            return self._set_transaction_done()
        else:
            if payment_data.get("response_message") == "Cancelled":
                res.update({
                'date':fields.datetime.now(),
                'paytabs_txn_id': tx,
                })
                self.write(res)
                return self._set_transaction_cancel()
            else:
                res.update({
                    'paytabs_txn_id': tx,
                    'acquirer_reference': tx,
                    'date':fields.datetime.now(),
                    })
                self.write(res)
                return self._set_transaction_pending()
