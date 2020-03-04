from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class StudentResultBook(models.Model):
    _description = 'Collection Student Academic Record'
    _name = 'student.result'
    _order = 'student_id, programme_id'
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('student_result_book_uniq',
         'UNIQUE (student_id)',
         'Student can only have one Result Book!')]

    student_id = fields.Many2one('quickgrades.student', 'Student', required=True)
    programme_id = fields.Many2one(related='student_id.programme_id', string='Programme')
    entry_ids = fields.One2many(comodel_name='student.result.entry', inverse_name='student_result_id', string='Entries',
                                required=False, track_visibility="always")
    outstanding_result_ids = fields.Many2many(comodel_name='student.result.entry',
                                              compute='_compute_outstanding_results', string="Outstanding Results",
                                              readonly=True)
    outstanding_course_ids = fields.Many2many(comodel_name='programme.course.entry',
                                              compute='_compute_outstanding_courses', string="Outstanding Courses",
                                              readonly=True)
    cgpa = fields.Float(string="CGPA", readonly=True, track_visibility="always")
    honours_id = fields.Many2one(comodel_name='quickgrades.honour', compute='_compute_honour', readonly=True, store=True,
                                 string="Honours", track_visibility="always")
    approved_result_ids = fields.One2many('student.result.entry', string='Approved Results',
                                          compute='_compute_approved_results', readonly=True)

    @api.depends('entry_ids')
    def _compute_outstanding_results(self):
        for record in self:
            res = []
            failed_courses = record.entry_ids.filtered(lambda c: c.grade_id.is_pass_mark == False and
                                                                 c.status == 'Approved')
            passed_courses = record.entry_ids.filtered(lambda c: c.grade_id.is_pass_mark == True)
            # _logger.debug("now in _compute_outstanding_results")
            # _logger.debug(failed_courses)
            # _logger.debug(passed_courses)
            for failed_course in failed_courses:
                if failed_course.id not in passed_courses.ids:
                    res.append(failed_course.id)

            record.outstanding_result_ids = res

    @api.depends('entry_ids')
    def _compute_outstanding_courses(self):
        for record in self:
            record.outstanding_course_ids = [entry.course_id.id for entry in record.outstanding_result_ids]

    def _compute_approved_results(self):
        for record in self:
            record.approved_result_ids = record.mapped('result_ids').filtered(
                lambda result: result.status == 'Approved')

    def action_recompute_cgpa(self):
        for record in self:
            if record.result_ids:
                approved_results = record.approved_result_ids
                gpa = self.env['academic.honour'].compute_gpa(approved_results)
                _logger.debug(
                    "Updating Semester GPA for {} ... {} to {}".format(record.matriculation_number, record.gpa, gpa))
                record.write({'gpa': gpa})
