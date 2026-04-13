import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MaterialModule } from '../../../../../Shared/Modules/MaterialModule';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { Subject, takeUntil } from 'rxjs';
import { FeedbackFormService } from '../../Services/feedback-form';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-feedback-form',
  standalone: true,
  imports: [CommonModule, MaterialModule, FormsModule, MatTableModule, MatPaginatorModule],
  templateUrl: './feedback-form.html',
  styleUrls: ['./feedback-form.scss']
})


export class FeedbackForm implements OnInit, OnDestroy {
  selectedFile: File | null = null;
  isDragOver = false;
  isUploading = false;
  isUploaded = false;
  isGenerating = false;

  private destroy$ = new Subject<void>();

  constructor(
    public dialogRef: MatDialogRef<FeedbackForm>,
    private snackBar: MatSnackBar,
    private feedbackFormService: FeedbackFormService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {}

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);

      input.value = '';
    }
  }

  private handleFile(file: File): void {
    if (!this.isValidFileType(file)) {
      this.showErrorSnackBar('Please upload an Excel or CSV file');
      return;
    }

    if (!this.isValidFileSize(file)) {
      this.showErrorSnackBar('File size should not exceed 10MB');
      return;
    }

    this.selectedFile = file;
    this.isUploaded = false;
    this.isUploading = false;
    this.isGenerating = false;
    this.cdr.detectChanges();
    
    this.showSuccessSnackBar(`File "${file.name}" selected successfully`);
  }

  private isValidFileType(file: File): boolean {
    const allowedTypes = [
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv'
    ];

    return (
      allowedTypes.includes(file.type) ||
      file.name.endsWith('.xlsx') ||
      file.name.endsWith('.xls') ||
      file.name.endsWith('.csv')
    );
  }

  private isValidFileSize(file: File): boolean {
    const maxSize = 10 * 1024 * 1024; // 10MB
    return file.size <= maxSize;
  }

  onUploadClick(): void {
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    fileInput?.click();
  }

  onUploadFile(): void {
    if (!this.selectedFile) {
      this.showErrorSnackBar('Please select a file first');
      return;
    }

    console.log('🚀 Starting upload for:', this.selectedFile.name);
    
    this.isUploading = true;
    this.isUploaded = false;
    this.isGenerating = false;
    
    this.cdr.detectChanges();

    this.feedbackFormService
      .uploadFile(this.selectedFile)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: any) => {
          console.log('✅ Upload SUCCESS:', response);
          
          this.isUploading = false;
          this.isUploaded = true;
          this.isGenerating = false;
          
          console.log('States after upload:', {
            isUploading: this.isUploading,
            isUploaded: this.isUploaded,
            isGenerating: this.isGenerating
          });
          
        
          this.cdr.detectChanges();
          
          this.showSuccessSnackBar('File uploaded successfully!');
        },
        error: (error: any) => {
          console.error('❌ Upload ERROR:', error);
          
          this.isUploading = false;
          this.isUploaded = false;
          this.isGenerating = false;
          
          this.cdr.detectChanges();
          
          this.showErrorSnackBar(
            error.error?.message || 
            error.message || 
            'Failed to upload file. Please try again.'
          );
        }
      });
  }

  onGenerateAnalysis(): void {
    if (!this.isUploaded) {
      this.showErrorSnackBar('Please upload the file first');
      return;
    }

    console.log('🚀 Starting generate analysis');
    
    this.isGenerating = true;
    this.cdr.detectChanges();

    this.feedbackFormService
      .generateAnalysis()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: any) => {
          console.log('✅ Generate SUCCESS:', response);
          
          this.isGenerating = false;
          this.cdr.detectChanges();
          
          this.showSuccessSnackBar('Analysis generated successfully!');
          
          this.dialogRef.close({
            success: true,
            data: response,
            file: this.selectedFile
          });
        },
        error: (error: any) => {
          console.error('❌ Generate ERROR:', error);
          
          this.isGenerating = false;
          this.cdr.detectChanges();
          
          this.showErrorSnackBar(
            error.error?.message || 
            error.message || 
            'Failed to generate analysis. Please try again.'
          );
        }
      });
  }

  onDiscard(): void {
    console.log('Discard clicked. Uploaded:', this.isUploaded);
    
    if (this.isUploaded) {
      this.deleteFile();
    }

    this.resetAllStates();
    this.dialogRef.close();
  }

  private resetAllStates(): void {
    this.selectedFile = null;
    this.isDragOver = false;
    this.isUploading = false;
    this.isUploaded = false;
    this.isGenerating = false;
    this.cdr.detectChanges();
  }

  private deleteFile(): void {
    console.log('🗑️ Deleting uploaded file...');
    this.feedbackFormService
      .deletePendingResponses()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          console.log('✅ File deleted successfully');
        },
        error: (error: any) => {
          console.error('❌ Delete error:', error);
        }
      });
  }

  private showSuccessSnackBar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar'],
      verticalPosition: 'top',
      horizontalPosition: 'right'
    });
  }

  private showErrorSnackBar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar'],
      verticalPosition: 'top',
      horizontalPosition: 'right'
    });
  }
}