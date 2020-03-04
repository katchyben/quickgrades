from odoo import models, fields, api, _, tools, exceptions
from odoo.modules.module import get_module_resource
import base64


class Student(models.Model):
    """Defining a subject """
    _name = "quickgrades.student"
    _description = "Students"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('quick_grades', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    name = fields.Char('Name', size=128, required=True)
    matriculation_number = fields.Char('Registration. No', size=64, help='Registration No.')
    application_number = fields.Char('Application. No', size=64, help='Application No.')
    image = fields.Binary(
        "Photograph", default=_default_image, attachment=True,
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

    def _create_student_result(self, student):
        StudentResultBook = self.env['student.result']
        vals = {}
        vals['student_id'] = student.id
        vals['programme_id'] = student.programme_id.id
        result_book = StudentResultBook.create(vals)
        student.write({'result_book_ids': [(4, result_book.id)]})

        return True

    def write(self, vals):
        tools.image_resize_images(vals)
        return super(Student, self).write(vals)

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
