import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RadioButtonCustomFieldComponent } from './radio-button-custom-field.component';

describe('RadioButtonCustomFieldComponent', () => {
  let component: RadioButtonCustomFieldComponent;
  let fixture: ComponentFixture<RadioButtonCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RadioButtonCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RadioButtonCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
