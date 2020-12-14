import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardComponent, DashboardSkeletonComponent } from './dashboard.component';
import { Angular2FontawesomeModule } from 'angular2-fontawesome';
import { FormsModule } from '@angular/forms';
import { HeaderComponent } from '../../_components';
import { Utils } from '../../_helpers';
import { ToastrService } from 'ngx-toastr';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      providers: [Utils],
      imports: [Angular2FontawesomeModule, FormsModule, Utils],
      declarations: [ DashboardComponent,DashboardSkeletonComponent, HeaderComponent ]
    })
    .compileComponents();
  }));


  // beforeEach(() => {
  //   fixture = TestBed.createComponent(DashboardComponent);
  //   component = fixture.componentInstance;
  //   fixture.detectChanges();
  // });

  // it('should create Dashboard component', () => {
  //   expect(component).toBeTruthy();
  // });
});
