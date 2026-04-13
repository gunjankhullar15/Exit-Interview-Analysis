import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../../../Core/Environment/Environment';
import { map, Observable } from 'rxjs';
import { Dash } from '../../../../Shared/Interfaces/Dash';

@Injectable({
  providedIn: 'root',
})
export class Dash1 {
 private readonly http = inject(HttpClient);
  private readonly BASE_URL = environment.PREVIEW_BASE_URL;


getDashboardData(): Observable<Dash[]> {
    return this.http.get<Dash[]>(`${this.BASE_URL}/reports`).pipe(
      map((data) => 
        data.map((item, index) => ({
          ...item,
          SNo: index + 1
        }))
      )
    );
  }
  }


