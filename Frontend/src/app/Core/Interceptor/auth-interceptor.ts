import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const isFormData = req.body instanceof FormData;

  if (!isFormData) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'ngrok-skip-browser-warning': 'true'
  };
 return next(req.clone({ setHeaders: headers })).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('HTTP Error:', error);
        throw error;
      })
    );
  } else {
    const headers = {
      'Accept': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    };

 return next(req.clone({ setHeaders: headers })).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('HTTP Error:', error);
        throw error;
      })
    );
  }
      
}