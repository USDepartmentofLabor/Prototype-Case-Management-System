import { Component, OnInit, Input } from '@angular/core';
import { CaseStatus } from 'app/_models';
import { CaseService } from 'app/_services';
import * as _ from 'lodash';

@Component({
  selector: 'app-status-badge',
  template: `<span *ngIf="!isStatusDataEmpty"
  class="badge"
  [ngClass]="{
    'todo': status.name === 'TODO' || status.name === 'Initiated', 
    'in-progress': status.name === 'In Progress' || status.name === 'Scheduled',
    'done': status.name === 'Done' || status.name === 'Compliant',
    'delayed': status.name === 'Delayed',
    'default': status.name === 'Non-Compliant'
  }">
  <i class="fa fa-circle" aria-hidden="true"></i> <span class="status-text">{{ status.name.toUpperCase() }}</span>
  </span>
  `,
  styles: [
    `
    .badge { 
      font-size: 12;
      font-weight: 700;
    }
    .status-text{
      margin-left:5px;
    }
    .todo{
    color: #004085;
    background-color: #cce5ff;
    border:1px solid #b8daff;
    }
    .in-progress{
    color: #856404;
    background-color: #fff3cd;
    border:1px solid #ffeeba;
    }
    .done {
    color: #155724;
    background-color: #d4edda;
    border:1px solid #c3e6cb;
    }
    .delayed {
      color: #b22222;
      background-color: #ffd6eb;
      border:1px solid #ffbdde;
    }
    .default {
      color: #000000;
      background-color: #dcdcdc;
      border:1px solid #d3d3d3;
    }
    `
  ]
})
export class StatusBadgeComponent implements OnInit {
 @Input() status: CaseStatus;
  isStatusDataEmpty: boolean = false;
  //status: string;
  constructor() { }

  ngOnInit() {
    this.renderStatusBadge();
  }

  renderStatusBadge() {
    _.isEmpty(this.status) ? this.isStatusDataEmpty = true : this.isStatusDataEmpty = false;// this.status = this.statusData;
  }
}

