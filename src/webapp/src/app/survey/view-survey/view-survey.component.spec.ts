/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientModule } from '@angular/common/http';
import { ViewSurveyComponent } from './view-survey.component';
import { SurveyComponent } from '../survey.component';
import { AnimatedLoaderComponent } from '../../_components';
import { Router } from "@angular/router";
import { Location } from "@angular/common";

describe('ViewSurveyComponent', () => {
  let component: ViewSurveyComponent;
  let fixture: ComponentFixture<ViewSurveyComponent>;
  let location: Location;
  let router: Router;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule.withRoutes([]), HttpClientModule],
      declarations: [ViewSurveyComponent, SurveyComponent, AnimatedLoaderComponent]
    }).compileComponents();

    router = TestBed.get(Router);
    location = TestBed.get(Location);
    router.initialNavigation();
  }));

it('should load animated loader component', () =>{
  const fixture = TestBed.createComponent(AnimatedLoaderComponent);
  const component = fixture.componentInstance;
  expect(component).toBeTruthy();
});

  it('should create view survey component', () => {
    fixture = TestBed.createComponent(ViewSurveyComponent);
    component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });


  it('should load the survey component  ', () => {
    const fixture = TestBed.createComponent(SurveyComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  it('should display a title', () => {
    fixture = TestBed.createComponent(ViewSurveyComponent);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('Survey');
  });

// Needs more work...
/*
  it('should navigate back to all surveys view', () => {
    let fixture = TestBed.createComponent(ViewSurveyComponent);
    let Component =  fixture.debugElement.componentInstance;
    const navigateSpy = spyOn(router, 'navigate');

    Component.sendData();
    fixture.detectChanges();
    expect(navigateSpy).toHaveBeenCalledWith(['surveys']);
});
*/

});
