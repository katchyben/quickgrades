# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, tools, exceptions
from odoo.modules.module import get_module_resource
import logging
import re

_logger = logging.getLogger(__name__)


class Semester(models.Model):
    """ Defining an academic year """
    _name = "quickgrades.semester"
    _description = "Semester"
    _order = "sequence asc"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', size=64, required=True, index=1, help='Name')
    code = fields.Char('Code', required=True, index=1, help='Code')
    
    
class EntryStatus(models.Model):
    """ Defining an academic year """
    _name = "quickgrades.entry.status"
    _description = "Entry Status"
    _order = "name asc"

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', required=True)


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
    position_ids = fields.One2many('quickgrades.position', 'department_id', 'Positions')


class Programme(models.Model):
    _name = "quickgrades.programme"
    _description = "Academic Programme"
    _order = 'department_id asc'
    
    @api.model
    def _get_default_status(self):
        return self.env['quickgrades.entry.status'].search([('name', '=', 'UME')], limit=1)

    name = fields.Char(compute='_compute_name', string="Name", store=True)
    department_id = fields.Many2one('quickgrades.department', 'Department', required=True)
    faculty_id = fields.Many2one('quickgrades.faculty', 'Faculty', required=True)
    diploma_id = fields.Many2one('quickgrades.diploma', 'Degree', required=True)
    course_ids = fields.One2many('programme.course.entry', 'programme_id', 'Courses')
    school_id = fields.Many2one(related='faculty_id.school_id', readonly=True, store=True)
    entry_status_id = fields.Many2one('quickgrades.entry.status', 'Entry Status', default=_get_default_status)
   
    @api.depends('department_id', 'diploma_id')
    def _compute_name(self):
        for record in self:
            if record.entry_status_id and record.entry_status_id.code == "CEP":
                record.name = "{0} {1} {2}".format(record.diploma_id.code, 
                                                   record.department_id.name, record.entry_status_id.code )
            else:
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
    type_id = fields.Many2one('quickgrades.diploma.type', "Degree Type", required=True)
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
    phone = fields.Char('Phone Number', size=64)
    email = fields.Char('Email', size=32)
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
    entry_status_id = fields.Many2one(related='programme_id.entry_status_id', store=True, readonly=True,
                                    string="Entry Status")
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
        vals = {'student_id': student.id, 'programme_id': student.programme_id.id}
        result_book = StudentResultBook.create(vals)
        return result_book

    def write(self, vals):
        return super(Student, self).write(vals)

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['name']).title()
        new_record = super(Student, self).create(vals)
        result_book = self._create_student_result(new_record)
        new_record.write({'result_book_ids': [(4, result_book.id)]})
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
    def compute_gpa(self, results):
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
    type_id = fields.Many2one('quickgrades.diploma.type', 'Degree Type', required=True)


class DiplomaType(models.Model):
    _name = 'quickgrades.diploma.type'
    _description = "Degree Type"
    _order = 'name desc'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(size=130, string='Description')
    diploma_ids = fields.One2many('quickgrades.diploma', 'type_id', 'Degrees')


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


