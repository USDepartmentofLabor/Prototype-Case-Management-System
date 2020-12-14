import { Component, OnInit } from '@angular/core';
import { CaseService } from '../../_services';
import { Router } from '@angular/router';
import { CaseDefinition } from '../../_models';
import { Utils } from '../../_helpers';
import * as _ from 'lodash';

@Component({
  selector: 'app-case-definitions',
  templateUrl: './case-definitions.component.html',
  styleUrls: ['./case-definitions.component.css']
})
export class CaseDefinitionsComponent implements OnInit {
  caseDefinitions: CaseDefinition[];
  isLoading: boolean = false;
  constructor(
    private router: Router, 
    private caseService: CaseService, 
    private utils: Utils
  ){}

  ngOnInit() {
    this.getAllCaseDefinitions();
  }

  private getAllCaseDefinitions(): void {
    this.isLoading = true;
    this.caseService.getAllCaseDefinitions().subscribe(
      (data) => {
        this.caseDefinitions =  this.sortCasesByDateCreated(data);
        this.isLoading = false;
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public isCaseDefinitonsDataEmpty(): boolean {
    return _.isEmpty(this.caseDefinitions);
  }

  public loadEditCaseDefiniton(_id: number): void {
    this.router.navigate([`/cases-definition/edit`, _id]);
  }

  public formatDateFromNow(_date: string): string {
    return _date ? this.utils.generateDateFormatFromNow(_date) : '';
  }

  public generateCaseDesc(_caseDesc: string): string {
    return this.utils.generateTruncatedText(this.utils.returnNonApplicableVal(_caseDesc), 25);
  }

  private sortCasesByDateCreated(_cases: CaseDefinition[]): CaseDefinition[] {
    return (_cases = _cases.sort(
      (_caseDefA, _caseDefB) => Date.parse(_caseDefB['created_at']) - Date.parse(_caseDefA['created_at'])
    ));
  }
}
