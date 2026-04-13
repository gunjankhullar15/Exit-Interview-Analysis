import { Injectable } from '@angular/core';
import { environment } from '../../../../Core/Environment/Environment';
import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';
import { UploadResponse } from '../../../../Shared/Interfaces/UploadResponse';
import { GenerateResponse } from '../../../../Shared/Interfaces/GenerateResponse';
import { DeleteResponse } from '../../../../Shared/Interfaces/DeleteResponse';

@Injectable({
  providedIn: 'root',
})


export class FeedbackFormService {
  private readonly BASE_URL = environment.PREVIEW_BASE_URL;

  constructor(private httpClient: HttpClient) {}

  
  uploadFile(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    return this.httpClient.post<UploadResponse>(`${this.BASE_URL}/upload-excel`, formData);
  }

  
  generateAnalysis(): Observable<GenerateResponse> {
    return this.httpClient.post<GenerateResponse>(`${this.BASE_URL}/Generate_llm_response/`, {});
  }

  
  deletePendingResponses(): Observable<DeleteResponse> {
    return this.httpClient.delete<DeleteResponse>(`${this.BASE_URL}/delete-pending-responses`);
  }
}