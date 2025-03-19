# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PortalPartnerExperience(models.Model):
    _name = "portal_partner_experience"
    _inherit = ["partner.experience"]
    _description = "Portal Partner Experience"
    _table = "partner_experience"
    _order = "date_start"
