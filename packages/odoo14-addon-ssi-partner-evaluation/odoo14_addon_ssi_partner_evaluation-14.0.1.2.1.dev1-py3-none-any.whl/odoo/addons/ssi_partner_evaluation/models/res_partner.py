# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    partner_evaluation_result_ids = fields.One2many(
        string="Partner Evaluation Results",
        comodel_name="res.partner.evaluation_result",
        inverse_name="partner_id",
        readonly=True,
    )

    partner_evaluation_ids = fields.One2many(
        string="Partner Evaluations",
        comodel_name="partner_evaluation",
        inverse_name="partner_id",
        readonly=True,
    )

    def _get_partner_evaluation_result(self, evaluation_type):
        self.ensure_one()
        result = False
        evaluations = self.partner_evaluation_result_ids.filtered(
            lambda r: r.type_id.id == evaluation_type.id
        )
        if evaluations:
            result = evaluations[0]

        return result
