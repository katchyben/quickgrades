from odoo import models, fields, api, exceptions


class HonourScheme(models.Model):
    _name = 'quickgrades.honour.scheme'
    _description = 'Academic Honors Scheme'
    name = fields.Char('Grade', size=128, required=True)
    description = fields.Text('Description')
    options = fields.Selection(string="Options",
                               selection=[
                                   ('allow_grade_replacement',
                                    'Allow Grades Replacement'),
                                   ('no_allow_replacement',
                                    'No Grades Replacement'),
                               ])
    honour_ids = fields.One2many(
        'quickgrades.honour', 'honour_scheme_id', 'Honour Scheme')

