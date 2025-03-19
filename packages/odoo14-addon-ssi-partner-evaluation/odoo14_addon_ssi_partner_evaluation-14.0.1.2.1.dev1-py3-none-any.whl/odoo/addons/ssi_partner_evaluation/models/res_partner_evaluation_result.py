# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartnerEvaluationResult(models.Model):
    _name = "res.partner.evaluation_result"
    _description = "res.partner - Evaluation Result"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        ondelete="cascade",
        required=True,
    )
    type_id = fields.Many2one(
        string="Evaluation Type",
        comodel_name="partner_evaluation_type",
        ondelete="restrict",
        required=True,
    )
    latest_evaluation_id = fields.Many2one(
        string="Latest Evaluation",
        comodel_name="partner_evaluation",
        compute="_compute_latest_evaluation_id",
        store=True,
        compute_sudo=True,
    )
    result_id = fields.Many2one(
        string="Result",
        related="latest_evaluation_id.final_result_id",
        store=True,
    )
    date = fields.Date(
        related="latest_evaluation_id.date",
        store=True,
    )

    @api.depends(
        "partner_id",
        "partner_id.partner_evaluation_ids",
        "partner_id.partner_evaluation_ids.type_id",
        "partner_id.partner_evaluation_ids.state",
        "partner_id.partner_evaluation_ids.final_result_id",
    )
    def _compute_latest_evaluation_id(self):
        for record in self:
            result = False
            evaluations = record.partner_id.partner_evaluation_ids.filtered(
                lambda r: r.state == "done" and r.type_id.id == record.type_id.id
            )
            if evaluations:
                result = evaluations[0]
            record.latest_evaluation_id = result
