from odoo import models, fields, api, exceptions


class LegacyStudent(models.Model):
    """ Defining Template For Student Import"""
    _name = "academic.legacy.student"
    _description = "Legacy Student"
    _order = "matric asc"

    name = fields.Char('Name', size=128, required=True)
    matric = fields.Char('Registration. No', required=True, index=1, help='matric')
    application_number = fields.Char('Application. No', size=64, help='Application No.')
    level = fields.Char('Level', required=True)
    dept = fields.Char('Dept', required=True)
    status = fields.Selection(
        string='Status',
        selection=[('New', 'New'), ('Failed', 'Failed'), ('Processed', 'Processed')],
        default='New',
        readonly=True
    )
