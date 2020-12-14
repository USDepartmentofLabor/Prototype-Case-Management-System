import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DateCustomFieldComponent } from './date-custom-field.component';

describe('DateCustomFieldComponent', () => {
  let component: DateCustomFieldComponent;
  let fixture: ComponentFixture<DateCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DateCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DateCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
