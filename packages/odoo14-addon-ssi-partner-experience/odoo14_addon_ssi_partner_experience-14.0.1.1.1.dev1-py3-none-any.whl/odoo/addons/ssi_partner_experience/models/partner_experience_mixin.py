# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerExperienceMixin(models.AbstractModel):
    _name = "partner.experience.mixin"
    _inherit = [
        "mail.activity.mixin",
        "mail.thread",
        "mixin.date_duration",
    ]
    _description = "Abstract Class for Partner Experience"
    _date_end_required = False

    name = fields.Char(
        string="Name",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )
    partner_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Address",
        help="Employer, School, University, " "Certification Authority",
        domain="[('is_company', '!=', False)]",
    )
    location = fields.Char(
        string="Location",
        help="Location",
    )
    expire = fields.Boolean(
        string="Expire",
        help="Expire",
        default=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
