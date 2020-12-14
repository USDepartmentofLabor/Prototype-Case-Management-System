import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RankListCustomFieldComponent } from './rank-list-custom-field.component';

describe('RankListButtonCustomFieldComponent', () => {
  let component: RankListCustomFieldComponent;
  let fixture: ComponentFixture<RankListCustomFieldComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RankListCustomFieldComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RankListCustomFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
