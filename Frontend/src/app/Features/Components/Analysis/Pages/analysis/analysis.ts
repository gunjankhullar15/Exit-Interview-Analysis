import { ChangeDetectorRef, Component,OnInit } from '@angular/core';
import { Navbar } from "../../../Navbar/Pages/navbar/navbar";
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Analysis1 } from '../../Services/analysis1';
import { AnalysisReport } from '../../../../../Shared/Interfaces/AnalysisReport';
import { CommonModule } from '@angular/common';
import { MaterialModule } from "../../../../../Shared/Modules/MaterialModule";

@Component({
  selector: 'app-analysis',
  imports: [Navbar, CommonModule, MaterialModule],
  templateUrl: './analysis.html',
  styleUrl: './analysis.scss',
  standalone: true
})

export class Analysis implements OnInit {
  isLoading: boolean = false;

  employeeData = {
    name: '',
    hrbp: '',
    designation: '',
    code: '',
    l1Manager: '',
    exitDate: '',
    department: '',
    l2Manager: '',
    resignationDate: ''
  };

  mcqData = {
    selectedAnswer: '',
    calculatedRating: '',
    sentimentScore: ''
  };

  subjectiveData = {
    positiveRemarks: '',
    negativeRemarks: '',
    otherIdeal: ''
  };

  summaryData = {
    content: ''
  };

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private analysisService: Analysis1,
    private snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    const employeeCode = this.route.snapshot.paramMap.get('employeeCode');
    
