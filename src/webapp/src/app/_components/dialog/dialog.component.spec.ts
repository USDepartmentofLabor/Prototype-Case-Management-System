import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DialogComponent } from './dialog.component';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

describe('DialogComponent', () => {
  let component: DialogComponent;
  let fixture: ComponentFixture<DialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [DialogComponent],
      providers: [NgbActiveModal]
    }).compileComponents();
  }));

  beforeEach(async(() => {
    fixture = TestBed.createComponent(DialogComponent);
    component = fixture.componentInstance;
    component.modalOptions = {
      buttonsTxt: 'Save'
    };
    fixture.detectChanges();
  }));

  it('Displays save button text', () => {
    expect(component.modalOptions.buttonsTxt).toMatch('Save');
  });

  it('should create', async(() => {
    fixture.detectChanges();
    fixture.whenStable().then(() => {
      expect(component).toBeTruthy();
    });
  }));
});
