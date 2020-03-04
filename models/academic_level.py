from odoo import models, fields, api, exceptions


class AcademicLevel(models.Model):
    """ Defining Level Information """
    _description = 'Academic Level Information'
    _name = 'quickgrades.level'
    _order = "name"

    sequence = fields.Integer('Sequence', default=1, required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=20, required=True)
    next_class_id = fields.Many2one('quickgrades.level', "Next Class")
    previous_class_id = fields.Many2one('quickgrades.level', "Previous Class")
    diploma_id = fields.Many2one('quickgrades.diploma', "Degree", required=True)
    description = fields.Text('Description')
