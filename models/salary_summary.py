from odoo import models, fields, api

class WdwSalarySummary(models.Model):
    _name = 'wdw.salary.summary'
    _description = 'Tóm tắt lương WDW'
    _order = 'period_id desc'

    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)
    total_employees = fields.Integer(string='Tổng số nhân viên', compute='_compute_summary', store=True)
    total_gross_salary = fields.Float(string='Tổng lương gross', digits=(12, 0), compute='_compute_summary', store=True)
    total_insurance = fields.Float(string='Tổng BHXH', digits=(12, 0), compute='_compute_summary', store=True)
    total_pit = fields.Float(string='Tổng thuế TNCN', digits=(12, 0), compute='_compute_summary', store=True)
    total_union = fields.Float(string='Tổng công đoàn', digits=(12, 0), compute='_compute_summary', store=True)
    total_cost = fields.Float(string='Tổng chi phí', digits=(12, 0), compute='_compute_summary', store=True)
    salary_payment_expenses = fields.Float(string='Chi phí chi trả', digits=(12, 0))
    first_advance = fields.Float(string='Tạm ứng 50%', digits=(12, 0))
    second_payment = fields.Float(string='Chi trả lần 2', digits=(12, 0), compute='_compute_summary', store=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    @api.depends('period_id', 'salary_payment_expenses', 'first_advance')
    def _compute_summary(self):
        for record in self:
            calculations = self.env['wdw.salary.calculation'].search([
                ('period_id', '=', record.period_id.id),
                ('state', '=', 'approved')
            ])
            record.total_employees = len(calculations)
            record.total_gross_salary = sum(calculations.mapped('gross_salary'))
            record.total_insurance = sum(calculations.mapped('social_insurance_8')) + sum(calculations.mapped('health_insurance_1_5')) + sum(calculations.mapped('unemployment_insurance_1'))
            record.total_pit = sum(calculations.mapped('pit_amount'))
            record.total_union = sum(calculations.mapped('union_fee'))
            record.total_cost = sum(calculations.mapped('total_company_cost'))
            record.second_payment = record.salary_payment_expenses - record.first_advance

    def action_generate_payslips(self):
        calculations = self.env['wdw.salary.calculation'].search([
            ('period_id', '=', self.period_id.id),
            ('state', '=', 'approved')
        ])
        payslip_model = self.env['wdw.pay.slip']
        for calc in calculations:
            existing = payslip_model.search([
                ('employee_id', '=', calc.employee_id.id),
                ('period_id', '=', calc.period_id.id)
            ])
            if existing:
                continue
            vals = {
                'employee_id': calc.employee_id.id,
                'period_id': calc.period_id.id,
                'working_days': calc.actual_working_days,
                'leave_days': calc.leave_days,
                'unpaid_leave_days': calc.unpaid_leave_days,
                'dependents': calc.dependents,
                'workday_pay': calc.workday_pay,
                'seniority_allowance': calc.seniority_allowance,
                'transport_allowance': calc.transport_allowance,
                'house_allowance': calc.house_allowance,
                'environment_allowance': calc.environment_allowance,
                'position_allowance': calc.position_allowance,
                'work_allowance': calc.work_allowance,
                'skill_allowance': calc.skill_allowance,
                'attendance_allowance': calc.attendance_allowance,
                'soldering_xray_allowance': calc.soldering_xray_allowance,
                'ot_150_amount': calc.ot_150_amount,
                'ot_210_amount': calc.ot_210_amount,
                'ot_night_200_amount': calc.ot_night_200_amount,
                'ot_night_150_amount': calc.ot_night_150_amount,
                'sunday_200_amount': calc.sunday_200_amount,
                'sunday_270_amount': calc.sunday_270_amount,
                'holiday_300_amount': calc.holiday_300_amount,
                'holiday_390_amount': calc.holiday_390_amount,
                'birthday_amount': calc.birthday_amount,
                'business_trip_amount': calc.business_trip_amount,
                'compensation_amount': calc.compensation_amount,
                'evaluation_bonus': calc.evaluation_bonus,
                'child_support': calc.child_support,
                'women_amount': calc.women_amount,
                'violation_deduction': calc.total_deduction,
                'gross_salary': calc.gross_salary,
                'social_insurance': calc.social_insurance_8 + calc.health_insurance_1_5 + calc.unemployment_insurance_1,
                'health_insurance': calc.health_insurance_1_5,
                'unemployment_insurance': calc.unemployment_insurance_1,
                'pit_amount': calc.pit_amount,
                'union_fee': calc.union_fee,
                'total_deductions': calc.total_deductions,
                'net_salary': calc.net_salary,
            }
            payslip_model.create(vals)