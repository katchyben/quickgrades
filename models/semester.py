from odoo import models, fields, api


class Semester(models.Model):
    """ Defining an academic year """
    _name = "quickgrades.semester"
    _description = "Semester"
    _order = "sequence asc"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', size=64, required=True, index=1, help='Name')
    code = fields.Char('Code', required=True, index=1, help='Code')
