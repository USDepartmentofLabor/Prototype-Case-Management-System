import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { RolesService } from '../../_services';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { Role, User } from '../../_models';

@Component({
  selector: 'app-add-user-modal',
  templateUrl: './add-user-modal.component.html',
  styleUrls: ['./add-user-modal.component.css'],
})
export class AddUserModalComponent implements OnInit {
  @Input() public user: User;
  @Output() passEntry: EventEmitter<EventListener> = new EventEmitter();
  newUserForm: FormGroup;
  roles: Role[];
  saveBtnTxt: string = '';
  isSavingUserData: boolean;
  submitted: boolean = false;

  constructor(
    public activeModal: NgbActiveModal,
    private formBuilder: FormBuilder,
    private roleService: RolesService
  ) {
    this.newUserForm = this.formBuilder.group({
      email: new FormControl(null, [Validators.required, Validators.email]),
      username: new FormControl(null, Validators.required),
      name: new FormControl(null, Validators.required),
      role: new FormControl(null, Validators.required),
    });
  }

  // convenience getter for easy access to form fields
  get form() {
    return this.newUserForm.controls;
  }

  ngOnInit() {
    this.getRoles();
  }

  private getRoles() {
    this.roleService.getRoles().subscribe(
      (data) => {
        this.roles = data;
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public generateAddUserBtnTxt(): string {
    return this.isSavingUserData ? 'Saving User...' : 'Save';
  }

  public submit(): void {
    this.isSavingUserData = true;
    this.submitted = true;
    if (this.newUserForm.invalid) {
      this.isSavingUserData = false;
    } else {
      this.passEntry.emit(this.newUserForm.value);
      setTimeout(() => {
        this.activeModal.close(this.newUserForm.value);
      }, 1000);
    }
  }
}