class AcademicProgrammeOption(models.Model):
    _name = "quickgrades.programme.option"
    _description = "Programme Option"
    _order = 'name asc'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    programme_id = fields.Many2one('quickgrades.programme', string='Programme', required=True)


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
    lecturer_ids = fields.Many2many(comodel_name='quickgrades.lecturer', string='Lecturers')

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
    _order = 'student_id,programme_id'
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('student_result_book_uniq',
         'UNIQUE (student_id)',
         'Student can only have one Result Book!')]

    student_id = fields.Many2one('quickgrades.student', 'Student', required=True)
    programme_id = fields.Many2one(related='student_id.programme_id', string='Programme', store=True)
    entry_ids = fields.One2many(comodel_name='student.result.entry', inverse_name='student_result_id', string='Entries',
                                required=False, track_visibility="always")
    outstanding_result_ids = fields.Many2many(comodel_name='student.result.entry',
                                              compute='_compute_outstanding_results', string="Outstanding Results",
                                              readonly=True)
    outstanding_course_ids = fields.Many2many(comodel_name='programme.course.entry',
                                              compute='_compute_outstanding_courses', string="Outstanding Courses",
                                              readonly=True)
    cgpa = fields.Float(string="CGPA", readonly=True, track_visibility="always")
    honours_id = fields.Many2one(comodel_name='quickgrades.honour', compute='_compute_honour', readonly=True,
                                 store=True,
                                 string="Honours", track_visibility="always")
    approved_result_ids = fields.One2many('student.result.entry', string='Approved Results',
                                          compute='_compute_approved_results', readonly=True)
    registration_id = fields.Many2one('student.registration', 'Registration')

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
            record.approved_result_ids = record.mapped('entry_ids').filtered(lambda result: result.status == 'Approved')

    def compute_cgpa(self):
        """ This will calculates the cumulative grade point average(CGPA) given a domain"""
        for record in self:
            approved_results = record.entry_ids.filtered(lambda r: r.status == 'Approved')
            cgpa = self.env['quickgrades.honour'].compute_gpa(approved_results)

            return cgpa

    def action_recompute_cgpa(self):
        for record in self:
            if record.entry_ids:
                cgpa = record.compute_cgpa()
                record.write({'cgpa': cgpa})
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
                honours = self.env['quickgrades.honour'].search([])
                honour = honours.filtered(lambda h: h.lower_bound <= record.cgpa <= h.upper_bound)
                record.honours_id = honour[0]

    def name_get(self):
        result = []
        for record in self:
            name = "{0} - {1} Results".format(record.student_id.matriculation_number, record.student_id.name)
            result.append((record.id, name))
        return result


class StudentRegistrationEntry(models.Model):
    _description = 'Student Course Registration Entry'
    _name = 'student.registration.entry'
    _order = 'level_id,semester_id'

    _sql_constraints = [
        ('registration_entry_course_uniq',
         'UNIQUE (student_id, course_id, session_id)',
         'Student, Course and Session must be unique!')]

    registration_id = fields.Many2one('student.registration', 'Registration', required=True, ondelete='cascade')
    student_id = fields.Many2one(related='registration_id.student_id', string='Student', store=True, readonly=True)
    programme_id = fields.Many2one(related='registration_id.programme_id', string='Programme', store=True,
                                   readonly=True)
    level_id = fields.Many2one(related='course_id.level_id', string='Level', store=True, readonly=True)
    session_id = fields.Many2one(related='registration_id.session_id', string='Session', store=True, readonly=True)
    course_id = fields.Many2one('programme.course.entry', 'Course', required=True, ondelete='cascade')
    units = fields.Integer(related='course_id.units', string='Units', readonly=True)
    code = fields.Char(related='course_id.code', string='Code', readonly=True)
    name = fields.Char(related='course_id.name', string='Name', readonly=True)
    semester_id = fields.Many2one(related='course_id.semester_id', string='Semester', readonly=True, store=True, )
    is_brought_forward = fields.Boolean('Brought Forward')

    def unlink(self):
        domain = [('registration_id', '=', self.registration_id.id), ('course_id', '=', self.course_id.id)]
        resultEntry = self.env['student.result.entry'].search(domain)
        resultEntry.unlink()
        result = super(StudentRegistrationEntry, self).unlink()

        return result


