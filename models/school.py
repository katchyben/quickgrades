from odoo import models, fields, api, exceptions


class School(models.Model):
    """ Defining School Information """
    _description = 'School Information'
    _name = 'quickgrades.school'
    _inherits = {'res.company': 'company_id'}

    company_id = fields.Many2one('res.company', 'Company', ondelete="cascade", required=True)
    code = fields.Char('Code', size=20, required=True, index=1)
    faculty_ids = fields.One2many('quickgrades.faculty', 'school_id', 'Faculties')
    grading_scheme_id = fields.Many2one('quickgrades.grading.scheme', 'Grading Scheme')
    honour_scheme_id = fields.Many2one('quickgrades.honour.scheme', 'Honour Scheme')
