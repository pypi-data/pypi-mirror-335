# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Partner Portal",
    "version": "14.0.1.2.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "portal",
        "web",
        "ssi_partner",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
        "views/assets.xml",
        "views/portal_templates.xml",
    ],
    "demo": [],
}
