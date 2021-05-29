odoo.define('payment_paytab_wk.payment_paytab_wk', function (require) {
    "use strict";
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    var qweb = core.qweb;
    var _t = core._t;
    var PaytabPaymentForm = publicWidget.Widget.extend({


    init: function() {
          this.reference = $('#reference').val();
          this.amount = $('#amount').val();
          this.currency = $('#currency').val();
          this.acquirer = $('#acquirer').val();
          this._initBlockUI(_t("Loading..."));
          console.log(this.reference);
          console.log(this.amount);
          console.log(this.currency);
          console.log(this.acquirer);
        //   this.return_url = $('#hyperpay_ret_url').val();
          this.start();
      },
    start: function() {
          var self = this;
          self._createPaytabsCheckoutId();
      },
    _createPaytabsCheckoutId: function() {
          var self = this;

          ajax.jsonRpc('/payment/paytabs/feedback', 'call', {
              'reference': self.reference,
              'amount': self.amount,
              'currency': self.currency,
              'acquirer': self.acquirer

          })
          .then(function(result) {
            $.unblockUI()
            if (result.redirect_url) {
                window.location = result.redirect_url;
            } else {
                var error_note = $('#error_note');
                if (error_note.length) {
                    $('#error_note').text(' ' + result.message)
                } else {
                    var form_el = $('input[data-provider="paytabs"]').parent().append('<div id="error_note" style="font-weight:bold;color:red;">' + result.message + '</div>')
                }
            }
        });
      },
    _initBlockUI: function(message) {
            if ($.blockUI) {
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/payment_paytabs_wk/static/src/img/ajax-loader.gif" class="fa-pulse"/>' +
                            '    <br />' + message +
                            '</h2>'
                });
            }
        },

      });
    new PaytabPaymentForm();

});
