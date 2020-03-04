from odoo import models, fields, api, exceptions


class SchoolCourse(models.Model):
    """ Defining Template For Course Import"""
    _name = "academic.school.course"
    _description = "Course Import"
    _order = "title asc"
    _rec_name = "title"

    title = fields.Char('Title', required=True)
    code = fields.Char('Code', help='Code')
    units = fields.Char('Units', required=True, help='Units')
    semester = fields.Char('Semester', required=True)
    level = fields.Char('Level', required=True)
    programme = fields.Char('Programme', required=True)
    option = fields.Char('Option', required=False)
    status = fields.Selection(
        string='Status',
        selection=[('New', 'New'), ('Failed', 'Failed'), ('Processed', 'Processed')],
        default='New',
        readonly=True
    )