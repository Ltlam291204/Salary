from odoo import models, fields, api
from datetime import datetime

class WdwTimesheet(models.Model):
    _name = 'wdw.timesheet'
    _description = 'Bảng chấm công WDW'
    _order = 'employee_id, date asc'
    _rec_name = 'display_name'

    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    date = fields.Date(string='Ngày', required=True, index=True)
    day_of_week_name = fields.Char(string='Thứ', compute='_compute_day_info', store=True)
    day_number = fields.Integer(string='Ngày trong tháng', compute='_compute_day_info', store=True)

    check_in_hour = fields.Float(string='Giờ vào', digits=(4, 2))
    check_out_hour = fields.Float(string='Giờ ra', digits=(4, 2))

    leave_type = fields.Selection([
        ('NP', 'Nghỉ phép'),
        ('KL', 'Nghỉ không lý do'),
        ('KLD', 'Nghỉ không lý do - mất chuyên cần'),
        ('OM', 'Nghỉ ốm'),
        ('TL', 'Nghỉ thai sản/vợ sinh'),
        ('HL', 'Hưởng 75% lương'),
        ('PNN', 'Nghỉ phép nửa ngày'),
        ('HH', 'Hiếu hỷ'),
        ('NL', 'Nghỉ lễ'),
    ], string='Loại nghỉ')

    ot_150_percent = fields.Float(string='OT 150% (giờ)', digits=(4, 2), default=0)
    ot_210_percent = fields.Float(string='OT 210% (giờ)', digits=(4, 2), default=0)
    ot_night_200_percent = fields.Float(string='OT đêm 200% (giờ)', digits=(4, 2), default=0)
    ot_night_150_percent = fields.Float(string='OT đêm 150% (giờ)', digits=(4, 2), default=0)
    late_early_hours = fields.Float(string='ĐMVS (giờ)', digits=(4, 2), default=0)
    late_early_amount = fields.Float(string='Trừ ĐMVS', digits=(12, 0), default=0)
    sunday_200_percent = fields.Float(string='Chủ nhật 200% (giờ)', digits=(4, 2), default=0)
    sunday_270_percent = fields.Float(string='Chủ nhật 270% (giờ)', digits=(4, 2), default=0)
    holiday_300_percent = fields.Float(string='Lễ 300% (giờ)', digits=(4, 2), default=0)
    holiday_390_percent = fields.Float(string='Lễ 390% (giờ)', digits=(4, 2), default=0)

    working_hours = fields.Float(string='Giờ làm việc', compute='_compute_working_hours', store=True, digits=(4, 2))
    normal_working_hours = fields.Float(string='Giờ bình thường', compute='_compute_working_hours', store=True, digits=(4, 2))
    is_sunday = fields.Boolean(string='Là CN', compute='_compute_day_info', store=True, index=True)
    is_holiday = fields.Boolean(string='Là lễ', compute='_compute_day_info', store=True, index=True)
    is_weekday = fields.Boolean(string='Ngày thường', compute='_compute_day_info', store=True)

    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    display_name = fields.Char(string='Tên hiển thị', compute='_compute_display_name', store=True)

    @api.depends('employee_id', 'date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.employee_id.name or ''} - {record.date or ''}"

    @api.depends('check_in_hour', 'check_out_hour', 'date')
    def _compute_working_hours(self):
        for record in self:
            if record.check_in_hour and record.check_out_hour:
                record.working_hours = record.check_out_hour - record.check_in_hour
                if not record.is_sunday and not record.is_holiday:
                    record.normal_working_hours = min(record.working_hours, 8.0)
                else:
                    record.normal_working_hours = 0
            else:
                record.working_hours = 0
                record.normal_working_hours = 0

    @api.depends('date')
    def _compute_day_info(self):
        for record in self:
            if record.date:
                record.day_number = record.date.day
                record.day_of_week_name = self._get_vietnamese_day(record.date.weekday())
                record.is_sunday = record.date.weekday() == 6
                record.is_weekday = record.date.weekday() < 5
                public_holiday = self.env['hr.holidays.public'].search([
                    ('year', '=', record.date.year)
                ], limit=1)
                is_holiday = False
                if public_holiday:
                    for line in public_holiday.line_ids:
                        if line.date == record.date:
                            is_holiday = True
                            break
                record.is_holiday = is_holiday
            else:
                record.day_number = 0
                record.day_of_week_name = ''
                record.is_sunday = False
                record.is_holiday = False
                record.is_weekday = False

    def _get_vietnamese_day(self, weekday):
        days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        return days[weekday]

    _sql_constraints = [
        ('unique_employee_date', 'UNIQUE(employee_id, date)', 'Mỗi nhân viên chỉ có một bản ghi chấm công trong ngày!')
    ]

class WdwSalaryPeriod(models.Model):
    _name = 'wdw.salary.period'
    _description = 'Kỳ tính lương'
    _order = 'date_from desc'

    name = fields.Char(string='Kỳ lương', required=True)
    date_from = fields.Date(string='Từ ngày', required=True)
    date_to = fields.Date(string='Đến ngày', required=True)
    month = fields.Integer(string='Tháng', compute='_compute_month_year', store=True)
    year = fields.Integer(string='Năm', compute='_compute_month_year', store=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('calculated', 'Đã tính lương'),
        ('paid', 'Đã chi trả'),
    ], string='Trạng thái', default='draft', tracking=True)
    description = fields.Text(string='Ghi chú')

    @api.depends('date_from')
    def _compute_month_year(self):
        for record in self:
            if record.date_from:
                record.month = record.date_from.month
                record.year = record.date_from.year
            else:
                record.month = 0
                record.year = 0

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_calculate(self):
        self.write({'state': 'calculated'})

    def action_pay(self):
        self.write({'state': 'paid'})

    def action_draft(self):
        self.write({'state': 'draft'})