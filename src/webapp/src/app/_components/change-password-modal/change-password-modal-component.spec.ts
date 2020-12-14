import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ChangePasswordModalComponent } from './change-password-modal-component';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FormBuilder } from '@angular/forms';

describe('ChangePasswordModalComponent', () => {
  let component: ChangePasswordModalComponent;
  let fixture: ComponentFixture<ChangePasswordModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      providers: [NgbActiveModal, FormBuilder],
      declarations: [ ChangePasswordModalComponent ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();
  }));


  it('should create change password modal component', () => {
    fixture = TestBed.createComponent(ChangePasswordModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });
});
