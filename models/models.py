# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, tools, exceptions
from odoo.modules.module import get_module_resource
import logging

_logger = logging.getLogger(__name__)


class Semester(models.Model):
    """ Defining an academic year """
    _name = "quickgrades.semester"
    _description = "Semester"
    _order = "sequence asc"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', size=64, required=True, index=1, help='Name')
    code = fields.Char('Code', required=True, index=1, help='Code')


class Department(models.Model):
    _name = "quickgrades.department"
    _description = "Department"
    _order = 'name'

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=64, required=True)
    previous_code = fields.Char('Previous Code', size=64, required=False)
    faculty_id = fields.Many2one('quickgrades.faculty', 'Faculty', required=True)
    diploma_ids = fields.Many2many(comodel_name='quickgrades.diploma', string='Degrees')
    student_ids = fields.One2many('quickgrades.student', 'department_id', 'Student', readonly=True)
    programme_ids = fields.One2many('quickgrades.programme', 'department_id', 'Programmes', readonly=True)


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


class Faculty(models.Model):
    _name = "quickgrades.faculty"
    _description = "Faculty"
    _order = "name"

    school_id = fields.Many2one('quickgrades.school', "School")
    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    department_ids = fields.One2many('quickgrades.department', 'faculty_id', 'Add Department')
    programme_ids = fields.One2many('quickgrades.programme', 'faculty_id', 'Programmes')


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


class AcademicLevel(models.Model):
    """ Defining Level Information """
    _description = 'Academic Level Information'
    _name = 'quickgrades.level'
    _order = "name"

    sequence = fields.Integer('Sequence', default=1, required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=20, required=True)
    next_class_id = fields.Many2one('quickgrades.level', "Next Class")
    previous_class_id = fields.Many2one('quickgrades.level', "Previous Class")
    diploma_id = fields.Many2one('quickgrades.diploma', "Degree", required=True)
    description = fields.Text('Description')


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


class Student(models.Model):
    """Defining a subject """
    _name = "quickgrades.student"
    _description = "Students"

    name = fields.Char('Name', size=128, required=True)
    matriculation_number = fields.Char('Registration. No', size=64, help='Registration No.', required=True)
    application_number = fields.Char('Application. No', size=64, help='Application No.')
    image = fields.Binary(
        "Photograph", attachment=True,
        help="This field holds the image used as photo for the student, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the student. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the student. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    programme_id = fields.Many2one('quickgrades.programme', "Programme", required=True)
    department_id = fields.Many2one(related='programme_id.department_id', store=True, readonly=True,
                                    string="Department")
    diploma_id = fields.Many2one(related='programme_id.diploma_id', string="Degree", store=True, readonly=True)
    school_id = fields.Many2one('quickgrades.school', 'School')
    result_book_ids = fields.One2many('student.result', 'student_id', 'Result Book', readonly=True)
    result_ids = fields.One2many('student.result.entry', 'student_id', 'Results')
    approved_result_ids = fields.One2many('student.result.entry', string='Approved Results',
                                          compute='_compute_approved_results', readonly=True)
    
    _sql_constraints = [
        ('student_registration_uniq',
         'UNIQUE (matriculation_number)',
         'Student Registration number already exist!')]


    def _create_student_result(self, student):
        StudentResultBook = self.env['student.result']
        vals = {}
        vals['student_id'] = student.id
        vals['programme_id'] = student.programme_id.id
        result_book = StudentResultBook.create(vals)
        student.write({'result_book_ids': [(4, result_book.id)]})

        return True

    def write(self, vals):
        # tools.image_resize_images(vals)
        return super(Student, self).write(vals)

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['name']).title()
        new_record = super(Student, self).create(vals)
        self._create_student_result(new_record)
        return new_record

    def name_get(self):
        result = []
        for record in self:
            name = "{0} {1}".format(record.matriculation_number, record.name)
            result.append((record.id, name))
        return result

    def _compute_approved_results(self):
        for record in self:
            record.approved_result_ids = record.mapped('result_ids').filtered(
                lambda result: result.status == 'Approved')


class Honour(models.Model):
    _name = 'quickgrades.honour'
    _description = 'Academic Honors'

    name = fields.Char('Honour', size=64, required=True)
    description = fields.Char('Description', size=250)
    upper_bound = fields.Float('To', required=True)
    lower_bound = fields.Float('From', required=True)
    honour_scheme_id = fields.Many2one('quickgrades.honour.scheme', 'Honour Scheme')

    @api.model
    def _compute_gpa(self, results):
        """ This will calculates the cumulative grade point average(CGPA) given a domain"""
        approved_results = results.filtered(lambda r: r.status == 'Approved')
        total_credits = sum([result.units for result in approved_results])
        total_points = sum([result.points * result.units for result in approved_results])
        if total_points:
            cgpa_in_str = str(total_points / total_credits)
            cgpa_in_float = float(cgpa_in_str[0:4])
            return cgpa_in_float
        else:
            return 0.00


