import { TestBed } from '@angular/core/testing';

import { FeedbackForm } from './feedback-form';

describe('FeedbackForm', () => {
  let service: FeedbackForm;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FeedbackForm);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
