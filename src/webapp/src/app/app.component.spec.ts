import { TestBed, async } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { HeaderComponent } from './_components/header/header.component';
import { HttpClientModule } from '@angular/common/http';
import { NO_ERRORS_SCHEMA } from '@angular/core';


describe('AppComponent', () => {
  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        HttpClientModule
      ],
      declarations: [
        HeaderComponent
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();
  }));


  it('should create the app header', async(() => {
    const fixture = TestBed.createComponent(HeaderComponent);
    const appHeader = fixture.debugElement.componentInstance;
    expect(appHeader).toBeTruthy();
  }));
});

// fixture.detectChanges();
// let SurveyServive = fixture.debugElement.injector.get(SurveyService)