class StudentRegistration(models.Model):
    _description = 'Student Registration'
    _name = 'student.registration'
    _inherit = ["mail.thread"]
    _rec_name = 'student_id'

    _sql_constraints = [
        ('registration_course_uniq',
         'UNIQUE (student_id, session_id, semester_id)',
         'Student can only register once!')]

    @api.model
    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    entry_date = fields.Date('Date', required=True, default=_get_default_date)
    student_id = fields.Many2one('quickgrades.student', 'Student', required=True)
    matriculation_number = fields.Char(related="student_id.matriculation_number", readonly=True, store=True)
    level_id = fields.Many2one('quickgrades.level', 'Level', required=True)
    session_id = fields.Many2one('academic.session', 'Session', required=True)
    semester_id = fields.Many2one('quickgrades.semester', 'Semester', required=True)
    programme_id = fields.Many2one('quickgrades.programme', string="Programme", required=True)
    diploma_id = fields.Many2one(related='programme_id.diploma_id', string="Diploma", store=True, readonly=True)
    total_credit_units = fields.Float(compute='_compute_total_credit_units', store=True)
    state = fields.Selection(string="Status",
                             selection=[
                                 ('New', 'New'),
                                 ('Approved', 'Approved'),
                                 ('Closed', 'Closed')
                             ], default='New', track_visibility="onchange", )
    entry_ids = fields.One2many('student.registration.entry', 'registration_id', 'Courses')
    entry_current_ids = fields.Many2many(comodel_name='student.registration.entry',
                                         compute='_compute_current_courses', string="Current Courses Forward",
                                         readonly=True)
    entry_brought_forward_ids = fields.Many2many(comodel_name='student.registration.entry',
                                                 compute='_compute_courses_brought_forward',
                                                 string="Courses Brought Forward", readonly=True)
    result_ids = fields.One2many('student.result.entry', 'registration_id', 'Results')
    gpa = fields.Float(string="Semester GPA", readonly=True, track_visibility="onchange")
    approved_result_ids = fields.One2many('student.result.entry', string='Approved Results',
                                          compute='_compute_approved_results', readonly=True)

    def _compute_approved_results(self):
        for record in self:
            record.approved_result_ids = record.mapped('result_ids').filtered(
                lambda result: result.status == 'Approved')

    def action_recompute_cgpa(self):
        for record in self:
            if record.result_ids:
                approved_results = record.approved_result_ids
                gpa = self.env['quickgrades.honour'].compute_gpa(approved_results)
                record.write({'gpa': gpa})

    def action_approve_registration(self):
        self.write({'state': 'Approved'})

    def action_close_registration(self):
        results = self.result_ids.filtered(lambda r: r.status == 'Approved')
        gpa = self.env['quickgrades.honour'].compute_gpa(results)
        self.write({'state': 'Closed', 'gpa': gpa})

    @api.depends('result_ids')
    def _compute_results(self):
        for record in self:
            if record.entry_ids:
                results = self.env["student.result.entry"].search([("session_id", "=", record.session_id.id),
                                                                   ("student_id", "=", record.student_id.id),
                                                                   ("semester_id", "=", record.semester_id.id)])
                record.result_ids = results
    
    @api.depends('entry_ids')         
    def _compute_total_credit_units(self):
         for record in self:
                if record.entry_ids:
                    record.total_credit_units = sum([entry.units for entry in record.entry_ids])

    def name_get(self):
        result = []
        for record in self:
            name = "{0} - {1}".format(record.student_id.matriculation_number, record.student_id.name)
            result.append((record.id, name))
        return result

    @api.depends('entry_ids')
    def _compute_courses_brought_forward(self):
        for record in self:
            record.entry_brought_forward_ids = record.entry_ids.filtered(lambda c: c.is_brought_forward == True)

    @api.depends('entry_ids')
    def _compute_current_courses(self):
        for record in self:
            record.entry_current_ids = record.entry_ids.filtered(lambda c: c.is_brought_forward == False)

    def get_result_for_course(self, course_id, ):
        return self.env['student.result.entry'].search([('student_id', '=', self.student_id.id),
                                                        ('course_id', '=', course_id),
                                                        ('semester_id', '=', self.semester_id.id),
                                                        ('session_id', '=', self.session_id.id)])

    def add_student_result_entry(self, student_result, course_id, scores):
        entry = self.get_result_for_course(course_id)
        if entry:
            entry.write({'ca_score': scores.get('exam', 0.00),
                         'practicals_score': scores.get('practicals', 0.00),
                         'test_score': scores.get('test', 0.00)})
        else:
            vals = {'student_result_id': student_result.id,
                    'student_id': self.student_id.id,
                    'course_id': course_id,
                    'semester_id': self.semester_id.id,
                    'level_id': self.level_id.id,
                    'session_id': self.session_id.id,
                    'registration_id': self.id,
                    'ca_score': scores.get('exam', 0.00),
                    'practicals_score': scores.get('practicals', 0.00),
                    'test_score': scores.get('test', 0.00),
                    'status': 'Approved'}
            entry = self.env['student.result.entry'].create(vals)
            # Adds result to Student Results Collection
            self.student_id.write({'result_ids': [(4, entry.id)]})
        return entry

    def _create_student_result_entries(self, student_result):
        vals = {}
        programme_id = self.programme_id.id
        semester_id = self.semester_id.id
        session_id = self.session_id.id
        level_id = self.level_id.id
        student = self.env['quickgrades.student'].browse(student_result.student_id.id)
        # option_id = student.option_id.id if student.option_id else None
        courses = self._get_courses(programme_id, level_id, semester_id)
        _logger.info("Courses for the Semester ::: {}".format(courses))
        for course in courses:
            vals['student_result_id'] = student_result.id
            vals['student_id'] = student.id
            vals['course_id'] = course.id
            vals['semester_id'] = semester_id
            vals['level_id'] = level_id
            vals['session_id'] = session_id
            vals['registration_id'] = self.id

            entry = self.env['student.result.entry'].create(vals)
            # Adds result to Student Results Collection
            student.write({'result_ids': [(4, entry.id)]})

        return True

    def _create_course_entries(self):
        level_id = self.level_id.id
        semester_id = self.semester_id.id
        programme_id = self.programme_id.id
        student_id = self.student_id.id
        #  option_id = registration.student_id.option_id.id if registration.student_id.option_id else None
        courses = self._get_courses(programme_id, level_id, semester_id)
        outstanding_course_ids = self._get_outstanding_courses(student_id, semester_id)

        for course in courses:
            StudentRegistrationEntry.create({'registration_id': self.id, 'course_id': course.id})

        for course_id in outstanding_course_ids:
            self.env['student.registration.entry'].create({'registration_id': self.id,
                                                           'course_id': course_id, 'is_brought_forward': True})
        return True

    def get_course_entry(self, course_id, ):
        return self.env['student.registration.entry'].search([('registration_id', '=', self.id),
                                                              ('course_id', '=', course_id)])

    def add_course_entry(self, course_id, is_brought_forward=False):
        entry = self.get_course_entry(course_id)
        if entry:
            return entry
        else:
            return self.env['student.registration.entry'].create({'registration_id': self.id,
                                                                  'course_id': course_id,
                                                                  'is_brought_forward': is_brought_forward})

    def _get_courses(self, programme_id, level_id, semester_id):
        courses = []
        domain = [('level_id', '=', level_id), ('semester_id', '=', semester_id), ('programme_id', '=', programme_id)]
        all_courses = self.env['programme.course.entry'].search(domain)
        _logger.info("All available courses {}".format(all_courses))
        # programme = self.env['academic.programme'].browse(programme_id)
        for course in all_courses:  # programme.course_ids.filtered(lambda c: c.semester_id.id == semester_id and c.level_id.id == level_id):
            courses.append(course)
        return courses

    def _get_outstanding_courses(self, student_id, semester_id):
        results = self.env['student.result'].search([('student_id', '=', student_id)])
        return results.outstanding_course_ids.filtered(lambda c: c.semester_id.id == semester_id).ids

    @api.model
    def create(self, vals):
        is_legacy = False
        if vals.get('is_legacy', False):
            is_legacy = True
            vals.pop('is_legacy')
        registration = super(StudentRegistration, self).create(vals)
        student_result = self.env['student.result'].browse(vals['student_id'])
        if is_legacy:
            return registration
        else:
            self._create_student_result_entries(student_result)
            self._create_course_entries()
        return registration

    def write(self, vals):
        result = super(StudentRegistration, self).write(vals)
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
    semester_id = fields.Many2one(comodel_name='quickgrades.semester', string='Semester', readonly=True)
    course_id = fields.Many2one(comodel_name='programme.course.entry', string='Course', readonly=True)
    level_id = fields.Many2one(comodel_name='quickgrades.level', string='Level', readonly=True)
    course_name = fields.Char(related="course_id.name", string='Course Name', readonly=True, store=True)
    course_code = fields.Char(related="course_id.code", string='Course Code', readonly=True, store=True)
    units = fields.Integer(related='course_id.units', string='Units', readonly=True, store=True)
    remarks = fields.Text('Remarks', track_visibility="all")
    gpa = fields.Float("GPA", compute='_compute_gpa',  store=True)
    ca_score = fields.Float('Examination Score', track_visibility="onchange")
    test_score = fields.Float('Test Score', track_visibility="onchange")
    points = fields.Float(related="grade_id.point", string='Points', readonly=True, store=True)
    points_obtained = fields.Float(string='Points Obtained', readonly=True, compute='_compute_points_obtained',
                                   store=True)
    practicals_score = fields.Float('Practicals Score', track_visibility="onchange")
    score = fields.Float(compute='_compute_total_score', string="Total", store=True, readonly=True,
                         track_visibility="onchange")
    grade_id = fields.Many2one(comodel_name='quickgrades.grade', compute='_compute_grade',
                               string="Grade", readonly=True, store=True, track_visibility="onchange")
    school_id = fields.Many2one('quickgrades.school', 'School', default=_default_school)
    is_pass_mark = fields.Boolean(compute='_compute_is_pass_mark', string="Is Pass Mark?", store=True, readonly=True,
                                  track_visibility="onchange")
    registration_id = fields.Many2one('student.registration', 'Registration')
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
    def _compute_points_obtained(self):
        for record in self:
            if record.grade_id:
                record.points_obtained = record.grade_id.point * record.units

    @api.depends('ca_score', 'practicals_score', 'test_score')
    def _compute_total_score(self):
        for record in self:
            total_score = record.ca_score + record.practicals_score + record.test_score
            record.score = total_score
            
    @api.depends('registration_id.entry_ids')
    def _compute_gpa(self):
        for record in self:
            if record.registration_id and record.registration_id.entry_ids:
                record.gpa = record.points_obtained/record.registration_id.total_credit_units
  
            
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

    def _check_if_result_exist(self, student_id, course_id, session_id):
        domain = [('session_id', '=', session_id), ('student_id', '=', student_id), ('course_id', '=', course_id)]
        result = self.env['student.result.entry'].search_count(domain)
        return result > 0

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

        vals['level'] = str(vals["level"]).strip().replace(" ", "")

        return super(LegacyStudentResult, self).create(vals)

    def create_registration_record(self, student, session_id, level_id, semester_id):
        vals = {'programme_id': student.programme_id.id,
                'student_id': student.id,
                'session_id': session_id,
                'level_id': level_id,
                'is_legacy': True,
                'semester_id': semester_id}
        registration = self.env['student.registration'].create(vals)

        return registration

    def check_registration_record(self, student_id, session_id, semester_id):
        registration = self.env['student.registration'].search(
            [('session_id', '=', session_id), ('student_id', '=', student_id), ('semester_id', '=', semester_id)])
        return registration

    def update_result_record(self, student_id, course_id, session_id):
        domain = [('student_id', '=', student_id), ('session_id', '=', session_id),
                  ('course_id', '=', course_id)]
        result = self.env['student.result.entry'].search(domain)
        _logger.info("Executing update_result_record {} ".format(result))
        if result:
            _logger.info("Updating Result {}".format(result))
            vals = {'status': 'Approved', 'ca_score': self.exam, 'test_score': self.test,
                    'practicals_score': self.practicals}
            result.write(vals)
            _logger.info("Result updated to {}".format(result))

    def action_process(self):
        for record in self:
            if record.status == "Processed":
                return True
            else:
                try:
                    student = self.env['quickgrades.student'].search([('matriculation_number', '=', record.matric)])
                    if not student:
                        raise ValueError("Student with the matric number {} was not found".format(record.matric))

                    session = self.env['academic.session'].search([('code', '=', record.session)])
                    if not session:
                        raise ValueError("Invalid Academic Session {}".format(record.session))

                    course = self.env['programme.course.entry'].search(
                        [('code', '=', record.course), ('programme_id', '=', student.programme_id.id)], limit=1)
                    if not course:
                        raise ValueError("{} was not found for {}".format(record.course, student.programme_id.name))

                    level = self.env['quickgrades.level'].search(
                        ["|", ('code', '=', record.level), ('name', '=', record.level)])
                    if not level:
                        raise ValueError("Invalid Level {}".format(record.level))

                    semester = self.env['quickgrades.semester'].search(
                        ["|", ('code', '=', record.semester), ('code', "=", record.semester.lower())])
                    if not semester:
                        raise ValueError("Invalid Semester code {}".format(record.semester))

                    # If already processed skip, handles duplicates
                    # if course and self._check_if_result_exist(student.id, course.id, session.id):
                    #    record.write({'status': 'Processed'})
                    #    return True

                    result_book = self.env['student.result'].search([('student_id', '=', student.id)])
                    registration = record.check_registration_record(student.id, session.id, semester.id)
                    registration = registration if registration else record.create_registration_record(student,
                                                                                                       session.id,
                                                                                                       level.id,
                                                                                                       semester.id)
                    registration.add_course_entry(course.id, False)
                    scores = {'exam': record.exam, 'practicals': record.practicals, 'test': record.test}
                    registration.add_student_result_entry(result_book, course.id, scores)
                    registration.action_recompute_cgpa()
                    result_book.action_recompute_cgpa()

                except ValueError as e:
                    return record.write({'status': 'Failed', 'remarks': e})

                except Exception as e:
                    return record.write({'status': 'Failed', 'remarks': e})

                return record.write({'status': 'Processed', 'remarks': 'Processed Successfully'})


