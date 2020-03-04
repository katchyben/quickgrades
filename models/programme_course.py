from odoo import models, fields, api, exceptions


class ProgrammeCourse(models.Model):
    _name = "programme.course"
    _description = "Course"
    _order = 'name, code, semester_id'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    semester_id = fields.Many2one('quickgrades.semester', 'Semester', required=True)
    diploma_id = fields.Many2one('quickgrades.diploma', 'Degree', required=True)
    entry_ids = fields.One2many('programme.course.entry', 'course_id', 'Programmes')

    def name_get(self):
        result = []
        for record in self:
            name = "{0}".format(record.code)
            result.append((record.id, name))
        return result
