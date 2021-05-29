# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "PayTabs Payment Acquirer",
  "summary"              :  """The module allow the customers to make payments on Odoo website using Paytabs Payment Gateway. The module facilitates Paytabs integration with Odoo""",
  "category"             :  "Website",
  "version"              :  "2.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Saurabh Gupta",
  "website"              :  "https://store.webkul.com/Odoo-Website-PayTabs-Payment-Acquirer.html",
  "description"          :  """Odoo Website PayTabs Payment Acquirer
Paytabs Sadad
Odoo Paytabs Payment Acquirer
Odoo Paytabs Payment Gateway
Payment Gateway
Paytabs
Pay tab
Paytabs integration
Payment acquirer
Payment processing
Payment processor
Website payments
Sale orders payment
Customer payment
Integrate Paytabs payment acquirer in Odoo
Integrate Paytabs payment gateway in Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_paytabs_wk&version=12.0&custom_url=/shop/payment",
  "depends"              :  [
                             'payment',
                             'website_sale',
                            ],
  "data"                 :  [
                             'views/template.xml',
                             'views/paytabs_payment_wk_view.xml',
                             'views/res_country_inherit_view.xml',
                            ],
  "demo"                 :  ['data/demo_paytabs.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  49.0,
  "currency"             :  "USD",
  "post_init_hook"       :  "create_missing_journal_for_acquirers",
}