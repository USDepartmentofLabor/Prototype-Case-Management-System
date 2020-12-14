import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MetabaseDashboardComponent } from './metabase-dashboard.component';

describe('MetabaseDashboardComponent', () => {
  let component: MetabaseDashboardComponent;
  let fixture: ComponentFixture<MetabaseDashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MetabaseDashboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MetabaseDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
