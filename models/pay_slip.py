from odoo import models, fields

class WdwPaySlip(models.Model):
    _name = 'wdw.pay.slip'
    _description = 'Phiếu lương WDW'
    _order = 'period_id desc, employee_id'

    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    employee_code = fields.Char(string="Mã NV", related="employee_id.identification_id", store=True, readonly=True)
    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)

    join_date = fields.Date(string='Ngày vào')
    department_id = fields.Many2one('hr.department', string='Bộ phận')
    job_id = fields.Many2one('hr.job', string='Chức vụ')
    dependents = fields.Integer(string='Số người phụ thuộc')
    bank_account = fields.Char(string='Tài khoản')

    working_days = fields.Float(string='Đi làm')
    leave_days = fields.Float(string='Nghỉ phép')
    unpaid_leave_days = fields.Float(string='KL-KLD')
    salary_deduction_days = fields.Float(string='Trừ lương')
    salary_75_percent_days = fields.Float(string='Hưởng 75%')
    half_leave_days = fields.Float(string='Phép nửa ngày')
    funeral_wedding_days = fields.Float(string='Hiếu hỷ')
    holiday_days = fields.Float(string='Nghỉ lễ')
    late_early_hours = fields.Float(string='ĐMVS')
    leave_balance = fields.Float(string='Tồn phép')

    workday_pay = fields.Float(string='Lương ngày công')
    seniority_allowance = fields.Float(string='Thâm niên')
    transport_allowance = fields.Float(string='PC đi lại')
    house_allowance = fields.Float(string='PC nhà ở')
    environment_allowance = fields.Float(string='PC môi trường')
    position_allowance = fields.Float(string='PC vị trí')
    work_allowance = fields.Float(string='PC công việc')
    skill_allowance = fields.Float(string='PC kỹ năng')
    attendance_allowance = fields.Float(string='PC chuyên cần')
    soldering_xray_allowance = fields.Float(string='PC hàn, Xray')

    ot_150_amount = fields.Float(string='OT ngày 150%')
    ot_210_amount = fields.Float(string='OT ngày 210%')
    ot_night_200_amount = fields.Float(string='OT đêm 200%')
    ot_night_150_amount = fields.Float(string='OT đêm 150%')
    sunday_200_amount = fields.Float(string='Chủ nhật ngày 200%')
    sunday_270_amount = fields.Float(string='Chủ nhật đêm 270%')
    holiday_300_amount = fields.Float(string='Lễ ngày 300%')
    holiday_390_amount = fields.Float(string='Lễ đêm 390%')

    birthday_amount = fields.Float(string='Sinh nhật')
    business_trip_amount = fields.Float(string='Công tác phí')
    compensation_amount = fields.Float(string='Bù lương')
    evaluation_bonus = fields.Float(string='Thưởng đánh giá')
    child_support = fields.Float(string='Trợ cấp con nhỏ')
    women_amount = fields.Float(string='Phụ nữ')

    violation_deduction = fields.Float(string='Trừ vi phạm')
    uniform_card_deduction = fields.Float(string='Trừ đồng phục')
    negative_leave_deduction = fields.Float(string='Truy thu phép âm')
    late_early_deduction = fields.Float(string='Trừ ĐMVS')

    gross_salary = fields.Float(string='Tổng thu nhập')
    other_bonus = fields.Float(string='Thưởng khác')

    social_insurance = fields.Float(string='BHXH 8%')
    health_insurance = fields.Float(string='BHYT 1.5%')
    unemployment_insurance = fields.Float(string='BHTN 1%')
    pit_amount = fields.Float(string='Thuế TNCN')
    union_fee = fields.Float(string='Đoàn phí')
    total_deductions = fields.Float(string='Tổng khấu trừ')
    net_salary = fields.Float(string='Lương thực nhận')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
    ], string='Trạng thái', default='draft')

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_send_payslip(self):
        self.ensure_one()
        template = self.env.ref('wdw_salary_management.email_template_payslip')
        if template:
            template.send_mail(self.id, force_send=True)
        self.write({'state': 'sent'})

    def action_print_payslip(self):
        self.ensure_one()
        return self.env.ref('wdw_salary_management.action_report_payslip').report_action(self)