class LegacyStudent(models.Model):
    """ Defining Template For Student Import"""
    _name = "academic.legacy.student"
    _description = "Legacy Student"
    _order = "matric asc"

    name = fields.Char('Name', size=128, required=True)
    matric = fields.Char('Registration. No', required=True, index=1, help='matric')
    application_number = fields.Char('Application. No', size=64, help='Application No.')
    phone = fields.Char('Phone Number', size=64)
    email = fields.Char('Email', size=32)
    level = fields.Char('Level', required=True)
    dept = fields.Char('Dept', required=True)
    status = fields.Selection(
        string='Status',
        selection=[('New', 'New'), ('Failed', 'Failed'), ('Processed', 'Processed')],
        default='New',
        readonly=True
    )
    remarks = fields.Char('Remarks')


    # NAU/2001/484557
    def _get_admission_year(self):
        parts = str(self.matric).split("/")
        if parts and len(parts) > 1:
            try:
                return int(parts[1])
            except Exception:
                raise ValueError("Invalid Registration Number {}".format(self.matric))
        else:
            raise ValueError("Invalid Registration Number {}".format(self.matric))

    def action_process(self):
        for record in self:
            if record.status == "Processed":
                return True
            else:
                try:
                    vals = {'matriculation_number': record.matric}
                    admission_year = self._get_admission_year()
                    admission_year_upper_bound = int(admission_year) + 1
                    code = str(admission_year) + "/" + str(admission_year_upper_bound)
                    session = self.env['academic.session'].search([('code', '=', code)])

                    if session:
                        vals['admission_year_id'] = session.id
                    else:
                        raise ValueError("Invalid Registration number {}".format(record.matric))
                    if record.phone:
                        vals['phone'] = "0" + record.phone

                    level = self.env['quickgrades.level'].search([('code', '=', record.level)])
                    if not level:
                        raise ValueError("Invalid Level {}".format(record.level))

                    diploma_id = level.diploma_id.id
                    dept = self.env['quickgrades.department'].search(
                        ['|', ('code', '=', record.dept), ('previous_code', '=', record.dept)])

                    if not dept:
                        raise ValueError("Invalid Department Code {}".format(record.dept))
                    programme = self.env['quickgrades.programme'].search([('department_id', '=', dept.id),
                                                                          ('diploma_id', '=', diploma_id)])
                    if not programme:
                        raise ValueError("Invalid Programme {} {} ".format(diploma_id.code, dept.name))

                    vals['level_id'] = level.id
                    vals['programme_id'] = programme.id

                    # Searches to see if the record already exists
                    student = self.env['quickgrades.student'].search(
                        [('matriculation_number', '=', vals['matriculation_number'])])
                    if student:
                        self.write({'status': 'Processed', 'remarks': 'Processed Successfully'})
                        _logger.info("{} already exists".format(vals['matriculation_number']))
                        return True
                    else:
                        self.env['quickgrades.student'].create(vals)

                except ValueError as v:
                    # _logger.info(v)
                    self.write({'status': 'Failed', 'remarks': v})
                    return False

                except Exception as e:
                    # _logger.info(e)
                    self.write({'status': 'Failed', 'remarks': e})
                    return False

                self.write({'status': 'Processed', 'remarks': 'Processed Successfully'})
                return True


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
    remarks = fields.Char('Remarks')


    def partition(self, data):
        if " " in data:
            return data
        else:
            parts = re.split('(\d.*)', data)
            return "{} {}".format(parts[0], parts[1])

    def create_course_record(self, diploma_id, code, name, semester_id):
        vals = {'name': name, 'code': code, 'semester_id': semester_id, 'diploma_id': diploma_id}
        course = self.env['programme.course'].create(vals)
        return course

    def create_course_entry_record(self, course_id, units, programme_id, level_id, option):
        vals = {}
        if option:
            optionObj = self.env['quickgrades.programme.option'].search(
                [('name', '=ilike', option), ('programme_id', '=', programme_id)])
            vals['option_id'] = optionObj.id

        vals['course_id'] = course_id
        vals['units'] = units
        vals['programme_id'] = programme_id
        vals['level_id'] = level_id
        course_entry = self.env['programme.course.entry'].create(vals)

        return course_entry

    def check_for_course_record(self, code):
        course = self.env['programme.course'].search([('code', '=', code)])
        return course

    def check_if_course_entry_exist(self, course_id, programme_id, option):
        domain = [('course_id', '=', course_id), ('programme_id', '=', programme_id)]
        if option:
            optionObj = self.env['quickgrades.programme.option'].search(
                [('name', '=ilike', option), ('programme_id', '=', programme_id)])
            domain = [('course_id', '=', course_id), ('programme_id', '=', programme_id),
                      ('option_id', '=', optionObj.id)]

        course = self.env['programme.course.entry'].search_count(domain)
        return course > 0

    def action_process(self):
        for record in self:
            if record.status == "Processed":
                return True
            else:
                try:
                    programme = self.env["quickgrades.programme"].search([("name", '=ilike', record.programme)])
                    if not programme:
                        raise ValueError("Invalid Programme {}".format(record.programme))
                    level = self.env["quickgrades.level"].search([("code", '=', record.level)])
                    if not level:
                        raise ValueError("Invalid Level {}".format(record.level))
                    semester = self.env["quickgrades.semester"].search([("code", '=', record.semester)])
                    if not semester:
                        raise ValueError("Invalid Semester {}".format(record.semester))
                    diploma_id = programme.diploma_id.id
                    course = record.check_for_course_record(record.code)
                    if course:
                        course_entry = record.check_if_course_entry_exist(course.id, programme.id, record.option)
                        if not course_entry:
                            record.create_course_entry_record(course.id, record.units,
                                                              programme.id, level.id, record.option)
                        else:
                            raise ValueError("{} already exist for {}".format(course.code, programme.name))
                    else:
                        course = record.create_course_record(diploma_id, record.code, record.title, semester.id)
                        course_entry = record.check_if_course_entry_exist(course.id, programme.id, record.option)
                        if not course_entry:
                            record.create_course_entry_record(course.id, record.units, programme.id,
                                                              level.id, record.option)
                        else:
                            raise ValueError("{} already exist for {}".format(course.code, programme.name))

                except ValueError as e:
                    record.write({'status': "Failed", 'remarks': e})
                    return False
                except Exception as e:
                    record.write({'status': "Failed", 'remarks': e})
                    return False
                record.write({'status': "Processed", 'remarks': "Successfully"})
                return True

    @api.model
    def create(self, vals):
        vals['title'] = str(vals["title"]).strip().title()
        vals['code'] = self.partition(str(vals["code"]).strip().replace("  ", " "))
        vals['level'] = str(vals["level"]).strip().replace(" ", "")
        if vals['option']:
            vals['option'] = str(vals["option"]).strip()
        vals['programme'] = str(vals["programme"]).strip().replace("  ", " ")

        return super(SchoolCourse, self).create(vals)


