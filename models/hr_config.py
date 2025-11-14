from odoo import models, fields

class WdwSalaryConfig(models.Model):
    _name = 'wdw.salary.config'
    _description = 'Cấu hình tính lương WDW'

    name = fields.Char(string='Tên cấu hình', required=True, default='Cấu hình')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    dependent_deduction = fields.Float(string='Mức giảm trừ gia cảnh', default=11000000, digits=(12, 0))
    personal_deduction = fields.Float(string='Giảm trừ bản thân', default=11000000, digits=(12, 0))

    ot_150_rate = fields.Float(string='OT 150%', default=1.5, digits=(3, 2))
    ot_210_rate = fields.Float(string='OT 210%', default=2.1, digits=(3, 2))
    ot_night_200_rate = fields.Float(string='OT đêm 200%', default=2.0, digits=(3, 2))
    ot_night_150_rate = fields.Float(string='OT đêm 150%', default=1.5, digits=(3, 2))
    sunday_200_rate = fields.Float(string='Chủ nhật 200%', default=2.0, digits=(3, 2))
    sunday_270_rate = fields.Float(string='Chủ nhật 270%', default=2.7, digits=(3, 2))
    holiday_300_rate = fields.Float(string='Lễ 300%', default=3.0, digits=(3, 2))
    holiday_390_rate = fields.Float(string='Lễ 390%', default=3.9, digits=(3, 2))

    social_insurance_employee = fields.Float(string='BHXH NV (%)', default=8, digits=(3, 1))
    social_insurance_company = fields.Float(string='BHXH Cty (%)', default=17.5, digits=(3, 1))
    health_insurance_employee = fields.Float(string='BHYT NV (%)', default=1.5, digits=(3, 1))
    health_insurance_company = fields.Float(string='BHYT Cty (%)', default=3.0, digits=(3, 1))
    unemployment_insurance_employee = fields.Float(string='BHTN NV (%)', default=1.0, digits=(3, 1))
    unemployment_insurance_company = fields.Float(string='BHTN Cty (%)', default=1.0, digits=(3, 1))
    union_fee_employee = fields.Float(string='Đoàn phí NV (%)', default=1.0, digits=(3, 1))
    union_fee_company = fields.Float(string='Đoàn phí Cty (%)', default=2.0, digits=(3, 1))

    _sql_constraints = [
        ('unique_company_config', 'UNIQUE(company_id)', 'Mỗi công ty chỉ có một cấu hình!')
    ]