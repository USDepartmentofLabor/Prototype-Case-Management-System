import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { DialogComponent } from '../../_components/index';
import { SurveyService } from '../../_services';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Utils } from 'app/_helpers';
import { Survey, DialogOptions } from '../../_models';
import * as _ from 'lodash';

@Component({
  selector: 'list-surveys-skeleton',
  templateUrl: './list-surveys-skeleton.html',
  styleUrls: ['./list-surveys.component.css']
})
export class ListSurveySkeletonComponent {}

@Component({
  selector: 'app-list-surveys',
  templateUrl: './list-surveys.component.html',
  styleUrls: ['./list-surveys.component.css'],
  providers: [SurveyService]
})
export class ListSurveysComponent implements OnInit {
  ALL_SURVEYS: string = 'all';
  ARCHIVED_SURVEYS: string = 'archived';
  ALL_SURVEY_TITLE: string = 'Data Collection Forms';
  ARCHIVED_SURVEY_TITLE: string = 'Archived Data Collection Forms';
  surveys: Survey[];
  sortedSurveys: Survey[];
  isSurveysLoaded: boolean = false;
  viewArchivedSurveysMode: boolean = false;
  saveChanges: boolean = false;
  currSurvey: Survey;
  title: string;

  constructor(
    private router: Router,
    private modalService: NgbModal,
    private surveyService: SurveyService,
    private utils: Utils
  ) {}

  ngOnInit() {
    this.getAllSurveysData();
  }

  public loadSurveyData(_type: string) {
    this.isSurveysLoaded = false;
    _type === this.ALL_SURVEYS ? this.getAllSurveysData() : this.getArchivedSurveysData();
  }

  public loadView(_surveyId: number, _route: string): void {
    switch (_route) {
      case 'Run': {
        this.router.navigate([`/form`, _surveyId]);
        break;
      }
      case 'Edit': {
        this.router.navigate([`/form/edit`, _surveyId]);
        break;
      }
      case 'Results': {
        this.router.navigate([`/form-response`, _surveyId]);
        break;
      }
      default: {
        break;
      }
    }
  }

  public formatDateFromNow(_date: string): string {
    return _date ? this.utils.generateDateFormatFromNow(_date) : '';
  }

  public handleArchive(_survey: Survey): void {
    const msgObj = {
      archiveMsg: 'Successfully archived a survey.',
      unArchiveMsg: 'Successfully Unarchived a survey'
    };

    const surveyData = {
      id: _survey.id,
      name: _survey.name,
      structure: _survey.structure,
      is_archived: this.viewArchivedSurveysMode ? false : true
    };

    let toastmsg = this.viewArchivedSurveysMode ? msgObj.unArchiveMsg : msgObj.archiveMsg;

    this.surveyService.updateSurvey(surveyData).subscribe(
      () => {
        this.utils.generateSuccessToastrMsg(toastmsg, '');
        this.viewArchivedSurveysMode
          ? this.loadSurveyData(this.ARCHIVED_SURVEYS)
          : this.loadSurveyData(this.ALL_SURVEYS);
      },
      error => {
        console.log(error.message);
      }
    );
  }

  public showDeleteDialog(_survey: Survey): void {
    this.currSurvey = _survey;
    this.openDialog();
  }

  public isSurveysDataEmpty() {
    return this.sortedSurveys.length > 0;
  }

  private getAllSurveysData(): void {
    this.sortedSurveys = [];
    this.surveyService.getAllSurveys().subscribe(
      (data) => {
        let surveys: Survey[] = data;
        this.sortedSurveys = surveys.sort((_surveyA, _surveyB) => {
          if(_surveyA.name < _surveyB.name) {
            return -1;
          } else if (_surveyA.name > _surveyB.name) {
            return 1;
          } else {
            return 0;
          }
        });
        this.title = this.ALL_SURVEY_TITLE;
        this.isSurveysLoaded = true;
        this.viewArchivedSurveysMode = false;
      },
      error => {
        console.log(error.message);
      }
    );
  }

  private getArchivedSurveysData(): void {
    this.sortedSurveys = [];
    this.surveyService.getAllSurveys(this.ALL_SURVEYS).subscribe(
      (data) => {
        let surveys: Survey[] = data;
        this.sortedSurveys = surveys.sort((_surveyA, _surveyB) => _surveyA.id - _surveyB.id);
        this.title = this.ARCHIVED_SURVEY_TITLE;
        this.isSurveysLoaded = true;
        this.viewArchivedSurveysMode = true;
      },
      error => {
        console.log(error.message);
      }
    );
  }

  private deleteSurvey(_surveyId: number): void {
    const msgObj = {
      errMsg: 'Invalid id selection!',
      succMsg: 'Survey successfully deleted!'
    };

    this.surveyService.deleteSurvey(_surveyId).subscribe(
      () => {
        this.utils.generateSuccessToastrMsg(msgObj.succMsg, '');
        this.viewArchivedSurveysMode
          ? this.loadSurveyData(this.ARCHIVED_SURVEYS)
          : this.loadSurveyData(this.ALL_SURVEYS);
      },
      error => {
        console.log(error.message);
        this.utils.generateErrorToastrMsg(msgObj.errMsg, error.message);
      }
    );
  }

  private generateDeleteDialogHeaderTxt(): string {
    return this.viewArchivedSurveysMode ? 'Delete Archived Survey' : 'Delete Survey';
  }

  private geneateDeleteDialogTxt(): string {
    return this.viewArchivedSurveysMode
      ? 'Are you sure you want to delete this archived survey?'
      : 'Are you sure you want to delete this survey?';
  }

  private openDialog(): void {
    const dialogOptions: DialogOptions = {
      headerText: this.generateDeleteDialogHeaderTxt(),
      bodyText: this.geneateDeleteDialogTxt(),
      primaryActionText: 'Yes, Delete',
      cancelBtnText: 'Cancel',
      btnClass: 'danger',
      saveChanges: false
    };

    const dialog = this.modalService.open(DialogComponent);
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe( (choice: boolean) => {
      if (choice === true) this.deleteSurvey(this.currSurvey.id);
    });
  }
}
