import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddDocumentsModalComponent } from './add-documents-modal.component';

describe('AddDocumentsModalComponent', () => {
  let component: AddDocumentsModalComponent;
  let fixture: ComponentFixture<AddDocumentsModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddDocumentsModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddDocumentsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
