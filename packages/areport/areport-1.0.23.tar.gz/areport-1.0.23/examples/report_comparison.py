from areport import Report, ReportComparison
from tests.deterministic_data import geometric_daily

# Create a report
portfolio_pf_values = geometric_daily(start_price=1, end_price=1.5, n_days=90)
benchmark_pf_values = geometric_daily(start_price=1, end_price=1.3, n_days=90)
comparison = ReportComparison(report=Report(portfolio_pf_values), benchmark_reports={'bm_1': Report(benchmark_pf_values)})

comparison.print_metrics()
comparison.metrics_to_csv(file_name='report_comparison_metrics.csv')
comparison.benchmark_daily_report_to_csv(file_name='benchmark_daily_report.csv')
comparison.benchmark_monthly_report_to_csv(file_name='benchmark_monthly_report.csv')
comparison.benchmark_annual_report_to_csv(file_name='benchmark_annual_report.csv')
comparison.benchmark_monthly_returns_to_csv(file_name='benchmark_monthly_returns.csv')
comparison.benchmark_annual_returns_to_csv(file_name='benchmark_annual_returns.csv')
comparison.benchmark_daily_returns_to_csv(file_name='benchmark_daily_returns.csv')
comparison.benchmark_daily_pf_values_to_csv(file_name='benchmark_daily_pf_values.csv')
comparison.benchmark_monthly_pf_values_to_csv(file_name='benchmark_monthly_pf_values.csv', lookback=2)
comparison.benchmark_annual_pf_values_to_csv(file_name='benchmark_annual_pf_values.csv')