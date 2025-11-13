import base64
import pandas as pd
from odoo import models, fields, api
from odoo.exceptions import UserError

class ImportTimesheetWizard(models.TransientModel):
    _name = 'wdw.import.timesheet.wizard'
    _description = 'Import dữ liệu chấm công từ Excel'
    
    file = fields.Binary(string='File Excel', required=True)
    filename = fields.Char(string='Tên file')
    period_id = fields.Many2one('wdw.salary.period', string='Kỳ lương', required=True)
    sheet_name = fields.Char(string='Sheet name', default='BCC')
    
    def action_import(self):
        self.ensure_one()
        
        if not self.file:
            raise UserError('Vui lòng chọn file Excel!')
        
        try:
            # Đọc file Excel
            data = base64.b64decode(self.file)
            df = pd.read_excel(data, sheet_name=self.sheet_name, header=None)
            
            # Tìm dòng bắt đầu dữ liệu
            header_row = None
            for i, row in df.iterrows():
                if 'Person No' in str(row.values) or 'Mã NV' in str(row.values):
                    header_row = i
                    break
            
            if header_row is None:
                raise UserError('Không tìm thấy tiêu đề trong file!')
            
            # Đọc lại với header đúng
            df = pd.read_excel(data, sheet_name=self.sheet_name, header=header_row)
            
            # Xử lý từng dòng
            success_count = 0
            for index, row in df.iterrows():
                # Bỏ qua dòng trống
                if pd.isna(row.get('Person No')) or pd.isna(row.get('Name')):
                    continue
                
                employee_code = str(row['Person No']).strip()
                employee_name = str(row['Name']).strip() if not pd.isna(row['Name']) else ''
                
                # Tìm nhân viên
                employee = self.env['hr.employee'].search([
                    '|',
                    ('identification_id', '=', employee_code),
                    ('name', 'ilike', employee_name)
                ], limit=1)
                
                if not employee:
                    # Tạo mới nhân viên nếu chưa tồn tại
                    employee = self.env['hr.employee'].create({
                        'identification_id': employee_code,
                        'name': employee_name,
                        'department_id': self.env['hr.department'].search([('name', 'ilike', str(row.get('Department', '')))], limit=1).id,
                        'job_id': self.env['hr.job'].search([('name', 'ilike', str(row.get('Position', '')))], limit=1).id,
                    })
                
                # Xử lý từng ngày trong tháng
                for day in range(1, 32):
                    col_start = f'{day:02d}'
                    col_check_in = f'{col_start}_start'
                    col_check_out = f'{col_start}_end'
                    
                    # Nếu không có cột, bỏ qua
                    if col_check_in not in df.columns or col_check_out not in df.columns:
                        continue
                    
                    check_in = row.get(col_check_in)
                    check_out = row.get(col_check_out)
                    
                    # Bỏ qua nếu không có dữ liệu
                    if pd.isna(check_in) and pd.isna(check_out):
                        continue
                    
                    # Chuyển đổi thời gian
                    check_in_hour = self._convert_time_to_float(check_in) if not pd.isna(check_in) else 0
                    check_out_hour = self._convert_time_to_float(check_out) if not pd.isna(check_out) else 0
                    
                    # Ngày trong tháng
                    try:
                        day_date = self.period_id.date_from.replace(day=day)
                    except ValueError:
                        continue
                    
                    # Xóa dữ liệu cũ
                    existing = self.env['wdw.timesheet'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '=', day_date)
                    ])
                    existing.unlink()
                    
                    # Tạo bản ghi mới
                    self.env['wdw.timesheet'].create({
                        'employee_id': employee.id,
                        'date': day_date,
                        'check_in_hour': check_in_hour,
                        'check_out_hour': check_out_hour,
                        'period_id': self.period_id.id,
                    })
                
                success_count += 1
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Import thành công',
                    'message': f'Đã import {success_count} nhân viên',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f'Lỗi import: {str(e)}')
    
    def _convert_time_to_float(self, time_val):
        """Chuyển đổi thời gian sang float"""
        if isinstance(time_val, (int, float)):
            return float(time_val)
        
        if isinstance(time_val, str):
            try:
                # Format: "06:21" -> 6.35
                parts = time_val.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                return hour + minute / 60
            except:
                return 0
        
        return 0