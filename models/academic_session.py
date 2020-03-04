from odoo import models, fields, api, exceptions


class AcademicSession(models.Model):
    """ Defining Level Information """
    _description = 'Academic Session Information'
    _name = 'academic.session'
    _order = "name"

    sequence = fields.Integer('Sequence', default=1, required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=20, required=True)
    description = fields.Text('Description')
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")


