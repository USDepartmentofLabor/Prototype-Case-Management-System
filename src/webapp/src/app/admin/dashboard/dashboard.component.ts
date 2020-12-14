import { Component, OnInit } from '@angular/core';
import { Utils } from '../../_helpers';
import * as _ from 'lodash';
import { AddUserModalComponent } from '../../_components/add-user-modal/add-user-modal.component';
import { UserService, AuthenticationService } from '../../_services';
import { ChangePasswordModalComponent } from '../../_components/change-password-modal/change-password-modal-component';
import { NgbModal, NgbModalOptions, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { User } from '../../_models/index';


@Component({
  selector: 'dashboard-skeleton',
  templateUrl: './dashboard-skeleton.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardSkeletonComponent {
  skeletonItems: Array<any>

  constructor() {
    this.skeletonItems = Array.from({ length: Math.floor(Math.random() * 10) }, () => Math.floor(Math.random() * 40));
  }
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  constructor(
  ) {}

  ngOnInit() {
  }

  
}
