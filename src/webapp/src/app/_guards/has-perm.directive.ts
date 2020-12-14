import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { Permission } from '../_models';
import * as _ from 'lodash';

interface Found {
    code: string;
    name: string;
    value: number;
}

@Directive({
    selector: '[hasPerm]'
})
export class HasPermDirective {
    lookupDataPerm: Permission[]; // permissionList
    currUsrPerm: number;
    found: Found;
    componentCode: string | string[];
    lookupData = JSON.parse(localStorage.getItem('lookupData')) || '';
    currentUser = JSON.parse(localStorage.getItem('currentUser'));


    perm: string | string [] = null;

    constructor(
        private templateRef: TemplateRef<HTMLObjectElement>,
        private viewContainer: ViewContainerRef
    ) {
    }

    @Input() set hasPerm(permission: string | string[]) {
        this.componentCode = permission;
        this.updateComponent();
    }

    private hasPermission(permissionVal: number, roleVal: number): boolean {
        return (permissionVal & roleVal) === permissionVal;
    }

    private updateComponent(): void {
        this.lookupDataPerm = this.lookupData.permissions;
        // get the current users permission value
        if (!this.currentUser) {
            return;
        }
        this.currUsrPerm = this.currentUser.role.permissions;

        if (_.isEmpty(this.lookupDataPerm)) {
            return;
        }
        this.found = this.lookupDataPerm.find(element => element.code === this.componentCode);
        if (this.found && this.currUsrPerm) {
            if (this.hasPermission(this.found.value, this.currUsrPerm) || this.isAdmin(this.currUsrPerm)) {
                this.viewContainer.createEmbeddedView(this.templateRef);
            } else {
                this.viewContainer.clear();
            }
        }
    }

    private isAdmin(currUsrPerm: number) {
        const adminPermissionValue = 1;
        return (currUsrPerm & adminPermissionValue) === adminPermissionValue;
    }
}
