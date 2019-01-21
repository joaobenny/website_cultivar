# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

class WebsiteCultivar(http.Controller):

    @http.route('/page/homepage', type='http', auth="public", website=True)
    def cultivar_home(self, **post):


        events = request.env['event.event'].sudo().search([])

        return request.render("website.homepage", {'events': events})