    if (employeeCode) {
      this.loadAnalysisReport(employeeCode);
    } else {
      this.snackBar.open('No employee code provided', 'Close', { duration: 3000 });
      this.router.navigate(['/dash']);
    }
  }

  loadAnalysisReport(employeeCode: string): void {
    console.log('=== loadAnalysisReport CALLED ===');
    console.log('Employee Code:', employeeCode);
    console.log('isLoading set to TRUE');
    this.isLoading = true;
    
   
    const timeoutId = setTimeout(() => {
      console.error('=== TIMEOUT: No response from API in 10 seconds ===');
      if (this.isLoading) {
        this.isLoading = false;
        this.snackBar.open('Request timed out. Please try again.', 'Close', { duration: 3000 });
      }
    }, 10000);
    
    console.log('Calling analysisService.getAnalysisReport...');
    
    const subscription = this.analysisService.getAnalysisReport(employeeCode);
    console.log('Subscription object:', subscription);
    console.log('Subscription type:', typeof subscription);
    
    subscription.subscribe({
      next: (data: any) => {
        clearTimeout(timeoutId); // Clear the timeout
        console.log('=== SUBSCRIBE NEXT TRIGGERED ===');
        console.log('=== FULL API Response ===');
        console.log(data);
        console.log('=== Data Type ===', typeof data);
        console.log('=== Data Keys ===', Object.keys(data));
        
        // Try to find the actual data location
        let actualData = data;
        
        // Check various possible nesting patterns
        if (data.data) {
          console.log('Found data.data');
          actualData = data.data;
        }
        
        if (actualData.full_analysis_json) {
          console.log('Found full_analysis_json');
          actualData = actualData.full_analysis_json;
        }
        
        console.log('=== Actual Data to Map ===');
        console.log(actualData);
        console.log('=== Actual Data Keys ===', Object.keys(actualData));
        
        this.mapDataToComponents(actualData);
        
        console.log('Setting isLoading to FALSE');
        this.isLoading = false;
        console.log('isLoading is now:', this.isLoading);
        
        // Force change detection
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        clearTimeout(timeoutId); // Clear the timeout
        console.error('=== SUBSCRIBE ERROR TRIGGERED ===');
        console.error('Error loading analysis report:', error);
        this.snackBar.open('Error loading analysis report', 'Close', { duration: 3000 });
        console.log('Setting isLoading to FALSE (error case)');
        this.isLoading = false;
      },
      complete: () => {
        console.log('=== SUBSCRIBE COMPLETE TRIGGERED ===');
      }
    });
    
    console.log('Subscribe called, waiting for response...');
  }

  mapDataToComponents(analysis: any): void {
    console.log('=== Starting mapDataToComponents ===');
    console.log('Analysis object:', analysis);
    
    // Map employee details with extensive logging
    console.log('Employee name options:', {
      name: analysis.name,
      employee_name: analysis.employee_name,
      Name: analysis.Name
    });
    
    this.employeeData = {
      name: analysis.name || analysis.employee_name || analysis.Name || 'N/A',
      hrbp: analysis.hrbp_name || analysis.hrbp || analysis.HRBP || 'N/A',
      designation: analysis.designation || analysis.Designation || 'N/A',
      code: analysis.employee_code || analysis.code || analysis.Code || 'N/A',
      l1Manager: analysis.l1_manager || analysis.l1Manager || analysis.L1Manager || 'N/A',
      exitDate: this.formatDate(analysis.exit_date || analysis.exitDate || analysis.ExitDate),
      department: analysis.department || analysis.Department || 'N/A',
      l2Manager: analysis.l2_manager || analysis.l2Manager || analysis.L2Manager || 'N/A',
      resignationDate: this.formatDate(analysis.resignation_date || analysis.resignationDate || analysis.ResignationDate)
    };

    console.log('=== Mapped Employee Data ===');
    console.log(this.employeeData);

    const objective = analysis.objective_analysis || analysis.objectiveAnalysis || {};
    console.log('Objective analysis:', objective);
    
    this.mcqData = {
      selectedAnswer: String(objective.total_questions || objective.totalQuestions || 0),
      calculatedRating: `${objective.positive_percentage || objective.positivePercentage || 0}`,
      sentimentScore: `${objective.negative_percentage || objective.negativePercentage || 0}`
    };

    console.log('=== Mapped MCQ Data ===');
    console.log(this.mcqData);
    const subjective = analysis.subjective_analysis || analysis.subjectiveAnalysis || {};
    console.log('Subjective analysis:', subjective);
    
    const sentimentDefs = subjective['Sentiment Definitions'] ||
                         subjective.Sentiment_Definitions || 
                         subjective.sentiment_definitions || 
                         subjective.SentimentDefinitions || {};
    
    console.log('Sentiment definitions:', sentimentDefs);
    
    this.subjectiveData = {
      positiveRemarks: this.formatRemarks(
        sentimentDefs.positive_sentiments || 
        sentimentDefs.positiveSentiments || 
        sentimentDefs.positive
      ),
       otherIdeal: this.formatRemarks(
        sentimentDefs.neutral_sentiments || 
        sentimentDefs.neutralSentiments || 
        sentimentDefs.neutral
      ),
      negativeRemarks: this.formatRemarks(
        sentimentDefs.negative_sentiments || 
        sentimentDefs.negativeSentiments || 
        sentimentDefs.negative
      ),
    };

    this.summaryData = {
      content: subjective.overall_summary || 
               subjective.overallSummary || 
               subjective.summary || 
               'No summary available'
    };

    setTimeout(() => {
      console.log('=== Current component state ===');
      console.log('employeeData:', this.employeeData);
      console.log('mcqData:', this.mcqData);
      console.log('subjectiveData:', this.subjectiveData);
      console.log('summaryData:', this.summaryData);
    }, 100);
  }

  formatRemarks(remarks: any): string {
    console.log('Formatting remarks:', remarks, 'Type:', typeof remarks);
    
    if (!remarks) {
      return 'No remarks available';
    }
    
    
    if (typeof remarks === 'string') {
      return remarks;
    }
    
   
    if (Array.isArray(remarks)) {
      if (remarks.length === 0) {
        return 'No remarks available';
      }
      
      return remarks
        .map(item => {
        
          const cleaned = item.trim().replace(/^-\s*/, '');
      
          return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
        })
        .join('\n');
    }
    
    if (typeof remarks === 'object') {
      return JSON.stringify(remarks, null, 2);
    }
    
    return 'No remarks available';
  }

  formatDate(dateStr: any): string {
    if (!dateStr) return 'N/A';
    
    console.log('Formatting date:', dateStr, 'Type:', typeof dateStr);
    
    try {
      let date: Date;
      
    
      if (dateStr instanceof Date) {
        date = dateStr;
      }
      
      else if (typeof dateStr === 'string' && dateStr.includes(' ')) {
        const parts = dateStr.split(' ');
        const monthMap: { [key: string]: number } = {
          'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
          'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11,
          'January': 0, 'February': 1, 'March': 2, 'April': 3, 'June': 5,
          'July': 6, 'August': 7, 'September': 8, 'October': 9, 'November': 10, 'December': 11
        };
        
        if (parts.length >= 3) {
          const day = parseInt(parts[0]);
          const month = monthMap[parts[1]];
          const year = parseInt(parts[2]);
          
          if (!isNaN(day) && month !== undefined && !isNaN(year)) {
            date = new Date(year, month, day);
          } else {
            return dateStr;
          }
        } else {
          date = new Date(dateStr);
        }
      }
    
      else {
        date = new Date(dateStr);
      }
      
      if (isNaN(date.getTime())) {
        console.log('Invalid date, returning original:', dateStr);
        return String(dateStr);
      }
      
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
    } catch (error) {
      console.error('Date parsing error:', error);
      return String(dateStr);
    }
  }

  onBack(): void {
    this.router.navigate(['/dash']);
  }

  onClose(): void {
    console.log('Close button clicked');
  }
}