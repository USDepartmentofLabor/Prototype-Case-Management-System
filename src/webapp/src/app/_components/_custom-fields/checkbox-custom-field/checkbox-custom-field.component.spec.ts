import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CheckboxCustomFieldComponent } from './checkbox-custom-field.component';

describe('CheckboxCustomFieldComponent', () => {
  let component: CheckboxCustomFieldComponent;
  let fixture: ComponentFixture<CheckboxCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CheckboxCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CheckboxCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
