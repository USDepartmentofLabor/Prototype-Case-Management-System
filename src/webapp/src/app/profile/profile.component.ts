import { AuthenticationService, UserService } from '../_services';
import { Component, OnInit } from '@angular/core';
import { NgbModal, NgbModalOptions, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ChangePasswordModalComponent } from '../_components/index';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { Utils } from '../_helpers';
import { User } from '../_models';
import * as _ from 'lodash';

@Component({
  selector: 'profile-skeleton',
  templateUrl: './profile-skeleton.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileSkeletonComponent {}

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  password: string;
  profileObj: object;
  userForm: FormGroup;
  user: User;
  closeResult: string;
  submitted: boolean = false;
  isProfileLoaded: boolean = false;
  editProfileMode: boolean = false;
  savingProfileData: boolean = false;
  currUser: User = this.authService.currentUserValue;
  modalOptions: NgbModalOptions = {
    backdrop: 'static'
  };

  constructor(
    private utils: Utils,
    private modalService: NgbModal,
    private authService: AuthenticationService,
    private userService: UserService,
    private formBuilder: FormBuilder
  ) {
    this.userForm = this.formBuilder.group({
      email: new FormControl(null, [Validators.required, Validators.email]),
      username: new FormControl(null, Validators.required),
      name: new FormControl(null, Validators.required),
      location: new FormControl(null)
    });
  }

  get form() {
    return this.userForm.controls;
  }

  ngOnInit() {
    this.getUserProfileData();
  }

  public getUserProfileData(): void {
    this.userService.getUserByID(this.currUser.id).subscribe(data => {
      this.user = data;
      this.user.firstInitial = this.utils.generateFirstInitalFromUserName(data.username);
      this.user.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
      this.isProfileLoaded = true;
    });
  }

  public setMemberSinceDisplayDate(_date: string): string {
    return this.utils.generateQueueDateFormat(_date);
  }

  public setEditProfileMode(): void {
    this.editProfileMode = this.editProfileMode ? false : true;
    const { email, username, name, location } = this.user;

    if (this.editProfileMode) {
      this.userForm.patchValue({
        email,
        username,
        name,
        location
      });
    }
  }

  public save(): void {
    const userDataObj = {
      id: this.currUser.id,
      email: this.userForm.value.email,
      username: this.userForm.value.username,
      name: this.userForm.value.name,
      location: this.userForm.value.location || 'location'
    };
    this.savingProfileData = true;
    this.submitted = true;
    if (this.userForm.invalid) {
      this.savingProfileData = false;
    } else {
      this.userService.updateUser(this.currUser.id, userDataObj).subscribe(() => {
        this.savingProfileData = this.editProfileMode = false;
        this.getUserProfileData();
        this.utils.generateSuccessToastrMsg('Successsfully updated your profile!', '');
      });
    }
  }

  public changePassword({ newPassword }): void {
    
    const pwd = {
      new_password: newPassword,
      confirm_password: newPassword
    };

    this.authService.changePassword(pwd, this.currUser.id).subscribe(
      data => {
        this.utils.generateSuccessToastrMsg(`${data.message} successfully`, '');
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public openChangePasswordModal(): void {
    const modalRef = this.modalService.open(ChangePasswordModalComponent, this.modalOptions);
    modalRef.result.then(
      result => {
        if (result) {
          _.isEmpty(result) ? console.log('No new obj') : this.changePassword(result);
        }
      },
      reason => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

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