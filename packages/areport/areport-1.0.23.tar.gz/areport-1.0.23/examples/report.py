from areport import Report
from tests.deterministic_data import geometric_daily

# Create a report
pf_values = geometric_daily(start_price=1, end_price=2, n_days=90)
report = Report(pf_values)

report.print_metrics()
report.metrics_to_csv(file_name='report_metrics.csv')
report.daily_pf_values_to_csv(file_name='daily_pf_values.csv')
report.daily_returns_to_csv(file_name='daily_returns.csv')
report.daily_report_to_csv(file_name='daily_report.csv')
report.monthly_report_to_csv(file_name='monthly_report.csv')