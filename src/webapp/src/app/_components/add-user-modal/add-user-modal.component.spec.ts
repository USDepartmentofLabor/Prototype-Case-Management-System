import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { Angular2FontawesomeModule } from 'angular2-fontawesome';
import { ReactiveFormsModule} from '@angular/forms';
import { AddUserModalComponent } from './add-user-modal.component';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

describe('AddUserModalComponent', () => {
  let component: AddUserModalComponent;
  let fixture: ComponentFixture<AddUserModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, Angular2FontawesomeModule],
      declarations: [ AddUserModalComponent ],
      providers: [NgbActiveModal]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddUserModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create add user modal', () => {
    expect(component).toBeTruthy();
  });
});
