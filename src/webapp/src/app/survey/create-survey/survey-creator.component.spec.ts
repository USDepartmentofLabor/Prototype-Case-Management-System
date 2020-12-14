import { ComponentFixture, TestBed, async } from '@angular/core/testing';
import { HttpClientModule } from '@angular/common/http';
import { SurveyCreatorComponent } from './survey-creator.component';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ToastrModule } from 'ngx-toastr';
import { RouterTestingModule } from '@angular/router/testing';

describe('SurveyCreatorComponent', () => {
  let component: SurveyCreatorComponent;
  let fixture: ComponentFixture<SurveyCreatorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [FormsModule, HttpClientModule, RouterTestingModule.withRoutes([]), ToastrModule.forRoot()],
      declarations: [SurveyCreatorComponent],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();
  }));

  it('should create the survey component', () => {
    fixture = TestBed.createComponent(SurveyCreatorComponent);
    component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  it('should bind survey name value to input ', async(() => {
    fixture = TestBed.createComponent(SurveyCreatorComponent);

    // Update the title input
    const inputElement = fixture.debugElement.query(
      By.css('input[name="surveyName"]')
    ).nativeElement;
    inputElement.value = 'test survey';
    inputElement.dispatchEvent(new Event('input'));

    fixture.whenStable().then(() => {
      expect(inputElement.value).toEqual('test survey');
    });
  }));

  it('should throw an error if input is empty ', async(() => {
    fixture = TestBed.createComponent(SurveyCreatorComponent);
    let surveyHasError = false;
    const inputElement = fixture.debugElement.query(
      By.css('input[name="surveyName"]')
    ).nativeElement;
    inputElement.value = ' ';
    inputElement.dispatchEvent(new Event('input'));

    fixture.whenStable().then(() => {
      expect(inputElement.value).toEqual(' ');
      surveyHasError = true;
      expect(surveyHasError).toBeTruthy();
    });
  }));
});
