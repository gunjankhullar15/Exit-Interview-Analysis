import { BaseChartDirective } from 'ng2-charts';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
// import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { Chart, ChartConfiguration, ChartData, ChartType, registerables } from 'chart.js';
import { MaterialModule } from '../../../../../../Shared/Modules/MaterialModule';
import { FormsModule } from '@angular/forms';
import { Navbar } from '../../../../Navbar/Pages/navbar/navbar';
// import { environment } from '../../../../../../../app/Core/Environment/Environment';
import { ChartsSer } from '../../../Services/charts-ser';
import { ReportData, BreakdownItem } from '../../../../../../Shared/Interfaces/chartReport';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(...registerables, ChartDataLabels);

@Component({
  selector: 'app-charts',
  imports: [CommonModule, FormsModule, MaterialModule, Navbar,BaseChartDirective],
  templateUrl: './charts.html',
  styleUrl: './charts.scss',
})



export class Charts implements OnInit {

  isLoading = false;
  reportData: ReportData | null = null;

  startDateObj: Date | null = null;
  endDateObj: Date | null = null;
  startDate = '';
  endDate = '';

  selectedDepartment = '';
  departments: string[] = [];

  doughnutChartLabels: string[] = [];

  doughnutChartData: ChartData<'doughnut'> = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B'],
      borderWidth: 0,
      hoverOffset: 10
    }]
  };

  readonly doughnutChartType = 'doughnut' as const;

  readonly doughnutChartOptions: ChartConfiguration<'doughnut'>['options'] = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  animation: { duration: 600 },
  plugins: {
    legend: { display: false },

    tooltip: {
      backgroundColor: 'rgba(26,26,46,0.92)',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`
      }
    },

    // ── datalabels: show % on each slice ─────────────────────────────────────
    datalabels: {
      display: true,
      color: '#ffffff',
      font: {
        size: 13,
        weight: 'bold',
        family: 'Roboto, sans-serif'
      },
      formatter: (value: number) => `${Math.round(value)}%`,

      // Place label in the middle of each arc segment
      anchor: 'center',
      align: 'center',

      // Only show label if slice is big enough (skip tiny slivers)
      clip: false,
    } as any
  }
};










  departmentBreakdown: BreakdownItem[] = [];
  reasonBreakdown: BreakdownItem[] = [];

  readonly COLORS = [
    '#6366F1', '#8B5CF6', '#EC4899', '#F59E0B',
    '#10B981', '#F97316', '#3B82F6', '#EF4444'
  ];

  // Maps each raw API reason key → display group name
  readonly REASON_GROUPS: { [key: string]: string } = {
    'role redundancy':                 'Role Redundancy',
    'lack of growth opportunities':    'Career Growth',
    'career change':                   'Career Growth',
    'dissatisfaction with management': 'Management & Leadership',
    'toxic work environment':          'Management & Leadership',
    'seeking higher salary':           'Business Challenges',
    'better work-life balance':        'Business Challenges',
    'personal reasons':                'Business Challenges'
  };

  readonly GROUP_COLORS: { [key: string]: string } = {
    'Role Redundancy':         '#6366F1',
    'Career Growth':           '#8B5CF6',
    'Management & Leadership': '#EC4899',
    'Business Challenges':     '#F59E0B'
  };

  constructor(
    private exitAnalysisService: ChartsSer,
    private snackBar: MatSnackBar,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const now = new Date();
    this.startDateObj = new Date(now.getFullYear(), 0, 1);
    this.endDateObj = now;
    this.syncDatesAndLoad();
  }

  private formatDate(date: Date): string {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const dd = date.getDate().toString().padStart(2, '0');
    return `${dd} ${months[date.getMonth()]} ${date.getFullYear()}`;
  }

  private syncDatesAndLoad(): void {
    if (this.startDateObj) this.startDate = this.formatDate(this.startDateObj);
    if (this.endDateObj)   this.endDate   = this.formatDate(this.endDateObj);
    this.loadReportData();
  }

  onStartDatePicked(date: Date | null): void {
    if (date) {
      this.startDateObj = date;
      this.startDate = this.formatDate(date);
      this.loadReportData();
    }
  }

  onEndDatePicked(date: Date | null): void {
    if (date) {
      this.endDateObj = date;
      this.endDate = this.formatDate(date);
      this.loadReportData();
    }
  }

  onDeptChange(): void {
    this.loadReportData();
  }

  goBack(): void {
    this.router.navigate(['/dash']);
  }

  // Navigate to exit-reasons page, passing all raw API data via router state
  viewAllReasons(): void {
    if (!this.reportData) return;

    const totalExits = this.reportData.summary.total_exits;
    const dept = this.selectedDepartment || 'All Departments';
    const title = `Total ${totalExits} Exits From ${dept}`;

    this.router.navigate(['/exit-reasons'], {
      state: {
        title,
        startDate: this.startDate,
        endDate:   this.endDate,
        reasonCounts:      this.reportData.reason_counts,
        feedbackByReason:  this.reportData.feedback_by_reason,
        overallPercentage: this.reportData.overall_percentage,
      }
    });
  }

  getLegendItems(): Array<{ label: string; color: string }> {
    return this.doughnutChartLabels.map((label, i) => ({
      label,
      color: this.GROUP_COLORS[label] ?? this.COLORS[i]
    }));
  }

  loadReportData(): void {
    if (!this.startDate || !this.endDate) return;
    this.isLoading = true;
    this.cdr.detectChanges();

    this.exitAnalysisService.getReportData(
      this.startDate,
      this.endDate,
      this.selectedDepartment || undefined
    ).subscribe({
      next: (data) => {
        this.reportData = data;
        this.processChartData(data);
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading report data:', err);
        this.snackBar.open('Error loading report data', 'Close', { duration: 3000 });
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  processChartData(data: ReportData): void {
    if (!this.selectedDepartment) {
      this.departments = Object.keys(data.exits_by_department);
    }

    // Donut chart — group raw reasons into 4 categories
    const grouped: { [key: string]: number } = {
      'Role Redundancy': 0, 'Career Growth': 0,
      'Management & Leadership': 0, 'Business Challenges': 0
    };
    Object.entries(data.overall_percentage).forEach(([reason, pctStr]) => {
      const pct = parseFloat(pctStr);
      const group = this.REASON_GROUPS[reason];
      if (group && pct > 0) grouped[group] += pct;
    });

    this.doughnutChartLabels = Object.keys(grouped).filter(k => grouped[k] > 0);
    this.doughnutChartData = {
      labels: [...this.doughnutChartLabels],
      datasets: [{
        data: this.doughnutChartLabels.map(l => Math.round(grouped[l])),
        backgroundColor: this.doughnutChartLabels.map(l => this.GROUP_COLORS[l]),
        borderWidth: 0,
        hoverOffset: 10
      }]
    };

    // Department bars — % of total exits
    const totalExits = data.summary.total_exits || 1;
    const deptEntries = Object.entries(data.exits_by_department).sort(([, a], [, b]) => b - a);
    this.departmentBreakdown = deptEntries.map(([dept, count], i) => ({
      label: dept,
      count,
      percentage: Math.round((count / totalExits) * 100),
      color: this.COLORS[i % this.COLORS.length]
    }));

    // Reason bars — only when a dept is selected
    if (this.selectedDepartment) {
      const totalReasons = Object.values(data.reason_counts).reduce((a, b) => a + b, 0) || 1;
      const reasonEntries = Object.entries(data.reason_counts)
        .filter(([, cnt]) => cnt > 0)
        .sort(([, a], [, b]) => b - a);
      this.reasonBreakdown = reasonEntries.map(([reason, count], i) => ({
        label: reason.charAt(0).toUpperCase() + reason.slice(1),
        count,
        percentage: Math.round((count / totalReasons) * 100),
        color: this.COLORS[i % this.COLORS.length]
      }));
    } else {
      this.reasonBreakdown = [];
    }
  }
}










