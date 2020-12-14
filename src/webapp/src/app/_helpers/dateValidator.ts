import { FormGroup } from '@angular/forms';

// custom validator to check that two fields match
export function dateValidator(start_date: string, end_date: string) {
    return (formGroup: FormGroup) => {
        const control = formGroup.controls[start_date];
        const matchingControl = formGroup.controls[end_date];

        if (matchingControl.errors && !matchingControl.errors.dateValidator) {
            // return if another validator has already found an error on the matchingControl
            return;
        }

        // if end date is lower than the start date
        let end_Date = Date.parse(matchingControl.value);
        let start_Date = Date.parse(control.value)
        if ( start_Date > end_Date) { 
            control.setErrors({ dateValidator: true });
        } else {
            control.setErrors(null);
        }
    }
}