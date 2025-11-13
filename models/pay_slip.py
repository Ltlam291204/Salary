from odoo import models, fields, api

class WdwPaySlip(models.Model):
    _name = 'wdw.pay.slip'
    _description = 'Phiếu lương WDW'
    _order = 'period_id desc, employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)
    
    # Thông tin cá nhân
    join_date = fields.Date(string='Ngày vào', related='employee_id.date_start')
    department_id = fields.Many2one('hr.department', string='Bộ phận', related='employee_id.department_id')
    job_id = fields.Many2one('hr.job', string='Chức vụ', related='employee_id.job_id')
    dependents = fields.Integer(string='Số người phụ thuộc')
    bank_account = fields.Char(string='Tài khoản', related='employee_id.bank_account_id.acc_number')
    
    # Thời gian làm việc
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
    
    # Thu nhập
    workday_pay = fields.Float(string='Lương ngày công')
    
    # Phụ cấp
    seniority_allowance = fields.Float(string='Thâm niên')
    transport_allowance = fields.Float(string='PC đi lại')
    house_allowance = fields.Float(string='PC nhà ở')
    environment_allowance = fields.Float(string='PC môi trường')
    position_allowance = fields.Float(string='PC vị trí')
    work_allowance = fields.Float(string='PC công việc')
    skill_allowance = fields.Float(string='PC kỹ năng')
    attendance_allowance = fields.Float(string='PC chuyên cần')
    soldering_xray_allowance = fields.Float(string='PC hàn, Xray')
    
    # OT
    ot_150_amount = fields.Float(string='OT ngày 150%')
    ot_210_amount = fields.Float(string='OT ngày 210%')
    ot_night_200_amount = fields.Float(string='OT đêm 200%')
    ot_night_150_amount = fields.Float(string='OT đêm 150%')
    sunday_200_amount = fields.Float(string='Chủ nhật ngày 200%')
    sunday_270_amount = fields.Float(string='Chủ nhật đêm 270%')
    holiday_300_amount = fields.Float(string='Lễ ngày 300%')
    holiday_390_amount = fields.Float(string='Lễ đêm 390%')
    
    # Phụ cấp khác
    birthday_amount = fields.Float(string='Sinh nhật')
    business_trip_amount = fields.Float(string='Công tác phí')
    compensation_amount = fields.Float(string='Bù lương')
    evaluation_bonus = fields.Float(string='Thưởng đánh giá')
    child_support = fields.Float(string='Trợ cấp con nhỏ')
    women_amount = fields.Float(string='Phụ nữ')
    
    # Các khoản trừ
    violation_deduction = fields.Float(string='Trừ vi phạm')
    uniform_card_deduction = fields.Float(string='Trừ đồng phục')
    negative_leave_deduction = fields.Float(string='Truy thu phép âm')
    late_early_deduction = fields.Float(string='Trừ ĐMVS')
    
    # Tổng kết
    gross_salary = fields.Float(string='Tổng thu nhập')
    other_bonus = fields.Float(string='Thưởng khác')
    
    # Bảo hiểm
    social_insurance = fields.Float(string='BHXH 8%')
    health_insurance = fields.Float(string='BHYT 1.5%')
    unemployment_insurance = fields.Float(string='BHTN 1%')
    
    # Thuế
    pit_amount = fields.Float(string='Thuế TNCN')
    union_fee = fields.Float(string='Đoàn phí')
    
    # Tổng khấu trừ
    total_deductions = fields.Float(string='Tổng khấu trừ')
    
    # Lương thực nhận
    net_salary = fields.Float(string='Lương thực nhận')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
    ], string='Trạng thái', default='draft')
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    def action_send_payslip(self):
        """Gửi phiếu lương qua email cho nhân viên"""
        self.ensure_one()
        template = self.env.ref('wdw_salary_management.email_template_payslip')
        if template:
            template.send_mail(self.id, force_send=True)
        self.write({'state': 'sent'})
    
    def action_print_payslip(self):
        """In phiếu lương"""
        self.ensure_one()
        return self.env.ref('wdw_salary_management.action_report_payslip').report_action(self)