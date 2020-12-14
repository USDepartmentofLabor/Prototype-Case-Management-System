import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ActivityDefinitionFormComponent } from './activity-definition-form.component';

describe('ActivityDefinitionFormComponent', () => {
  let component: ActivityDefinitionFormComponent;
  let fixture: ComponentFixture<ActivityDefinitionFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ActivityDefinitionFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ActivityDefinitionFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
