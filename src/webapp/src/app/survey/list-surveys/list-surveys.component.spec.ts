import { async, ComponentFixture, TestBed, fakeAsync } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientModule } from '@angular/common/http';
import { AnimatedLoaderComponent, HeaderComponent } from '../../_components/index';
import { ListSurveysComponent } from './list-surveys.component';
import { SurveyService } from '../../_services/index';
import { Router } from "@angular/router";
import { Location } from "@angular/common";
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { Angular2FontawesomeModule } from 'angular2-fontawesome';


describe('ListSurveysComponent', () => {
  let router: Router;
  let component: ListSurveysComponent;
  let fixture: ComponentFixture<ListSurveysComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule.withRoutes([]), HttpClientModule, Angular2FontawesomeModule],
      declarations: [ListSurveysComponent, AnimatedLoaderComponent, HeaderComponent,]
   
    }).compileComponents();

    router = TestBed.get(Router);
    location = TestBed.get(Location);
    router.initialNavigation();
  }));


  it('should create list component', () => {
    fixture = TestBed.createComponent(ListSurveysComponent);
    component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });


//   it('should display a different title', () => {
//     fixture = TestBed.createComponent(ListSurveysComponent);
//     fixture.detectChanges();
//     const compiled = fixture.debugElement.nativeElement;
//     expect(compiled.querySelector('h1').textContent).toContain('Surveys');
//   });

//   it('should\'t fetch data successfully if not called asynchronously', () =>{
//     let fixture = TestBed.createComponent(ListSurveysComponent);
//     let Component =  fixture.debugElement.componentInstance;
//     let dataService = fixture.debugElement.injector.get(SurveyService)
//     let spy = spyOn(dataService,'getSurvey')
//     spy.apply(null, [1])
//       fixture.detectChanges();
//       expect(Component.data).toBe(undefined);
//   });

//   it('should load survey based on id', () => {
//     let fixture = TestBed.createComponent(ListSurveysComponent);
//     const Component = fixture.debugElement.injector.get(SurveyService);
//     const saveSpy = spyOn(Component, 'getAllSurveys').and.callThrough();
  
//     expect(saveSpy.calls.any()).toBe(false, 'SurveyService.getAllSurveys called');

//   });

//   it('should navigate to view a single survey based on ID', () => {
//     const surveyID = 1;
//     let fixture = TestBed.createComponent(ListSurveysComponent);
//     let Component =  fixture.debugElement.componentInstance;
//     const navigateSpy = spyOn(router, 'navigate');

//     Component.loadSurveyView(surveyID);
//     expect(navigateSpy).toHaveBeenCalledWith(['/survey', surveyID]);
// });

});
