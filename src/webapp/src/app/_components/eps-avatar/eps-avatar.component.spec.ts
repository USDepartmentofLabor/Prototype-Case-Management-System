import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EpsAvatarComponent } from './eps-avatar.component';

describe('EpsAvatarComponent', () => {
  let component: EpsAvatarComponent;
  let fixture: ComponentFixture<EpsAvatarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EpsAvatarComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EpsAvatarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
