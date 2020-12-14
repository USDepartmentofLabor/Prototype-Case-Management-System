import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NewActivityModalComponent } from './new-activity-modal.component';

describe('NewActivityModalComponent', () => {
  let component: NewActivityModalComponent;
  let fixture: ComponentFixture<NewActivityModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NewActivityModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NewActivityModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
