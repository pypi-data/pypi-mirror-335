# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    shareholder_ids = fields.One2many(
        string="Shareholders",
        comodel_name="company.shareholder",
        inverse_name="partner_id",
    )
