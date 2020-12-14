import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NumberCustomFieldComponent } from './number-custom-field.component';

describe('NumberCustomFieldComponent', () => {
  let component: NumberCustomFieldComponent;
  let fixture: ComponentFixture<NumberCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NumberCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NumberCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
