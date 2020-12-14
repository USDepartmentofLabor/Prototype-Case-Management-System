import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditActivityDescriptionComponent } from './edit-activity-description.component';

describe('EditActivityDescriptionComponent', () => {
  let component: EditActivityDescriptionComponent;
  let fixture: ComponentFixture<EditActivityDescriptionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditActivityDescriptionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditActivityDescriptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
