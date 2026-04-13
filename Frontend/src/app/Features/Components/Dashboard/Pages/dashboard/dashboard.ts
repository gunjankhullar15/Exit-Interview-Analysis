import { Dash } from './../../../../../Shared/Interfaces/Dash';
import { AfterViewInit, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { MatPaginator } from '@angular/material/paginator';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { MaterialModule } from '../../../../../Shared/Modules/MaterialModule';
import { Navbar } from '../../../Navbar/Pages/navbar/navbar';
import { FeedbackForm } from '../../../Feedback-form/Pages/feedback-form/feedback-form';
import { Dash1 } from '../../Services/dash1';




@Component({
  selector: 'app-dashboard',
  imports: [CommonModule,MaterialModule,FormsModule,Navbar],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})


export class Dashboard implements OnInit, AfterViewInit {
  displayedColumns: string[] = [
    'SNo',
    'employee_code',
    'name',
    'department',
    'designation',
    'date_of_resignation',
    'exit_date',
    'l1_manager',
    // 'l2_manager',
    'hrbp_name',
    'overall_sentiment',
    'exit_reason'
  ];

  filterOptions = [
    { value: 'all', label: 'All Fields' },
    { value: 'employee_code', label: 'Emp Code' },
    { value: 'name', label: 'Name' },
    { value: 'department', label: 'Department' },
    { value: 'designation', label: 'Designation' },
    { value: 'l1_manager', label: 'L1 Manager' },
    // { value: 'l2_manager', label: 'L2 Manager' },
    { value: 'hrbp_name', label: 'HRBP' },
    { value: 'overall_sentiment', label: 'Overall Sentiments' },
    { value: 'exit_reason', label: 'Exit Reason' }
  ];

  dataSource: MatTableDataSource<Dash>;
  isLoading: boolean = false;
  isDownloading: boolean = false;

  searchText: string = '';
  selectedSearchField: string = 'all';
  selectedDepartment: string = '';
  selectedEmpCode: string = '';
  selectedResignationDate: any = null;
  selectedExitDate: any = null;
  selectedRow: number | null = null;

  @ViewChild(MatPaginator) paginator!: MatPaginator;


  constructor(
    private router: Router,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private dashboardService: Dash1,
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {
    this.dataSource = new MatTableDataSource<Dash>([]);
  }

  ngOnInit(): void {
    this.loadDashboardData();
    this.checkAuthentication();
  }


private checkAuthentication(): void {
   
    const isLoggedLocal = typeof window !== 'undefined' && localStorage.getItem('isLoggedIn') === 'true';
    const isLoggedSession = typeof window !== 'undefined' && sessionStorage.getItem('isLoggedIn') === 'true';

    if (!isLoggedLocal && !isLoggedSession) {
    
      this.router.navigate(['/login']);
    }
  }

  ngAfterViewInit(): void {
    if (this.paginator) {
      this.paginator.pageSize = 10;
      this.dataSource.paginator = this.paginator;
    }
  }



loadDashboardData(): void {
  this.isLoading = true;
  this.dashboardService.getDashboardData().subscribe({
    next: (data: Dash[]) => {
      this.dataSource.data = data;
      this.isLoading = false;
  
      this.debugDates();
      
      this.applyFilter();
    },
    error: (error: any) => {
      console.error('Error loading dashboard data:', error);
      this.snackBar.open('Error loading data', 'Close', { duration: 3000 });
      this.isLoading = false;
    }
  });
}


  UploadPage(): void {
    const dialogRef = this.dialog.open(FeedbackForm, {
      width: '550px',
      maxWidth: '90vw',
      disableClose: false,
      panelClass: 'upload-dialog',
      backdropClass: 'upload-dialog-backdrop'
    });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedSearchField = 'all';
    this.selectedDepartment = '';
    this.selectedEmpCode = '';
    this.selectedResignationDate = null;
    this.selectedExitDate = null;
    this.applyFilter();
  }

  

applyFilter(): void {
  this.dataSource.filterPredicate = (data: Dash, filter: string) => {
    const searchStr = this.searchText.toLowerCase();

  
    let matchesSearch = false;
    if (!this.searchText) {
      matchesSearch = true;
    } else if (this.selectedSearchField === 'all') {
      matchesSearch = 
        data.name?.toLowerCase().includes(searchStr) ||
        data.employee_code?.toLowerCase().includes(searchStr) ||
        data.department?.toLowerCase().includes(searchStr) ||
        data.designation?.toLowerCase().includes(searchStr) ||
        data.l1_manager?.toLowerCase().includes(searchStr) ||
        // data.l2_manager?.toLowerCase().includes(searchStr) ||
        data.hrbp_name?.toLowerCase().includes(searchStr) ||
        data['exit_reason']?.toLowerCase().includes(searchStr) ||
        (data.overall_sentiment?.toLowerCase().includes(searchStr) ?? false);
       
        
    } else {
      const fieldValue = (data as any)[this.selectedSearchField];
      matchesSearch = fieldValue?.toLowerCase().includes(searchStr) || false;
    }

    const matchesDepartment = !this.selectedDepartment ||
      data.department === this.selectedDepartment;

    const matchesEmpCode = !this.selectedEmpCode ||
      data.employee_code === this.selectedEmpCode;


    let matchesDateRange = true;
    
    if (this.selectedResignationDate || this.selectedExitDate) {
      const resignationDate = this.parseDate(data.date_of_resignation);
      const exitDate = this.parseDate(data.exit_date);
      
      if (this.selectedResignationDate) {
        const startDate = new Date(this.selectedResignationDate);
        startDate.setHours(0, 0, 0, 0);
        
        if (resignationDate) {
          matchesDateRange = matchesDateRange && resignationDate >= startDate;
        } else {
          matchesDateRange = false;
        }
      }
      
      if (this.selectedExitDate && matchesDateRange) {
        const endDate = new Date(this.selectedExitDate);
        endDate.setHours(23, 59, 59, 999);
        
        if (exitDate) {
          matchesDateRange = matchesDateRange && exitDate <= endDate;
        } else {
          matchesDateRange = false;
        }
      }
    }

    return matchesSearch && matchesDepartment && matchesEmpCode && matchesDateRange;
  };

  this.dataSource.filter = Math.random().toString();
  if (this.dataSource.paginator) {
    this.dataSource.paginator.firstPage();
  }
  
  
  console.log('Filter applied:', {
    searchText: this.searchText,
    selectedSearchField: this.selectedSearchField,
    selectedResignationDate: this.selectedResignationDate,
    selectedExitDate: this.selectedExitDate,
    filteredDataCount: this.dataSource.filteredData.length
  });
}


private parseDate(dateStr: string): Date | null {
  if (!dateStr || dateStr.trim() === '') return null;

  try {
  
    dateStr = dateStr.trim();
    
  
    let date: Date | null = null;
    
    
    if (dateStr.includes('-')) {
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        const part1 = parseInt(parts[0]);
        const part2 = parseInt(parts[1]);
        const part3 = parseInt(parts[2]);
        
        if (part1 > 12) {
         
          date = new Date(part3, part2 - 1, part1);
        } else if (part2 > 12) {
        
          date = new Date(part3, part1 - 1, part2);
        } else {
         
          date = new Date(part3, part2 - 1, part1);
        }
      }
    }
    
    else if (dateStr.includes('/')) {
      const parts = dateStr.split('/');
      if (parts.length === 3) {
        const part1 = parseInt(parts[0]);
        const part2 = parseInt(parts[1]);
        const part3 = parseInt(parts[2]);
        
        if (part1 > 12) {
          
          date = new Date(part3, part2 - 1, part1);
        } else if (part2 > 12) {
      
          date = new Date(part3, part1 - 1, part2);
        } else {
        
          date = new Date(part3, part2 - 1, part1);
        }
      }
    }
   
    else {
      date = new Date(dateStr);
    }
    

    if (date && !isNaN(date.getTime())) {
      date.setHours(0, 0, 0, 0);
      return date;
    }
    
    return null;
  } catch (error) {
    console.error('Error parsing date:', dateStr, error);
    return null;
  }
}

debugDates(): void {
  console.log('Sample dates from data:');
  this.dataSource.data.slice(0, 5).forEach(item => {
    console.log({
      employee: item.employee_code,
      resignation: item.date_of_resignation,
      resignationParsed: this.parseDate(item.date_of_resignation),
      exit: item.exit_date,
      exitParsed: this.parseDate(item.exit_date)
    });
  });
}


  private compareDates(dateStr: string, selectedDate: any): boolean {
    if (!dateStr || !selectedDate) return false;

    try {
      const parts = dateStr.split('-');
      let dataDate: Date;

      if (parseInt(parts[0]) > 12) {
        dataDate = new Date(
          parseInt(parts[2]),
          parseInt(parts[1]) - 1,
          parseInt(parts[0])
        );
      } else {
        dataDate = new Date(
          parseInt(parts[2]),
          parseInt(parts[0]) - 1,
          parseInt(parts[1])
        );
      }

      const selectedDateObj = new Date(selectedDate);
      return dataDate.toDateString() === selectedDateObj.toDateString();
    } catch (error) {
      console.error('Error comparing dates:', error);
      return false;
    }
  }

  downloadFilteredData(): void {
    const filteredData = this.dataSource.filteredData;
    
    if (filteredData.length === 0) {
      this.snackBar.open('No data to download', 'Close', { duration: 3000 });
      return;
    }

    const employeeCodes = filteredData
      .map(item => item.employee_code)
      .filter(code => code);

    if (employeeCodes.length === 0) {
      this.snackBar.open('No valid employee codes found', 'Close', { duration: 3000 });
      return;
    }

    this.isDownloading = true;
    
    
    const baseUrl = `https://confabulatory-kindlier-danyelle.ngrok-free.dev/download-employee-details-csv/`;
    const queryParams = employeeCodes.map(code => `employee_codes=${encodeURIComponent(code)}`).join('&');
    const apiUrl = `${baseUrl}?${queryParams}`;

    this.http.get(apiUrl, { 
      responseType: 'blob',
      observe: 'response'
    }).subscribe({
      next: (response) => {
        const blob = response.body;
        if (blob) {
        
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          
         
          const contentDisposition = response.headers.get('Content-Disposition');
          let filename = 'employee_details.csv';
          
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
              filename = filenameMatch[1];
            }
          }
          
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          
          this.snackBar.open('Download successful', 'Close', { duration: 3000 });
        }
       
        this.isDownloading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error downloading data:', error);
        this.snackBar.open('Error downloading data', 'Close', { duration: 3000 });
        this.isDownloading = false;
        this.cdr.detectChanges();
      }
    });
  }

  onRowClick(row: Dash): void {
    this.selectedRow = row.SNo!;
    console.log('Row clicked:', row);
    this.router.navigate([`/analysis/${row.employee_code}`], {
      state: { employee: row }
    });
  }

  getRowClass(row: Dash): string {
    return this.selectedRow === row.SNo ? 'selected-row' : '';
  }


navigateToReport(): void {
  this.router.navigate(['/report']);
}



  getSearchPlaceholder(): string {
    if (this.selectedSearchField === 'all') {
      return 'Search all fields';
    }
    const selectedOption = this.filterOptions.find(o => o.value === this.selectedSearchField);
    return selectedOption ? `Search ${selectedOption.label}` : 'Search';
  }
}