import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TextCustomFieldComponent } from './text-custom-field.component';

describe('TextCustomFieldComponent', () => {
  let component: TextCustomFieldComponent;
  let fixture: ComponentFixture<TextCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TextCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TextCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
