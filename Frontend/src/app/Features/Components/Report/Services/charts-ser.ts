import { Injectable } from '@angular/core';
import { environment } from '../../../../Core/Environment/Environment';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {ReportData} from '../../../../Shared/Interfaces/chartReport';




@Injectable({
  providedIn: 'root',
})

export class ChartsSer  {

  private readonly apiUrl = `${environment.API_BASE_URL}/graphical_report_data/`;

  constructor(private http: HttpClient) {}

  getReportData(startDate: string, endDate: string, department?: string): Observable<ReportData> {
    let params = new HttpParams()
      .set('start_date', startDate)
      .set('end_date', endDate);

    if (department) {
      params = params.set('department', department);
    }

    return this.http.get<ReportData>(this.apiUrl, { params });
  }
}