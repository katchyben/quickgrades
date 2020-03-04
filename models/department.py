from odoo import models, fields, api, exceptions


class Department(models.Model):
    _name = "quickgrades.department"
    _description = "Department"
    _order = 'name'

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=64, required=True)
    previous_code = fields.Char('Previous Code', size=64, required=False)
    faculty_id = fields.Many2one('quickgrades.faculty', 'Faculty', required=True)
    diploma_ids = fields.Many2many(comodel_name='quickgrades.diploma', string='Degrees')
    student_ids = fields.One2many('quickgrades.student', 'department_id', 'Student', readonly=True)
    programme_ids = fields.One2many('quickgrades.programme', 'department_id', 'Programmes', readonly=True)

