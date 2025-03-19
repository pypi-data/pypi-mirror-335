# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CompanyShareholder(models.Model):
    _name = "company.shareholder"
    _description = "Company Shareholder"
    _order = "partner_id, sequence, id"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=10,
    )
    shareholder_id = fields.Many2one(
        string="Shareholder",
        comodel_name="res.partner",
        required=True,
    )
    number_of_share = fields.Integer(
        string="Num. Of Share",
        required=True,
        default=1,
    )
