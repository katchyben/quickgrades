from odoo import models, fields, api, exceptions


class ProgrammeCourseEntry(models.Model):
    _name = "programme.course.entry"
    _description = "Course"
    _order = 'level_id,semester_id,name,code'

    name = fields.Char(related="course_id.name", string='Name', readonly=True, store=True)
    code = fields.Char(related="course_id.code", string='Code', readonly=True, store=True)
    semester_id = fields.Many2one(related="course_id.semester_id", string='Semester', readonly=True, store=True)
    units = fields.Integer("Units", required=True, default=1)
    course_id = fields.Many2one('programme.course', 'Prerequisite')
    programme_id = fields.Many2one('quickgrades.programme', 'Department')
    level_id = fields.Many2one('quickgrades.level', 'Level', required=True)

    def name_get(self):
        result = []
        for record in self:
            name = "{0}".format(record.code)
            result.append((record.id, name))
        return result