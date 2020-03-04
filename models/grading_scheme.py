from odoo import models, fields, api, exceptions


class GradingScheme(models.Model):
    _name = 'quickgrades.grading.scheme'
    _description = 'Academic Grading Scheme'

    name = fields.Char('Name', size=64, required=True)
    description = fields.Text('Description')
    grading_ids = fields.One2many('quickgrades.grade', 'grading_scheme_id', 'Gradings')

    def get_grade(self, score):
        res = 0
        for scheme in self:
            for grade in scheme.grading_ids:
                if grade.min_grade <= score <= grade.max_grade:
                    res = grade.id
                    break
        return res
