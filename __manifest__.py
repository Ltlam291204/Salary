{
    'name': 'Salary Management',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Quản lý lương  theo mẫu Excel',
    'description': """
Module quản lý chấm công và tính lương tự động 
- Import dữ liệu chấm công từ Excel
- Tính lương tự động theo quy định
- In phiếu lương
- Báo cáo tổng hợp
""",
    'author': 'phulq',
    'website': 'https://wdw.vn',
    'depends': [
        'hr',
        'hr_contract',
        'hr_holidays',
        'hr_public_holidays',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/timesheet_views.xml',  # ← Đưa lên trước
        'views/menu.xml',             # ← Sau khi đã có action
        'views/salary_calculation_views.xml',
        'views/pay_slip_views.xml',
        'views/salary_summary_views.xml',
        'wizard/import_timesheet_wizard.xml',
        # 'reports/pay_slip_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}