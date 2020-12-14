import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditActivityNameComponent } from './edit-activity-name.component';

describe('EditActivityNameComponent', () => {
  let component: EditActivityNameComponent;
  let fixture: ComponentFixture<EditActivityNameComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditActivityNameComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditActivityNameComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
