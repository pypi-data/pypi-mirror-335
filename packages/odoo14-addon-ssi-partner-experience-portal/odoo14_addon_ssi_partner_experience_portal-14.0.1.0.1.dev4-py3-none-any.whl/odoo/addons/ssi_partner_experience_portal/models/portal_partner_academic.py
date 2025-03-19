# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PortalPartnerAcademic(models.Model):
    _name = "portal_partner_academic"
    _inherit = ["partner.academic"]
    _description = "Portal Partner Academic"
    _table = "partner_academic"
    _order = "date_start"
