import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NewCaseDefinitionComponent } from './new-case-definition.component';

describe('NewCaseDefinitionComponent', () => {
  let component: NewCaseDefinitionComponent;
  let fixture: ComponentFixture<NewCaseDefinitionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NewCaseDefinitionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NewCaseDefinitionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