class AutoJobScheduler(models.Model):
    """ Defining Job Scheduler"""
    _name = "auto.job.scheduler"
    _description = "Automatic Job Scheduler"
    _order = "name asc"

    date = fields.Char('Date')
    name = fields.Char('Name', required=True)
    description = fields.Char('Description')

    @api.model
    def process_result(self):
        new_records = self.env['academic.legacy.student.result'].search([('status', '=', 'New')], limit=350)
        if new_records:
            for result in new_records:
                _logger.info(" Processing New Student ****** {} ******".format(result.matric))
                result.action_process()
        else:
            failed_records = self.env['academic.legacy.student.result'].search([('status', '=', 'Failed')], limit=350)
            for result in failed_records:
                _logger.info(" Processing Failed ****** {} ******".format(result.matric))
                result.action_process()

    @api.model
    def process_student(self):
        new_records = self.env['academic.legacy.student'].search([('status', '=', 'New')], limit=350)
        if new_records:
            for student in new_records:
                _logger.info(" Processing New ****** {} ******".format(student.name))
                student.action_process()
        else:
            failed_records = self.env['academic.legacy.student'].search([('status', '=', 'Failed')], limit=350)
            for student in failed_records:
                _logger.info(" Processing Failed ****** {} ******".format(student.name))
                student.action_process()

    @api.model
    def process_course(self):
        new_records = self.env['academic.school.course'].search([('status', '=', 'New')], limit=350)
        if new_records:
            for course in new_records:
                _logger.info(" Processing New ****** {} ******".format(course.code))
                course.action_process()
        else:
            failed_records = self.env['academic.school.course'].search([('status', '=', 'Failed')], limit=350)
            for course in failed_records:
                _logger.info(" Processing Failed ****** {} ******".format(course.code))
                course.action_process()
                

