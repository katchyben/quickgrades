from odoo import models, fields, api, exceptions


class Diploma(models.Model):
    _name = 'quickgrades.diploma'
    _description = "Degree"
    _order = 'name desc'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(size=130, string='Description')
    department_ids = fields.Many2many(comodel_name='quickgrades.department', string='Departments')

