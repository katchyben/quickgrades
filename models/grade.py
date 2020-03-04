from odoo import models, fields, api, exceptions


class Grade(models.Model):
    _name = 'quickgrades.grade'
    _description = 'Academic Grade'
    _order = 'name asc'

    name = fields.Char('Grade', size=64, required=True)
    point = fields.Float(required=True)
    description = fields.Char('Description', size=250)
    min_grade = fields.Float('Lower Bound', required=True)
    max_grade = fields.Float('Upper Bound', required=True)
    is_pass_mark = fields.Boolean('Is Pass Mark?')
    grading_scheme_id = fields.Many2one('quickgrades.grading.scheme', 'Grading Scheme')



