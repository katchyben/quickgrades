from odoo import models, fields, api, _


class State(models.Model):
    _description = "State"
    _name = 'academic.state'
    _order = 'name'

    lga_ids = fields.One2many('state.lga', 'state_id', 'LGAs')
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=False)
    country_id = fields.Many2one('res.country', 'Country')




