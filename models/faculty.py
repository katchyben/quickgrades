from odoo import models, fields, api, exceptions


class Faculty(models.Model):
    _name = "quickgrades.faculty"
    _description = "Faculty"
    _order = "name"

    school_id = fields.Many2one('quickgrades.school', "School")
    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    department_ids = fields.One2many('quickgrades.department', 'faculty_id', 'Add Department')
    programme_ids = fields.One2many('quickgrades.programme', 'faculty_id', 'Programmes')
