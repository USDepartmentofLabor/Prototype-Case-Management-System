/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { AnimatedLoaderComponent } from './animated-loader.component';

describe('AnimatedLoaderComponent', () => {
  let component: AnimatedLoaderComponent;
  let fixture: ComponentFixture<AnimatedLoaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AnimatedLoaderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnimatedLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create component', () => {
    expect(component).toBeTruthy();
  });

  // it('should show TEST INPUT', () => {
  //   fixture.detectChanges();
  //   component = fixture.componentInstance;
  //   expect(fixture.nativeElement.querySelector('div').innerText).toEqual('TEST INPUT');
  // });
});
