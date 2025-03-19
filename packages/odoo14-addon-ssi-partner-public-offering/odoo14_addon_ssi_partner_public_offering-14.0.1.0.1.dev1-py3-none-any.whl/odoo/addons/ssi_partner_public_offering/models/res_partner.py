# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    public_offering_ids = fields.Many2many(
        string="Public Offering",
        comodel_name="company_public_offering_type",
        relation="rel_res_partner_2_public_offering_type",
        column1="partner_id",
        column2="public_offering_type_id",
    )
