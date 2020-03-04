from odoo import models, fields, api, exceptions


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
