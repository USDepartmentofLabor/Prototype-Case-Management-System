import { Component, OnInit } from '@angular/core';
import { AddUserModalComponent, ChangePasswordModalComponent } from '../../_components';
import { UserService, AuthenticationService } from '../../_services';
import { NgbModal, NgbModalOptions, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { Location } from '@angular/common';
import { User, Role } from '../../_models';
import { Utils } from '../../_helpers';
import * as _ from 'lodash';

@Component({
  selector: 'users-skeleton',
  templateUrl: './users-skeleton.html',
  styleUrls: ['./users.component.css']
})
export class UsersSkeletonComponent {
  skeletonItems: Array<number>;

  constructor() {
    this.skeletonItems = Array.from(
      {
        length: Math.floor(Math.random() * 10)
      },
      () => Math.floor(Math.random() * 40)
    );
  }
}

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {
  isUserDataLoaded: boolean = false;
  currSelectedUser: number = null;
  isUserListLoaded: boolean = false;
  isSavingUserData: boolean;
  userId: number;
  roles: Role[];
  closeResult: string;
  userForm: FormGroup;
  password: string;
  accActionTxt: string;
  username: string;
  currUserRole: string;
  lookUpData: any = JSON.parse(localStorage.getItem('lookupData'));
  users: User[];
  user: User;
  options: NgbModalOptions = {
    backdrop: 'static'
  };

  constructor(
    private modalService: NgbModal,
    private utils: Utils,
    private userService: UserService,
    private authService: AuthenticationService,
    private formBuilder: FormBuilder,
    private _location: Location
  ) {
    this.userForm = this.formBuilder.group({
      email: new FormControl(null, [Validators.required, Validators.email]),
      username: new FormControl(null, Validators.required),
      name: new FormControl(null, Validators.required),
      role: new FormControl(null, Validators.required),
      location: new FormControl(null),
      is_active: new FormControl(null),
      password: new FormControl({ value: '***********', disabled: true })
    });
  }

  ngOnInit() {
    setTimeout(() => {
      this.getAllUsers();
    }, 2000);
  }

  public back(): void {
    this._location.back();
  }

  public displayUserData(_selection: number, _userId: number): void {
    this.currSelectedUser = _selection;
    this.userId = _userId;

    if (this.isUserDataLoaded) {
      this.isUserDataLoaded = false;
    }
    this.isUserDataLoaded = true;
    this.roles = this.lookUpData.roles;

    this.userService.getUserByID(this.userId).subscribe(data => {
      const { email, username, name, location = 'location', is_active } = data;
      this.accActionTxt = this.generateAccountDeactivationTxt(is_active);
      this.username = username;
      this.currUserRole = data.role.name;
      this.userForm.patchValue({
        email,
        username,
        role: data.role.name,
        name,
        location,
        is_active
      });
    });
  }

  public save(): void {
    const userDataObj = {
      id: this.userId,
      email: this.userForm.value.email,
      name: this.userForm.value.name,
      username: this.userForm.value.username,
      location: this.userForm.value.location || 'location',
      is_active: this.userForm.value.is_active,
      role_id: this.utils.getSelectedRoleObj(this.userForm.value.role, this.roles).id
    };

    this.isSavingUserData = true;
    this.userService.updateUser(this.userId, userDataObj).subscribe(
      () => {
        this.currSelectedUser = null;
        this.isUserDataLoaded = this.isSavingUserData = false;

        this.utils.generateSuccessToastrMsg('Successfully saved user.', '');
        this.isUserListLoaded = false;
        setTimeout(() => {
          this.getAllUsers();
          this.isUserListLoaded = false;
        }, 1500);
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public cancel(): void {
    this.currSelectedUser = null;
    this.isUserDataLoaded = false;
  }

  public changePassword(newPassword: { newPassword: string, confirmPassword: string }): void {
    const pwd = {
      new_password: newPassword.newPassword,
      confirm_password: newPassword.confirmPassword
    };
    this.authService.changePassword(pwd, this.userId).subscribe(
      data => {
        this.utils.generateSuccessToastrMsg(`${data.message} successfully`, '');
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public resendWelcomeEmail(): void {
    this.userService.resendWelcome(this.userId).subscribe(
      () => {
        this.utils.generateSuccessToastrMsg('Successfully sent email!', '');
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public checkValue() {
    this.accActionTxt = this.generateAccountDeactivationTxt(this.userForm.controls.is_active.value);
  }

  private generateAccountDeactivationTxt(_status: boolean): string {
    return _status ? 'Deactivate' : 'Activate';
  }

  private getAllUsers(): void {
    this.userService.getAllUsers().subscribe(data => {
      this.users = data;
      this.users = this.users.sort(
        (_userA, _userB) =>
          Date.parse(_userB['updated_at']) - Date.parse(_userA['updated_at'])
      );
      this.users.map(user => {
        user.firstInitial = this.utils.generateFirstInitalFromUserName(user.username);
        user.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
      });
      this.isUserListLoaded = true;
    });
  }

  private createNewUser({ email, username, role, name, location = 'location' }) {
    const data = {
      email: email,
      username: username,
      role_id: role,
      name: name,
      location: location
    };

    this.userService.createNewUser(data).subscribe(
      () => {
        this.getAllUsers();
        this.utils.generateSuccessToastrMsg('User Successfully Created', '');
      },
      error => {
        this.utils.generateErrorToastrMsg(error.msg);
      }
    );
  }

  public generateUserStatusClass(_status: boolean): string {
    return _status ? 'active' : 'inactive';
  }

  public formatLastUpdateDate(_date: string): string {
    return _date ? this.utils.generateDateFormatFromNow(_date) : '';
  }

  public openModal() {
    const modalRef = this.modalService.open(AddUserModalComponent, this.options);
    modalRef.componentInstance.user = this.user;
    modalRef.result.then(
      result => {
        if (result) {
          // the result from the create user modal
          _.isEmpty(result) ? console.log('No new obj') : this.createNewUser(result);
        }
      },
      reason => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  public openChangePasswordDialog() {
    const modalRef = this.modalService.open(ChangePasswordModalComponent, this.options);
    modalRef.result.then(
      result => {
        if (result) {
          // the result from the create user modal
          _.isEmpty(result) ? console.log('No new obj') : this.changePassword(result);
        }
      },
      reason => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  // this will catch the promise error when modal is closed
  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }
}
