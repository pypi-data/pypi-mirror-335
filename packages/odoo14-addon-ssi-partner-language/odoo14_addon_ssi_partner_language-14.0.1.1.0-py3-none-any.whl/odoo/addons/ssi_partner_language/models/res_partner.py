# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    language_ids = fields.One2many(
        comodel_name="partner.language",
        inverse_name="partner_id",
        string="Languages",
        help="Languages",
    )
