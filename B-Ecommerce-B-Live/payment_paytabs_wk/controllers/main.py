import logging
_logger = logging.getLogger(__name__)
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import requests
from ast import literal_eval
import json
import werkzeug.utils
from werkzeug.exceptions import BadRequest
from odoo.service import common



class WebsiteSale(WebsiteSale):
	_paytabs_feedbackUrl='/payment/paytabs/feedback'

	@http.route([_paytabs_feedbackUrl], type='json', auth='public', website=True)
	def paytabs_payment(self, **post):
		merchant_detail = request.env["payment.acquirer"].sudo().browse(int(post.get('acquirer',0)))
		partner = request.env.user.partner_id
		products,qty,price_unit,sale_order_detail,billing_address,address_shipping = merchant_detail.create_paytabs_params(partner,post)
		request.session['so_id']= post.get("reference")
		total_amount = literal_eval(post.get('amount'))
		try:
			client_id = int(merchant_detail.paytabs_client_id)
		except Exception as e:
			_logger.warning("-------- Client Id issue ------ %r",e)
			return {"message":"Invalid client id "}
		paytabs_tx_values = {
				"profile_id": client_id,
				"payment_methods": ["all"],
				"tran_type": "sale",
				"tran_class": "ecom",
				"cart_id": post.get("reference"),
				"cart_currency": post.get('currency'),
				"cart_amount": total_amount,
				"cart_description": post.get("reference"),
				"paypage_lang": "en",
				"customer_details": {
					"name": partner.name,
					"email": partner.email or sale_order_detail.partner_id.email,
					"phone": partner.phone,
					"street1": address_shipping.street or partner.street ,
					"state": partner.state_id.name or sale_order_detail.partner_shipping_id.name,
					"city": partner.city or sale_order_detail.partner_shipping_id.name,
					"country": partner.country_id.code2  or  sale_order_detail.partner_id.country_id.code2,
					"zip":partner.zip or sale_order_detail.partner_id.zip,
					"ip": request.httprequest.environ['REMOTE_ADDR'],
				},
				"shipping_details": {
					"name": partner.name,
					"email": partner.email or sale_order_detail.partner_id.email,
					"phone": partner.phone,
					"street1": address_shipping.street or partner.street ,
					"state": partner.state_id.name or sale_order_detail.partner_shipping_id.name,
					"city": partner.city or sale_order_detail.partner_shipping_id.name,
					"country": partner.country_id.code2  or  sale_order_detail.partner_id.country_id.code2,
					"zip":partner.zip or sale_order_detail.partner_id.zip,
					"ip": request.httprequest.environ['REMOTE_ADDR'],
				},
				"return": merchant_detail.paytabs_url().get('return_url'),
			}
		headers = {"authorization":merchant_detail.paytabs_client_secret,'Content-Type': 'application/json'}
		result = requests.post(url= merchant_detail.paytabs_url().get('pay_page_url'),headers = headers, data=json.dumps(paytabs_tx_values))
		request_params = literal_eval(result.text)
		if request_params.get("tran_ref"):
			request.session['tx_id']= request_params.get("tran_ref")
		return request_params

	@http.route(['/paytabs/feedback'], type='http', auth='public', website=True ,csrf=False)
	def paytabs_feedback(self, **post):
		acquirer =  request.env["payment.acquirer"].sudo().search([("provider","=","paytabs")])
		params = {
			"profile_id": int(acquirer.paytabs_client_id),
			"tran_ref": request.session.get('tx_id')
		}
		headers = {"authorization":acquirer.paytabs_client_secret,'Content-Type': 'application/json'}
		result = requests.post(url= acquirer.paytabs_url().get('verify_payment'),headers = headers, data=json.dumps(params))
		request_params = json.loads(result.text)
		request_params["paytabs_transaction_id"] = request.session.get('tx_id')
		request.env['payment.transaction'].form_feedback(request_params, 'paytabs')
		return werkzeug.utils.redirect('/payment/process')
