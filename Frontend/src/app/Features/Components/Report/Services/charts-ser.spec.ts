import { TestBed } from '@angular/core/testing';

import { ChartsSer } from './charts-ser';

describe('ChartsSer', () => {
  let service: ChartsSer;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChartsSer);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
