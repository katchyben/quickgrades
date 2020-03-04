from odoo import models, fields, api, exceptions


class StudentResultBookEntry(models.Model):
    _description = 'Student Academic Record'
    _name = 'student.result.entry'
    _order = 'entry_date, session_id, semester_id, level_id'

    _sql_constraints = [
        ('student_result_uniq',
         'UNIQUE (student_id, session_id, course_id, semester_id)',
         'Student can only register a particular once a session!')]

    @api.model
    def _default_school(self):
        return self.env['quickgrades.school'].search([('name', '=', 'Nnamdi Azikiwe University')], limit=1)

    @api.model
    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    entry_date = fields.Date('Date', default=_get_default_date)
    student_id = fields.Many2one(comodel_name='quickgrades.student', string='Student')
    programme_id = fields.Many2one(related='student_id.programme_id', store=True, string='Programme', readonly=True)
    reg_number = fields.Char(related='student_id.matriculation_number', store=True, string='Reg #', readonly=True)
    student_result_id = fields.Many2one('student.result', 'Result Book')
    session_id = fields.Many2one('academic.session', 'Session')
    section_id = fields.Many2one('academic.section', 'Class')
    semester_id = fields.Many2one(comodel_name='quickgrades.semester', string='Semester', readonly=True)
    course_id = fields.Many2one(comodel_name='programme.course.entry', string='Course', readonly=True)
    level_id = fields.Many2one(comodel_name='quickgrades.level', string='Level', readonly=True)
    course_name = fields.Char(related="course_id.name", string='Course Name', readonly=True, store=True)
    course_code = fields.Char(related="course_id.code", string='Course Code', readonly=True, store=True)
    units = fields.Integer(related='course_id.units', string='Units', readonly=True, store=True)
    remarks = fields.Text('Remarks', track_visibility="all")
    gpa = fields.Float("GPA")
    ca_score = fields.Float('Examination Score', track_visibility="onchange")
    test_score = fields.Float('Test Score', track_visibility="onchange")
    points = fields.Float(related="grade_id.point", string='Points', readonly=True, store=True)
    points_obtained = fields.Float(string='Points Obtained', readonly=True)
    practicals_score = fields.Float('Practicals Score', track_visibility="onchange")
    score = fields.Float(compute='_compute_total_score', string="Total", store=True, readonly=True,
                         track_visibility="onchange")
    grade_id = fields.Many2one(comodel_name='quickgrades.grade', compute='_compute_grade',
                               string="Grade", readonly=True, store=True, track_visibility="onchange")
    school_id = fields.Many2one('quickgrades.school', 'School', default=_default_school)
    is_pass_mark = fields.Boolean(compute='_compute_is_pass_mark', string="Is Pass Mark?", store=True, readonly=True,
                                  track_visibility="onchange")
    status = fields.Selection(
        string="Status",
        selection=[
            ('Draft', 'Draft'),
            ('Pending', 'Pending Approval'),
            ('Approved', 'Approved')], default='Draft')

    def name_get(self):
        result = []
        for record in self:
            name = "{0} {1} :: {2}".format(record.course_id.code, record.score, record.grade_id.name)
            result.append((record.id, name))
        return result

    def write(self, vals):
        if 'score' in vals or 'ca_score' in vals or 'test_score' in vals or 'practicals_score' in vals or 'status' in vals:
            if self.status == "Draft":
                vals['status'] = 'Pending'
            else:
                points = self.grade_id.point * self.units
                vals['points_obtained'] = points

        return super(StudentResultBookEntry, self).write(vals)

    @api.constrains('practicals_score', 'test_score', 'ca_score')
    def _check_score_lesser_than_100(self):
        for record in self:
            if record.score > 100:
                raise exceptions.ValidationError('Total Score cannot be greater than 100')

    @api.constrains('practicals_score')
    def _check_practicals_score_lesser_zero(self):
        for record in self:
            if record.practicals_score < 0:
                raise exceptions.ValidationError('Practical Score cannot be lesser than 0')

    @api.constrains('practicals_score')
    def _check_practicals_score_lesser_zero(self):
        for record in self:
            if record.practicals_score < 0:
                raise exceptions.ValidationError('Practical Score cannot be lesser than 0')

    @api.constrains('test_score')
    def _check_test_score_lesser_zero(self):
        for record in self:
            if record.test_score < 0:
                raise exceptions.ValidationError('Test Score cannot be lesser than 0')

    @api.constrains('score')
    def _check_score(self):
        for record in self:
            if record.score > 100:
                raise exceptions.ValidationError('Score cannot be greater than 100')

    @api.depends('ca_score', 'practicals_score', 'test_score')
    def _compute_grade(self):
        for record in self:
            grading_scheme = record.school_id.grading_scheme_id
            total_score = record.ca_score + record.practicals_score + record.test_score
            record.grade_id = grading_scheme.get_grade(total_score)

    @api.depends('ca_score', 'practicals_score', 'test_score')
    def _compute_is_pass_mark(self):
        for record in self:
            grading_scheme = record.school_id.grading_scheme_id
            total_score = record.ca_score + record.practicals_score + record.test_score
            grade_id = grading_scheme.get_grade(total_score)
            grade = self.env['quickgrades.grade'].browse(grade_id)
            record.is_pass_mark = grade.is_pass_mark

    @api.depends('ca_score', 'practicals_score', 'test_score')
    def _compute_total_score(self):
        for record in self:
            total_score = record.ca_score + record.practicals_score + record.test_score
            record.score = total_score
