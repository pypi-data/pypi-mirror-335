# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerCertification(models.Model):
    _name = "partner.certification"
    _inherit = "partner.experience.mixin"
    _description = "Contact's Certification Experience"

    certification = fields.Char(
        string="Certification Number",
        help="Certification Number",
    )
