from odoo import models, fields, api, exceptions
import re


class LegacyStudentResult(models.Model):
    """ Defining Template For Student Result Import"""
    _name = "academic.legacy.student.result"
    _description = "Legacy Student Result"
    _order = "matric asc"
    _rec_name = "course"

    session = fields.Char('Session', required=True)
    course = fields.Char('Course', required=True)
    level = fields.Char('Level', required=True)
    dept = fields.Char('Dept', required=True)
    semester = fields.Char('Semester', required=True)
    matric = fields.Char('Registration', required=True, index=1, help='matric')
    practicals = fields.Float('Practicals', required=False)
    exam = fields.Float('Exam', required=True)
    test = fields.Float('C/A', required=True)
    total = fields.Float(compute='_compute_total', string="Total", store=True, readonly=True)
    grade = fields.Char('Grade')
    status = fields.Selection(
        string='Status',
        selection=[('New', 'New'), ('Failed', 'Failed'), ('Processed', 'Processed')],
        default='New',
        readonly=True
    )
    remarks = fields.Char('Remarks')

    def partition(self, data):
        if " " in data:
            return data
        else:
            parts = re.split('(\d.*)', data)
            return "{} {}".format(parts[0], parts[1])

    def find(self, session, semester, course, matric):
        domain = [('session', '=', session), ('semester', '=', semester),
                  ('course', '=', course), ('matric', '=', matric)]
        return self.env['academic.legacy.student.result'].search(domain)

    @api.constrains('exam', 'test', 'practicals')
    def _check_total(self):
        for record in self:
            total = record.exam + record.test + record.practicals
            if total > 100.00:
                raise exceptions.ValidationError("'Total {}' is greater than 100".format(total))

    def delete(self, result):
        result.unlink()

    @api.depends('exam', 'test', 'practicals')
    def _compute_total(self):
        for record in self:
            record.total = record.exam + record.test + record.practicals

    @api.model
    def create(self, vals):
        # Sanitize data
        vals['session'] = str(vals["session"]).strip().replace(" ", "")
        vals['semester'] = str(vals["semester"]).strip().replace(" ", "").lower()
        vals['course'] = self.partition(str(vals["course"]).strip())
        vals['exam'] = float(str(vals["exam"]).strip())
        vals['test'] = float(str(vals["test"]).strip())
        vals['matric'] = str(vals["matric"]).replace(" ", "").strip()
        vals['dept'] = str(vals['dept']).upper().strip()

        # Remove Existing Record to create anew one.
        res = self.find(vals['session'], vals['semester'], vals['course'], vals['matric'])
        if res:
            self.delete(res)

        vals['level'] = self.partition(str(vals["level"]).strip().replace(" ", ""))

        return super(LegacyStudentResult, self).create(vals)
