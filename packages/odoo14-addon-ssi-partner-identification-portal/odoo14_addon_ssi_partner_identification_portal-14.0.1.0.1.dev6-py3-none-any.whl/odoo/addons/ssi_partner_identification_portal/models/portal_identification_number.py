# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PortalIdentificationNumber(models.Model):
    _name = "portal_identification_number"
    _inherit = ["res.partner.id_number"]
    _description = "Portal Identification Number"
    _table = "res_partner_id_number"
    _order = "category_id"
