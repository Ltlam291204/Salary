from odoo import models, fields, api

class WdwSalaryCalculation(models.Model):
    _name = 'wdw.salary.calculation'
    _description = 'Bảng tính lương chi tiết'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Thông tin nhân viên
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    employee_code = fields.Char(string='Mã NV', related='employee_id.identification_id', store=True)
    department_id = fields.Many2one('hr.department', string='Bộ phận', related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string='Chức vụ', related='employee_id.job_id', store=True)
    join_date = fields.Date(string='Ngày vào', related='employee_id.date_start')
    
    # Kỳ lương
    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)
    
    # Thông tin hợp đồng
    contract_id = fields.Many2one('hr.contract', string='Hợp đồng')
    
    # Thông tin lương - Bảo hiểm
    salary_insurance = fields.Float(string='Lương đóng BHXH', digits=(12, 0))
    basic_salary = fields.Float(string='Lương cơ bản', digits=(12, 0))
    
    # Phụ cấp
    seniority_allowance = fields.Float(string='Thâm niên', digits=(12, 0), default=0)
    transport_allowance = fields.Float(string='PC đi lại', digits=(12, 0), default=0)
    house_allowance = fields.Float(string='PC nhà ở', digits=(12, 0), default=0)
    environment_allowance = fields.Float(string='PC môi trường', digits=(12, 0), default=0)
    fire_protection_allowance = fields.Float(string='PCCC', digits=(12, 0), default=0)
    position_allowance = fields.Float(string='PC chức vụ', digits=(12, 0), default=0)
    work_allowance = fields.Float(string='PC công việc', digits=(12, 0), default=0)
    skill_allowance = fields.Float(string='PC kỹ năng', digits=(12, 0), default=0)
    attendance_allowance = fields.Float(string='PC chuyên cần', digits=(12, 0), default=0)
    soldering_xray_allowance = fields.Float(string='Hàn, Xray', digits=(12, 0), default=0)
    other_allowance = fields.Float(string='PC khác', digits=(12, 0), default=0)
    
    # Thời gian làm việc
    standard_working_days = fields.Integer(string='Ngày công TC', default=26)
    actual_working_days = fields.Float(string='Ngày công TT', digits=(4, 1), default=0)
    leave_days = fields.Float(string='Nghỉ phép', digits=(4, 1), default=0)
    unpaid_leave_days = fields.Float(string='KL-KLD-OM', digits=(4, 1), default=0)
    unpaid_no_attendance_days = fields.Float(string='Nghỉ KL mất CC', digits=(4, 1), default=0)
    salary_75_percent_days = fields.Float(string='Hưởng 75%', digits=(4, 1), default=0)
    half_leave_days = fields.Float(string='Phép nửa ngày', digits=(4, 1), default=0)
    funeral_wedding_days = fields.Float(string='Hiếu hỷ', digits=(4, 1), default=0)
    holiday_days = fields.Float(string='Nghỉ lễ', digits=(4, 1), default=0)
    
    # Lương ngày công
    workday_pay = fields.Float(string='Lương ngày công', digits=(12, 0), compute='_compute_salary', store=True)
    leave_balance = fields.Float(string='Phép tồn', digits=(4, 1), default=0)
    
    # OT ban ngày
    ot_150_hours = fields.Float(string='OT 150% (giờ)', digits=(4, 2), default=0)
    ot_150_amount = fields.Float(string='OT 150% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    ot_210_hours = fields.Float(string='OT 210% (giờ)', digits=(4, 2), default=0)
    ot_210_amount = fields.Float(string='OT 210% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    
    # OT đêm
    ot_night_200_hours = fields.Float(string='OT đêm 200% (giờ)', digits=(4, 2), default=0)
    ot_night_200_amount = fields.Float(string='OT đêm 200% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    ot_night_150_hours = fields.Float(string='OT đêm 150% (giờ)', digits=(4, 2), default=0)
    ot_night_150_amount = fields.Float(string='OT đêm 150% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Chủ nhật
    sunday_200_hours = fields.Float(string='Chủ nhật 200% (giờ)', digits=(4, 2), default=0)
    sunday_200_amount = fields.Float(string='Chủ nhật 200% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    sunday_270_hours = fields.Float(string='Chủ nhật 270% (giờ)', digits=(4, 2), default=0)
    sunday_270_amount = fields.Float(string='Chủ nhật 270% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Lễ
    holiday_300_hours = fields.Float(string='Lễ 300% (giờ)', digits=(4, 2), default=0)
    holiday_300_amount = fields.Float(string='Lễ 300% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    holiday_390_hours = fields.Float(string='Lễ 390% (giờ)', digits=(4, 2), default=0)
    holiday_390_amount = fields.Float(string='Lễ 390% (tiền)', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Tổng OT
    total_ot_hours = fields.Float(string='Tổng giờ OT', digits=(4, 2), compute='_compute_salary', store=True)
    total_ot_amount = fields.Float(string='Tổng tiền OT', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Phụ cấp khác
    birthday_amount = fields.Float(string='Sinh nhật', digits=(12, 0), default=0)
    business_trip_amount = fields.Float(string='Công tác phí', digits=(12, 0), default=0)
    compensation_amount = fields.Float(string='Bù lương', digits=(12, 0), default=0)
    evaluation_bonus = fields.Float(string='Thưởng đánh giá', digits=(12, 0), default=0)
    leave_compensation = fields.Float(string='Trợ cấp mất việc', digits=(12, 0), default=0)
    child_support = fields.Float(string='Trợ cấp con nhỏ', digits=(12, 0), default=0)
    women_amount = fields.Float(string='Phụ nữ', digits=(12, 0), default=0)
    
    total_allowance = fields.Float(string='Tổng phụ cấp', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Các khoản trừ
    violation_deduction = fields.Float(string='Vi phạm', digits=(12, 0), default=0)
    uniform_card_deduction = fields.Float(string='Trừ đồng phục', digits=(12, 0), default=0)
    negative_leave_deduction = fields.Float(string='Truy thu phép âm', digits=(12, 0), default=0)
    late_early_deduction = fields.Float(string='ĐMVS', digits=(12, 0), default=0)
    total_deduction = fields.Float(string='Tổng trừ', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Tổng quan
    gross_salary = fields.Float(string='Tổng lương gross', digits=(12, 0), compute='_compute_salary', store=True)
    other_bonus = fields.Float(string='Thưởng khác', digits=(12, 0), default=0)
    taxable_income = fields.Float(string='Thu nhập chịu thuế', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Bảo hiểm
    social_insurance_8 = fields.Float(string='BHXH 8%', digits=(12, 0), compute='_compute_salary', store=True)
    health_insurance_1_5 = fields.Float(string='BHYT 1.5%', digits=(12, 0), compute='_compute_salary', store=True)
    unemployment_insurance_1 = fields.Float(string='BHTN 1%', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Thuế và khấu trừ
    pit_amount = fields.Float(string='Thuế TNCN', digits=(12, 0), compute='_compute_salary', store=True)
    union_fee = fields.Float(string='Đoàn phí', digits=(12, 0), compute='_compute_salary', store=True)
    total_deductions = fields.Float(string='Tổng khấu trừ', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Người phụ thuộc
    dependents = fields.Integer(string='Số người phụ thuộc', default=0)
    dependent_deduction_amount = fields.Float(string='Giảm trừ gia cảnh', digits=(12, 0), compute='_compute_salary', store=True)
    taxable_income_after_deduction = fields.Float(string='Thu nhập tính thuế', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Thực nhận
    net_salary = fields.Float(string='Lương thực nhận', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Chi phí công ty
    company_social_insurance_17_5 = fields.Float(string='BHXH 17.5%', digits=(12, 0), compute='_compute_salary', store=True)
    company_health_insurance_3 = fields.Float(string='BHYT 3%', digits=(12, 0), compute='_compute_salary', store=True)
    company_unemployment_insurance_1 = fields.Float(string='BHTN 1%', digits=(12, 0), compute='_compute_salary', store=True)
    company_union_2 = fields.Float(string='Công đoàn 2%', digits=(12, 0), compute='_compute_salary', store=True)
    total_company_cost = fields.Float(string='Tổng chi phí công ty', digits=(12, 0), compute='_compute_salary', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('approved', 'Đã duyệt'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    
    @api.depends(
        'basic_salary', 'actual_working_days', 'standard_working_days',
        'ot_150_hours', 'ot_210_hours', 'ot_night_200_hours', 'ot_night_150_hours',
        'sunday_200_hours', 'sunday_270_hours', 'holiday_300_hours', 'holiday_390_hours',
        'seniority_allowance', 'transport_allowance', 'house_allowance', 'environment_allowance',
        'fire_protection_allowance', 'position_allowance', 'work_allowance', 'skill_allowance',
        'attendance_allowance', 'soldering_xray_allowance', 'other_allowance',
        'birthday_amount', 'business_trip_amount', 'compensation_amount', 'evaluation_bonus',
        'leave_compensation', 'child_support', 'women_amount',
        'violation_deduction', 'uniform_card_deduction', 'negative_leave_deduction', 'late_early_deduction',
        'salary_insurance', 'dependents', 'leave_days'
    )
    def _compute_salary(self):
        config = self.env['wdw.salary.config'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not config:
            config = self.env['wdw.salary.config'].create({'name': 'Default Config'})
        
        for record in self:
            if not record.basic_salary or not record.standard_working_days:
                continue
            
            # Lương ngày công
            daily_rate = record.basic_salary / record.standard_working_days
            hourly_rate = record.basic_salary / (record.standard_working_days * 8)
            
            record.workday_pay = daily_rate * record.actual_working_days
            
            # OT ban ngày
            record.ot_150_amount = record.ot_150_hours * hourly_rate * 1.5
            record.ot_210_amount = record.ot_210_hours * hourly_rate * 2.1
            
            # OT đêm
            record.ot_night_200_amount = record.ot_night_200_hours * hourly_rate * 2.0
            record.ot_night_150_amount = record.ot_night_150_hours * hourly_rate * 1.5
            
            # Chủ nhật
            record.sunday_200_amount = record.sunday_200_hours * hourly_rate * 2.0
            record.sunday_270_amount = record.sunday_270_hours * hourly_rate * 2.7
            
            # Lễ
            record.holiday_300_amount = record.holiday_300_hours * hourly_rate * 3.0
            record.holiday_390_amount = record.holiday_390_hours * hourly_rate * 3.9
            
            # Tổng OT
            record.total_ot_hours = (
                record.ot_150_hours + record.ot_210_hours +
                record.ot_night_200_hours + record.ot_night_150_hours +
                record.sunday_200_hours + record.sunday_270_hours +
                record.holiday_300_hours + record.holiday_390_hours
            )
            record.total_ot_amount = (
                record.ot_150_amount + record.ot_210_amount +
                record.ot_night_200_amount + record.ot_night_150_amount +
                record.sunday_200_amount + record.sunday_270_amount +
                record.holiday_300_amount + record.holiday_390_amount
            )
            
            # Tổng phụ cấp
            record.total_allowance = (
                record.seniority_allowance + record.transport_allowance +
                record.house_allowance + record.environment_allowance +
                record.fire_protection_allowance + record.position_allowance +
                record.work_allowance + record.skill_allowance +
                record.attendance_allowance + record.soldering_xray_allowance +
                record.other_allowance + record.birthday_amount +
                record.business_trip_amount + record.compensation_amount +
                record.evaluation_bonus + record.leave_compensation +
                record.child_support + record.women_amount
            )
            
            # Bảo hiểm
            record.social_insurance_8 = record.salary_insurance * 0.08
            record.health_insurance_1_5 = record.salary_insurance * 0.015
            record.unemployment_insurance_1 = record.salary_insurance * 0.01
            
            # Tổng trừ
            record.total_deduction = (
                record.violation_deduction + record.uniform_card_deduction +
                record.negative_leave_deduction + record.late_early_deduction
            )
            
            # Tổng lương gross
            record.gross_salary = (
                record.workday_pay + record.total_ot_amount +
                record.total_allowance - record.total_deduction + record.other_bonus
            )
            
            # Giảm trừ gia cảnh
            record.dependent_deduction_amount = record.dependents * config.dependent_deduction
            
            # Thu nhập chịu thuế
            record.taxable_income = record.gross_salary - (
                record.social_insurance_8 + record.health_insurance_1_5 +
                record.unemployment_insurance_1 + record.dependent_deduction_amount
            )
            
            # Tính thuế TNCN
            record.pit_amount = self._calculate_pit(record.taxable_income)
            
            # Đoàn phí
            record.union_fee = record.gross_salary * 0.01 if record.gross_salary > 0 else 0
            
            # Tổng khấu trừ
            record.total_deductions = (
                record.social_insurance_8 + record.health_insurance_1_5 +
                record.unemployment_insurance_1 + record.pit_amount +
                record.union_fee
            )
            
            # Lương thực nhận
            record.net_salary = record.gross_salary - record.total_deductions
            
            # Chi phí công ty
            record.company_social_insurance_17_5 = record.salary_insurance * 0.175
            record.company_health_insurance_3 = record.salary_insurance * 0.03
            record.company_unemployment_insurance_1 = record.salary_insurance * 0.01
            record.company_union_2 = record.gross_salary * 0.02
            record.total_company_cost = (
                record.gross_salary + record.company_social_insurance_17_5 +
                record.company_health_insurance_3 + record.company_unemployment_insurance_1 +
                record.company_union_2
            )
    
    def _calculate_pit(self, taxable_income):
        # Logic tính thuế TNCN theo bảng tính Việt Nam
        if taxable_income <= 0:
            return 0
        
        # Bảng thuế suất 2023
        tax_brackets = [
            (0, 5000000, 0.05),
            (5000000, 10000000, 0.10),
            (10000000, 18000000, 0.15),
            (18000000, 32000000, 0.20),
            (32000000, 52000000, 0.25),
            (52000000, 80000000, 0.30),
            (80000000, float('inf'), 0.35)
        ]
        
        tax = 0
        remaining_income = taxable_income
        
        for low, high, rate in tax_brackets:
            bracket_size = high - low
            taxable_in_bracket = min(remaining_income, bracket_size)
            
            if taxable_in_bracket > 0:
                tax += taxable_in_bracket * rate
                remaining_income -= taxable_in_bracket
            else:
                break
        
        return tax
    
    def action_calculate_from_timesheet(self):
        for record in self:
            # Lấy dữ liệu từ timesheet
            timesheets = self.env['wdw.timesheet'].search([
                ('employee_id', '=', record.employee_id.id),
                ('period_id', '=', record.period_id.id)
            ])
            
            if not timesheets:
                continue
            
            # Reset dữ liệu
            record.write({
                'actual_working_days': 0, 'leave_days': 0, 'unpaid_leave_days': 0,
                'ot_150_hours': 0, 'ot_210_hours': 0, 'ot_night_200_hours': 0,
                'ot_night_150_hours': 0, 'sunday_200_hours': 0, 'sunday_270_hours': 0,
                'holiday_300_hours': 0, 'holiday_390_hours': 0,
                'late_early_deduction': 0
            })
            
            # Tính tổng các loại nghỉ
            record.actual_working_days = len(timesheets.filtered(lambda t: not t.leave_type and t.working_hours > 0))
            record.leave_days = len(timesheets.filtered(lambda t: t.leave_type == 'NP'))
            record.unpaid_leave_days = len(timesheets.filtered(lambda t: t.leave_type in ['KL', 'KLD', 'OM']))
            record.salary_75_percent_days = len(timesheets.filtered(lambda t: t.leave_type == 'HL'))
            record.half_leave_days = len(timesheets.filtered(lambda t: t.leave_type == 'PNN'))
            record.funeral_wedding_days = len(timesheets.filtered(lambda t: t.leave_type == 'HH'))
            record.holiday_days = len(timesheets.filtered(lambda t: t.leave_type == 'NL'))
            record.unpaid_no_attendance_days = len(timesheets.filtered(lambda t: t.leave_type == 'KLD'))
            
            # Tính OT
            record.ot_150_hours = sum(timesheets.mapped('ot_150_percent'))
            record.ot_210_hours = 0  # Không có trong timesheet
            record.ot_night_200_hours = sum(timesheets.mapped('ot_night_200_percent'))
            record.ot_night_150_hours = sum(timesheets.mapped('ot_night_150_percent'))
            record.sunday_200_hours = sum(timesheets.mapped('sunday_200_percent'))
            record.sunday_270_hours = sum(timesheets.mapped('sunday_270_percent'))
            record.holiday_300_hours = sum(timesheets.mapped('holiday_300_percent'))
            record.holiday_390_hours = sum(timesheets.mapped('holiday_390_percent'))
            
            # Tính trừ đi muộn về sớm
            record.late_early_deduction = sum(timesheets.mapped('late_early_amount'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_approve(self):
        self.write({'state': 'approved'})
    
    def action_draft(self):
        self.write({'state': 'draft'})

class WdwSalaryCalculationLine(models.Model):
    _name = 'wdw.salary.calculation.line'
    _description = 'Chi tiết tính lương'
    
    calculation_id = fields.Many2one('wdw.salary.calculation', string='Bảng lương')
    name = fields.Char(string='Mục')
    hours = fields.Float(string='Số giờ')
    amount = fields.Float(string='Số tiền')
    note = fields.Char(string='Ghi chú')