class Credentials(models.Model):
    """ Credentials """
    _name = "quickgrades.credentials"
    _description = " Credentials"

    lecturer_id = fields.Many2one('quickgrades.lecturer', 'Lecturer', required=True)
    institution = fields.Char('Institution', required=True, size=250)
    discipline = fields.Char('Discipline', required=True, size=250)
    remarks = fields.Text('Remarks')
    diploma_id = fields.Many2one('quickgrades.diploma', 'Diploma', required=True)
    honour_id = fields.Many2one('quickgrades.honour', 'Honour')
    exam_year = fields.Char(required=True, string='Year')
    
    def name_get(self):
        result = []
        for record in self:
            name = "{0} {1} ".format(record.diploma_id.code, record.discipline)
            result.append((record.id, name))
        return result
    
    
class Position(models.Model):
    """Position"""
    _name = "quickgrades.position"
    _description = "Position"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    department_id = fields.Many2one('quickgrades.department')
   

class Lecturer(models.Model):
    """ Defining Academic Staff"""
    _name = "quickgrades.lecturer"
    _description = "Academic Staff"
    _order = "name asc"

    name = fields.Char('Name', required=True)
    surname = fields.Char('Surname', required=True)
    full_name = fields.Char(compute='_compute_full_name', string="Full Name", store=True)
    phone_number = fields.Char('Phone #', required=True)
    middle_name = fields.Char(string='Middle Name', required=False)
    marital_status = fields.Selection(
        selection=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
        required=False,
        string='Marital Status')
    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female')], required=True, string='Sex')
    address = fields.Text(string='Address', required=False)
    email = fields.Char('Email Address')
    title = fields.Selection(string="Title",
                             selection=[
                                 ('Mr', 'Mr'),
                                 ('Mrs', 'Mrs'),
                                 ('Dr', 'Dr'),
                                 ('Engr', 'Engr'),
                                 ('Prof', 'Prof')])
    
    department_id = fields.Many2one('quickgrades.department', 'Department', required=True)
    credential_ids = fields.One2many('quickgrades.credentials', 'lecturer_id', string='Credentials')
    course_ids = fields.Many2many(comodel_name='programme.course', string='Courses')
    faculty_id = fields.Many2one(related='department_id.faculty_id', string='Faculty', readonly=True, store=True)
    employment_date = fields.Date('Employment Date', required=False)
    title = fields.Selection(
        string='Title',
        required=False,
        selection=[('Dr', 'Dr'), ('Engr', 'Engr'), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Miss', 'Miss')],
    )
    department_id = fields.Many2one(
        comodel_name='staff.department', string='Department')
    middle_name = fields.Char(string='Middle Name', required=False)
    marital_status = fields.Selection(
        selection=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
        required=False,
        string='Marital Status')
    position_id = fields.Many2one('quickgrades.academic.position', 'Position', required=False)
    image = fields.Binary(
        "Photograph", attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    
    @api.depends('name', 'surname', 'title')
    def _compute_full_name(self):
        for record in self:
            if record.title:
                record.full_name = "{0} {1} {2}".format(record.title, record.name, record.surname)
            else:
                record.full_name = "{0} {1}".format(record.name, record.surname)

    
    def name_get(self):
        result = []
        for record in self:
            name = "{0}".format(record.full_name)
            result.append((record.id, name))
        return result

