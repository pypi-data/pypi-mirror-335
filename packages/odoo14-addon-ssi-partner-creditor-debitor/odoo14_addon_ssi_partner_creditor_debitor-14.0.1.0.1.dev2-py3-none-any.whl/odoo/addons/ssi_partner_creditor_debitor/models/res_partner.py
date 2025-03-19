# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    primary_creditor_id = fields.Many2one(
        string="Primary Creditor",
        comodel_name="res.partner",
        compute="_compute_primary_creditor_id",
        store=True,
    )
    creditor_ids = fields.One2many(
        string="Creditors",
        comodel_name="partner_creditor_debtor",
        inverse_name="debtor_id",
    )
    debtor_ids = fields.One2many(
        string="Debitors",
        comodel_name="partner_creditor_debtor",
        inverse_name="creditor_id",
    )

    @api.depends(
        "creditor_ids",
        "creditor_ids.sequence",
        "creditor_ids.creditor_id",
    )
    def _compute_primary_creditor_id(self):
        for record in self:
            result = False
            if record.creditor_ids:
                result = record.creditor_ids[0].creditor_id
            record.primary_creditor_id = result
