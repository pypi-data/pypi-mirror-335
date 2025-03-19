# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    ownership_type_id = fields.Many2one(
        string="Ownership Type",
        comodel_name="company_ownership_type",
    )
    entity_type_id = fields.Many2one(
        string="Entity Type",
        comodel_name="company_entity_type",
    )
    blood_type = fields.Selection(
        string="Blood Type (ABO)",
        selection=[
            ("A", "A"),
            ("B", "B"),
            ("0", "O"),
            ("AB", "AB"),
        ],
        required=False,
    )
    blood_type_rhesus = fields.Selection(
        string="Blood Type (Rh)",
        selection=[
            ("positive", "+"),
            ("negative", "-"),
        ],
        required=False,
    )
    religion_id = fields.Many2one(
        string="Religion",
        comodel_name="res_partner_religion",
    )
    ethnicity_id = fields.Many2one(
        string="Ethnicity",
        comodel_name="res_partner_ethnicity",
    )
    marital = fields.Selection(
        string="Marital Status",
        selection=[
            ("single", "Single"),
            ("married", "Married"),
            ("cohabitant", "Legal Cohabitant"),
            ("widower", "Widower"),
            ("divorced", "Divorced"),
        ],
        default="single",
        required=False,
    )
    spouse_complete_name = fields.Char(
        string="Spouse Complete Name",
        required=False,
    )
    spouse_birthdate = fields.Date(
        string="Spouse Birthdate",
        required=False,
    )
