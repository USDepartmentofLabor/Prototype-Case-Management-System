import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectCustomFieldComponent } from './select-custom-field.component';

describe('SelectCustomFieldComponent', () => {
  let component: SelectCustomFieldComponent;
  let fixture: ComponentFixture<SelectCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SelectCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
