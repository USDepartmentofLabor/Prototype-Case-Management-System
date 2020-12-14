import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TextareaCustomFieldComponent } from './textarea-custom-field.component';

describe('TextareaCustomFieldComponent', () => {
  let component: TextareaCustomFieldComponent;
  let fixture: ComponentFixture<TextareaCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TextareaCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TextareaCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
