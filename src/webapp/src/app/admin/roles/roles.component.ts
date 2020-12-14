import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, FormArray, Validators } from '@angular/forms';
import { Location } from '@angular/common';
import { RolesService } from '../../_services';
import { Role, Permission, DialogOptions } from '../../_models';
import { Utils, roleNameValidator } from '../../_helpers';
import { NgbModal, NgbModalOptions } from '@ng-bootstrap/ng-bootstrap';
import { DialogComponent } from '../../_components';

@Component({
  selector: 'app-roles',
  templateUrl: './roles.component.html',
  styleUrls: ['./roles.component.css']
})
export class RolesComponent implements OnInit {
  currSelectedRole: number = null;
  selectedRoleId: number = null;
  selectedRole: number = null;
  roles: Role[] = null;
  permissions: Permission[] = null;
  addPermissionsForm: FormGroup;
  createNewRoleMode: boolean = true;
  activePermissions: Permission[] = [];
  permissionsLoaded: boolean = false;
  userCanEditRole: boolean = false;
  userCanAddRole: boolean = true;
  permissionsTxt: string = '';
  submitted: boolean = false;
  ADD_NEW_ROLE_BTN_TXT: string = '+ Add New Role';
  RESERVED_ROLE: string = 'Admin';
  errorMsg: string = '';
  lookUpData = JSON.parse(localStorage.getItem('lookupData'));
  primaryDialogOptions: NgbModalOptions = {
    backdrop: 'static'
  };
  roleTitle: string = null;

