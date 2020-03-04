from odoo import models, fields, api, exceptions


class Programme(models.Model):
    _name = "quickgrades.programme"
    _description = "Academic Programme"
    _order = 'department_id asc'

    name = fields.Char(compute='_compute_name', string="Name", store=True)
    department_id = fields.Many2one('quickgrades.department', 'Department', required=True)
    faculty_id = fields.Many2one('quickgrades.faculty', 'Faculty', required=True)
    diploma_id = fields.Many2one('quickgrades.diploma', 'Degree', required=True)
    course_ids = fields.One2many('programme.course.entry', 'programme_id', 'Courses')
    school_id = fields.Many2one(related='faculty_id.school_id', readonly=True, store=True)

    @api.depends('department_id', 'diploma_id')
    def _compute_name(self):
        for record in self:
            record.name = "{0} {1}".format(record.diploma_id.code, record.department_id.name)
