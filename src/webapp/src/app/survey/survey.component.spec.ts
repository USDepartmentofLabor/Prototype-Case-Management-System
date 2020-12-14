import { ComponentFixture, TestBed, async } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { HeaderComponent } from '../_components';
import { SurveyComponent } from './survey.component';
import { NO_ERRORS_SCHEMA } from '@angular/core';


describe('SurveyComponent', () => {
    let component: SurveyComponent;
    let fixture: ComponentFixture<SurveyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        RouterTestingModule
      ],
      declarations: [
        HeaderComponent,
        SurveyComponent
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();
  }));


  it('should create the survey components', () => {
    fixture = TestBed.createComponent(SurveyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });
  
});