  constructor(
    private _location: Location,
    private rolesService: RolesService,
    private formBuilder: FormBuilder,
    private utils: Utils,
    private modalService: NgbModal
  ) {
    this.addPermissionsForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        roleNameValidator,
        Validators.minLength(2)
      ]),
      default: new FormControl(),
      permissionCheckBoxes: new FormArray([], [utils.validateMinSelectedCheckboxes(1)])
    });
  }

  ngOnInit() {
    this.getAllRoles();
  }

  get form() {
    return this.addPermissionsForm.controls;
  }

  public back(): void {
    this._location.back();
  }

  private getAllRoles(): void {
    this.rolesService.getRoles().subscribe(
      response => {
        if (this.userCanAddRole)
          response.unshift({
            default: false,
            id: 0,
            name: this.ADD_NEW_ROLE_BTN_TXT,
            permissions: 0,
            control: 'new',
            permission_codes: []
          });

        this.roles = response;
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public setMode(_selection: number, _role: Role): void {
    if (this.submitted) {
      this.errorMsg = '';
      this.submitted = false;
    }
    if (_role.id == 0) {
      this.createNewRoleMode = true;
      this.addPermissionsForm.reset();
      this.userCanEditRole = false;
      this.handlePermissonDisplay(_role);
    } else {
      this.createNewRoleMode = false;
      this.userCanEditRole = false;
      this.addPermissionsForm.patchValue({
        name: _role.name,
        default: _role.default
      });
      if (_role.name === this.RESERVED_ROLE) {
        this.userCanEditRole = true;
      }
      this.handlePermissonDisplay(_role);
    }
    this.currSelectedRole = _selection;
  }

  private handlePermissonDisplay(_role: Role): void {
    this.permissionsLoaded = false;
    this.roleTitle = _role.name;
    this.selectedRole = _role.permissions;
    this.selectedRoleId = _role.id;
    this.generatePermissionsTxt();
    this.resetPermissionOptionCheckboxes();
    this.permissions = this.sortPermissionsAlpha();
    this.addPermissionOptionCheckboxes();
  }

  public generatePermissionsTxt() {
    return this.createNewRoleMode ? 'Add Permissions' : 'Permissions';
  }

  public generateSaveBtnTxt() {
    return this.createNewRoleMode ? 'Save New Role' : 'Save';
  }

  public submit(): void {
    this.createNewRoleMode ? this.createNewRole() : this.updateRole();
  }
  public cancel(): void {
    this.permissionsLoaded = false;
    this.currSelectedRole = null;
  }

  private createNewRole(): void {
    const newRole: Role = {
      name: this.addPermissionsForm.value.name,
      default: this.addPermissionsForm.value.default,
      permissions: this.sumPermissions(this.getSelectedPermissions()),
      permission_codes: [] // TODO FIX THIS
    };

    this.submitted = true;
    if (this.addPermissionsForm.invalid) {
      return;
    } else {
      this.rolesService.createNewRole(newRole).subscribe(
        () => {
          this.utils.generateSuccessToastrMsg('Role Successfully created', '');
          this.addPermissionsForm.reset();
          this.permissionsLoaded = false;
          this.getAllRoles();
        },
        error => {
          this.errorMsg = error.message;
        }
      );
    }
  }

  private updateRole(): void {
    const newRole: Role = {
      name: this.addPermissionsForm.value.name,
      default: this.addPermissionsForm.value.default,
      permissions: this.sumPermissions(this.getSelectedPermissions()),
      permission_codes: [] // TODO FIX THIS
    };

    this.submitted = true;
    if (this.addPermissionsForm.invalid) {
      return;
    } else {
      this.rolesService.updateRole(this.selectedRoleId, newRole).subscribe(
        () => {
          this.utils.generateSuccessToastrMsg('Role Successfully updated', '');
          this.getAllRoles();
        },
        error => {
          this.errorMsg = error.message;
        }
      );
    }
  }

  public deleteRole(): void {
    this.rolesService.deleteRole(this.selectedRoleId).subscribe(
      () => {
        this.utils.generateSuccessToastrMsg('Role Successfully Deleted', '');
        this.permissionsLoaded = false;
        this.getAllRoles();
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public showDeleteIcon(_roleName: string): boolean {
    switch (_roleName) {
      case 'Admin': {
        return false;
      }
      case this.ADD_NEW_ROLE_BTN_TXT: {
        return false;
      }
      default:
        return true;
    }
  }

  public capitalizeInput(_str: string): string {
    return this.utils.generateCapitalizeString(_str);
  }

  private getSelectedPermissions(): number[] {
    const selectedPermissions = [];
    const selectedPermcb = this.form.permissionCheckBoxes as FormArray;
    selectedPermcb.controls.forEach((checkbox, index) => {
      if (checkbox.value) {
        selectedPermissions.push(this.permissions[index].value);
      }
    });
    return selectedPermissions;
  }

  private addPermissionOptionCheckboxes(): void {
    this.permissions.map(permission => {
      const control = !this.createNewRoleMode
        ? new FormControl({
            value: this.hasPermission(permission.value, this.selectedRole),
            disabled: this.userCanEditRole
          })
        : new FormControl();
      (this.addPermissionsForm.controls.permissionCheckBoxes as FormArray).push(control);
    });
    setTimeout(() => {
      this.permissionsLoaded = true;
    }, 1000);
  }

  private resetPermissionOptionCheckboxes() {
    this.permissions = [];
    const control = <FormArray>this.addPermissionsForm.controls['permissionCheckBoxes'];
    for (let i = control.length - 1; i >= 0; i--) {
      control.removeAt(i);
    }
  }

  private sortPermissionsAlpha() {
    return (this.permissions = this.lookUpData.permissions.sort((
      _permA: Permission,
      _permB: Permission
    ) => {
      if (_permA.name < _permB.name) {
        return -1;
      }
      if (_permA.name > _permB.name) {
        return 1;
      }
      return 0;
    }));
  }

  public displayDeleteRolePrompt(_role: Role): void {
    this.selectedRoleId = _role.id;
    this.openDeleteDialogPrompt();
  }

  public onCheckboxChange(e: { target: { checked: boolean } }): void {
    if (e.target.checked) this.openDefaultRoleDialogPrompt();
  }

  private hasPermission(_permissionVal: number, _roleVal: number): boolean {
    return (_permissionVal & _roleVal) == _permissionVal;
  }

  private sumPermissions(_permissions: number[]): number {
    return _permissions.reduce((sum, num) => sum + num, 0);
  }

  /* 
  Incase you need to remove permissions
  private removePermissions(permissions: number[], role: number): number {
    return permissions.reduce((sum, num) => sum - num, role);
  }
  */

  private openDeleteDialogPrompt(): void {
    const dialogOptions: DialogOptions = {
      headerText: 'Delete Role',
      bodyText: 'Are you sure you want to delete this role?',
      primaryActionText: 'Yes, Delete',
      cancelBtnText: 'Cancel',
      btnClass: 'danger',
      saveChanges: false
    };

    const dialog = this.modalService.open(DialogComponent, this.primaryDialogOptions);
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe( (choice: boolean) => {
      if (choice) this.deleteRole();
    });
  }

  private openDefaultRoleDialogPrompt(): void {
    const dialogOptions: DialogOptions = {
      headerText: 'Set Role to Default',
      bodyText: 'Are you sure you want set this Role to default',
      primaryActionText: 'Yes, Set Default',
      cancelBtnText: 'Cancel',
      btnClass: "success",
      saveChanges: false
    };

    const dialog = this.modalService.open(DialogComponent, this.primaryDialogOptions);
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe( (choice: boolean) => {
      setTimeout(() => {
        this.addPermissionsForm.patchValue({
          default: choice ? (this.addPermissionsForm.value.default = true) : false
        });
      }, 5000);
    });
  }
}