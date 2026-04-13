import { FeedbackForm } from './Features/Components/Feedback-form/Pages/feedback-form/feedback-form';
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Login } from './Features/Components/Login/Pages/login/login';
import { Analysis1 } from './Features/Components/Analysis/Services/analysis1';
import { Dash1 } from './Features/Components/Dashboard/Services/dash1';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('feedback');
}
