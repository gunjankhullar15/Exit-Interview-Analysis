import { Injectable } from '@angular/core';
import { environment } from '../../../../Core/Environment/Environment';
import { HttpClient } from '@angular/common/http';
import { AnalysisReport } from '../../../../Shared/Interfaces/AnalysisReport';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})

export class Analysis1 {
  private baseUrl = environment.PREVIEW_BASE_URL;

  constructor(private http: HttpClient) {}

  getAnalysisReport(employeeCode: string): Observable<AnalysisReport> {
    
    
    return this.http.get<AnalysisReport>( `${this.baseUrl}/report/${employeeCode}`);
  }
}