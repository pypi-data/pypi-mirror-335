# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    formal_education_level_id = fields.Many2one(
        string="Latest Formal Level Education",
        comodel_name="partner.formal_education_level",
    )
    field_of_study_id = fields.Many2one(
        string="Latest Field of Study",
        comodel_name="partner.field_of_study",
    )
    education_institution_id = fields.Many2one(
        string="Latest Formal Education Institution",
        comodel_name="res.partner",
    )
    gpa = fields.Float(
        string="Latest GPA",
    )
    diploma = fields.Char(
        string="Latest Diploma",
    )
