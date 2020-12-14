import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadDocumentsModalComponent } from './upload-documents-modal.component';

describe('UploadDocumentsModalComponent', () => {
  let component: UploadDocumentsModalComponent;
  let fixture: ComponentFixture<UploadDocumentsModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UploadDocumentsModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadDocumentsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
