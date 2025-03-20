# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerAcademic(models.Model):
    _name = "partner.academic"
    _inherit = "partner.experience.mixin"
    _description = "Contact's Academic Experience"

    diploma = fields.Char(
        string="Diploma Number",
    )
    education_level_id = fields.Many2one(
        string="Education Level",
        comodel_name="partner.formal_education_level",
    )
    field_of_study_id = fields.Many2one(
        string="Field of Study",
        comodel_name="partner.field_of_study",
    )
    gpa = fields.Float(
        string="Latest GPA",
    )
    activities = fields.Text(
        string="Activities and associations",
    )
