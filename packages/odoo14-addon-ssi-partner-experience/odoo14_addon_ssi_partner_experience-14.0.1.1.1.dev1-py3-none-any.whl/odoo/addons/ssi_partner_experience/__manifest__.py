# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Partner Experience",
    "version": "14.0.1.1.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "mail",
        "ssi_duration_mixin",
        "ssi_partner_education_level",
    ],
    "data": [
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "menu.xml",
        "views/partner_academic_view.xml",
        "views/partner_certification_view.xml",
        "views/partner_experience_view.xml",
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
    ],
    "demo": [],
}