class Diploma(models.Model):
    _name = 'quickgrades.diploma'
    _description = "Degree"
    _order = 'name desc'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(size=130, string='Description')
    department_ids = fields.Many2many(comodel_name='quickgrades.department', string='Departments')


class GradingScheme(models.Model):
    _name = 'quickgrades.grading.scheme'
    _description = 'Academic Grading Scheme'

    name = fields.Char('Name', size=64, required=True)
    description = fields.Text('Description')
    grading_ids = fields.One2many('quickgrades.grade', 'grading_scheme_id', 'Gradings')

    def get_grade(self, score):
        res = 0
        for scheme in self:
            for grade in scheme.grading_ids:
                if grade.min_grade <= score <= grade.max_grade:
                    res = grade.id
                    break
        return res


class HonourScheme(models.Model):
    _name = 'quickgrades.honour.scheme'
    _description = 'Academic Honors Scheme'
    name = fields.Char('Grade', size=128, required=True)
    description = fields.Text('Description')
    options = fields.Selection(string="Options",
                               selection=[
                                   ('allow_grade_replacement',
                                    'Allow Grades Replacement'),
                                   ('no_allow_replacement',
                                    'No Grades Replacement'),
                               ])
    honour_ids = fields.One2many(
        'quickgrades.honour', 'honour_scheme_id', 'Honour Scheme')


class Grade(models.Model):
    _name = 'quickgrades.grade'
    _description = 'Academic Grade'
    _order = 'name asc'

    name = fields.Char('Grade', size=64, required=True)
    point = fields.Float(required=True)
    description = fields.Char('Description', size=250)
    min_grade = fields.Float('Lower Bound', required=True)
    max_grade = fields.Float('Upper Bound', required=True)
    is_pass_mark = fields.Boolean('Is Pass Mark?')
    grading_scheme_id = fields.Many2one('quickgrades.grading.scheme', 'Grading Scheme')


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
    option_id = fields.Many2one('quickgrades.programme.option', 'Option', required=False)

    def name_get(self):
        result = []
        for record in self:
            name = "{0}".format(record.code)
            result.append((record.id, name))
        return result


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
            for failed_course in failed_courses:
                 if failed_course.id not in passed_courses.ids:
                    res.append(failed_course.id)

            record.outstanding_result_ids = res

    @api.depends('entry_ids')
    def _compute_outstanding_courses(self):
        for record in self:
            record.outstanding_course_ids = [entry.course_id.id for entry in record.outstanding_result_ids]
    
    @api.depends('entry_ids')
    def _compute_approved_results(self):
        for record in self:
            record.approved_result_ids = record.mapped('entry_ids').filtered(
            lambda result: result.status == 'Approved')

    def _compute_cgpa(self):
        """ This will calculates the cumulative grade point average(CGPA) given a domain"""
        for record in self:
            approved_results = record.entry_ids.filtered(lambda r: r.status == 'Approved')
            cgpa = self.env['academic.honour'].compute_gpa(approved_results)

            return cgpa
        
    def action_recompute_cgpa(self):
        for record in self:
            if record.entry_ids:
                cgpa = record._compute_cgpa()
                record.write({'cgpa': cgpa})
                _logger.debug("Updating Student CGPA for {} ... {} to {}".format(record.student_id.matriculation_number,
                                                                                 record.cgpa, cgpa))
                record._compute_honour()
                    
    @api.model
    def write(self, values):
        # Add code here
        if values.get('entry_ids', False):
            self.action_recompute_cgpa()
        return super(StudentResultBook, self).write(values)
    
    @api.depends('cgpa')
    def _compute_honour(self):
        for record in self:
            if record.cgpa > 0.00:
                honours = self.env['academic.honour'].search([])
                honour = honours.filtered(lambda h: h.lower_bound <= record.cgpa <= h.upper_bound)
                record.honours_id = honour[0]
                
    def name_get(self):
        result = []
        for record in self:
            name = "{0} - {1} Results".format(record.student_id.matriculation_number, record.student_id.name)
            result.append((record.id, name))
        return result


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


class State(models.Model):
    _description = "State"
    _name = 'academic.state'
    _order = 'name'

    lga_ids = fields.One2many('state.lga', 'state_id', 'LGAs')
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=False)
    country_id = fields.Many2one('res.country', 'Country')


class StateLga(models.Model):
    _description = "LGA"
    _name = 'state.lga'
    _order = 'name'

    state_id = fields.Many2one('academic.state', 'State', required=True)
    name = fields.Char('Local Government Area', size=64, required=True)


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
