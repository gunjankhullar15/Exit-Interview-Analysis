import { Routes } from '@angular/router';
import { Login } from './Features/Components/Login/Pages/login/login';
import { Analysis } from './Features/Components/Analysis/Pages/analysis/analysis';
import { FeedbackForm } from './Features/Components/Feedback-form/Pages/feedback-form/feedback-form';
import { Dashboard } from './Features/Components/Dashboard/Pages/dashboard/dashboard';
import { AuthGuard } from './Core/Guards/authGuard';
import { Charts } from './Features/Components/Report/Pages/charts/charts/charts';
import { LoginGuard } from './Core/Guards/loginGuard';
import { ExitReasons } from './Features/Components/Exit/Pages/exit-reason/exit-reason';

export const routes: Routes = [
  
    {path: '', redirectTo: 'login', pathMatch: 'full'},
 
    {path:'login',component:Login, canActivate: [LoginGuard]},

    {path: 'analysis/:employeeCode',component: Analysis, canActivate: [AuthGuard]},
    
    {path:'feedback',component:FeedbackForm, canActivate: [AuthGuard]},
   
    {path:'dash',component:Dashboard, canActivate: [AuthGuard]},
    
    {path:'report',component:Charts, canActivate: [AuthGuard]},

    {path:'exit-reasons',component:ExitReasons, canActivate: [AuthGuard]},
];

