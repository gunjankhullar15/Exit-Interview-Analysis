import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExitReason } from './exit-reason';

describe('ExitReason', () => {
  let component: ExitReason;
  let fixture: ComponentFixture<ExitReason>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExitReason]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExitReason);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
