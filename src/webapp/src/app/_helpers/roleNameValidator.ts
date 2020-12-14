import { AbstractControl } from '@angular/forms';

export function roleNameValidator(control: AbstractControl): { [key: string]: boolean } | null {
  if (control.value === 'Admin') {
    return { roleNameValidator: true };
  }
  return null;
}
