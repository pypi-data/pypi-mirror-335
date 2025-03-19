# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PortalPartnerBankAccount(models.Model):
    _name = "portal_partner_bank_account"
    _inherit = ["res.partner.bank"]
    _description = "Portal Partner Bank Account"
    _table = "res_partner_bank"
    _order = "acc_number"
