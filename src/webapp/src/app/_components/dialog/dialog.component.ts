import { Component, Output, Input, EventEmitter } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { DialogOptions } from '../../_models';


@Component({
  selector: 'app-dialog',
  templateUrl: './dialog.component.html',
  styleUrls: ['./dialog.component.css'],
})
export class DialogComponent {
  @Input() public dialogOptions: DialogOptions;
  @Output() passEntry: EventEmitter<Boolean> = new EventEmitter();

  constructor(public activeModal: NgbActiveModal) {}

  public generateBtnClass(btnClass: string = 'default'): string {
    return {
      'default': 'btn-primary',
      'success': 'btn-success',
      'danger': 'btn-danger'
    }[btnClass];
  }

  public choice(action: boolean): void {
    this.passEntry.emit((this.dialogOptions.saveChanges = action));
    this.activeModal.close();
  }
}
