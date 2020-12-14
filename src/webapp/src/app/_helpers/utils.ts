import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import * as moment from 'moment';
import * as _ from 'lodash';
import { ValidatorFn, FormArray } from '@angular/forms';
import {
    Role
} from '../_models';

@Injectable({
    providedIn: 'root'
})
export class Utils {
    backgroundColorClassNames: Array<string> = [
        'light-green',
        'light-blue ',
        'blue-grey',
        'indigo',
        'pink',
        'brown',
        'grey',
        'teal',
        'cyan'
    ];
    randomColorClass: string;

    constructor(private toastr: ToastrService) {
    }

    generateCurrentYear(): number {
        return new Date().getFullYear();
    }

    generateBooleanVal(val: string): string | boolean {
        return !_.isEmpty(val) ? !!val : '';
    }

    generateDateFormatFromNow(date: string): string {
        return moment.utc(date).fromNow();
    }

    generateQueueDateFormat(date: string): string {
        return moment(date, 'YYYY-MM-DD').format('L');
    }

    generateCurrentDate(): string {
        return moment(new Date(), 'YYYY-MM-DD').format('L');
    }

    generateFirstInitalFromUserName(username: string): string {
        return username.charAt(0).toUpperCase();
    }

    generateUppercaseString(str: string): string {
        return str.toUpperCase();
    }

    generateRandomBackgroundColorClass() {
        return (this.randomColorClass = this.backgroundColorClassNames[
            Math.floor(Math.random() * this.backgroundColorClassNames.length)
            ]);
    }

    generateSuccessToastrMsg(msg: string, msgTitle: string = 'Success!'): void {
        this.toastr.success(`${msg}`, `${msgTitle}`, {
            timeOut: 2000,
            tapToDismiss: true
        });
    }

    generateTruncatedText(str: string, size = 32): string {
        return str.length > size ? str.slice(0, size) + '...' : str;
    }

    generateErrorToastrMsg(msg: string, msgTitle = 'error!'): void {
        this.toastr.error(`${msg}`, `${msgTitle}`, {
            timeOut: 2000,
            tapToDismiss: true
        });
    }

    // capitalize each first letter in a string
    generateCapitalizeString(str: string): string {
        return _.startCase(str).trim();
    }

    getSelectedRoleObj(lookup: string, rolesObj: Role[]): Role {
        for (let i = 0; i < rolesObj.length; i++) {
            if (rolesObj[i].name === lookup) {
                return rolesObj[i];
            }
        }
    }

    validateMinSelectedCheckboxes(min = 1): ValidatorFn {
        const validator: ValidatorFn = (formArray: FormArray) => {
            const totalSelected = formArray.controls
                .map(control => control.value)
                .reduce((prev, next) => (next ? prev + next : prev), 0);
            return totalSelected >= min ? null : {required: true};
        };
        return validator;
    }

    returnNonApplicableVal(val: string): string {
        return _.isEmpty(val) ? 'N/A' : val;
    }
}
