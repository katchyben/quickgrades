from odoo import models, fields, api, exceptions


class StateLga(models.Model):
    _description = "LGA"
    _name = 'state.lga'
    _order = 'name'

    state_id = fields.Many2one('academic.state', 'State', required=True)
    name = fields.Char('Local Government Area', size=64, required=True)
