from odoo import models, fields, _


class ImpactDataType(models.Model):
    _name = "impact.data.type"
    _description = "Impact Data Type"
    _order = "name asc"

    name = fields.Char(string=_("Name"), required=True, help=_("Name of the type."))
    description = fields.Text(
        string=_("Description"), help=_("Description of the type.")
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string=_("Company"),
        default=lambda self: self.env.company,
        help=_("Company to which the type belongs."),
    )

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique(name, company_id)",
            "Type name must be unique by company.",
        )
    ]
