import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as SurveyKo from 'survey-knockout';
import * as SurveyCreator from 'survey-creator';
import * as widgets from 'surveyjs-widgets';
// import 'inputmask/dist/inputmask/phone-codes/phone.js';
import { SurveyService } from '../../_services';
import { ToastrService } from 'ngx-toastr';
import { Observable, Subject } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DialogComponent } from '../../_components/index';
import { Utils } from '../../_helpers';
import { Location } from '@angular/common';
import { DialogOptions } from '../../_models';
import * as _ from 'lodash';

widgets.icheck(SurveyKo);
widgets.select2(SurveyKo);
widgets.inputmask(SurveyKo);
widgets.jquerybarrating(SurveyKo);
widgets.jqueryuidatepicker(SurveyKo);
widgets.nouislider(SurveyKo);
widgets.select2tagbox(SurveyKo);
widgets.sortablejs(SurveyKo);
widgets.ckeditor(SurveyKo);
widgets.autocomplete(SurveyKo);
widgets.bootstrapslider(SurveyKo);

var CkEditor_ModalEditor = {
  afterRender: function(modalEditor, htmlElement) {
    var editor = window['CKEDITOR'].replace(htmlElement);
    editor.on('change', function() {
      modalEditor.editingValue = editor.getData();
    });
    editor.setData(modalEditor.editingValue);
  },
  destroy: function(modalEditor, htmlElement) {
    var instance = window['CKEDITOR'].instances[htmlElement.id];
    if (instance) {
      instance.removeAllListeners();
      window['CKEDITOR'].remove(instance);
    }
  }
};
SurveyCreator.SurveyPropertyModalEditor.registerCustomWidget(
  'html',
  CkEditor_ModalEditor
);

@Component({
  selector: 'survey-creator',
  templateUrl: './survey-creator.component.html',
  styleUrls: ['./survey-creator.component.css'],
  providers: [SurveyService]
})
export class SurveyCreatorComponent implements OnInit {
  surveyCreator: SurveyCreator.SurveyCreator;
  surveyId: string;
  surveyData: object[];
  surveyName: string = null;
  surveyNameUpdated: boolean = false;
  surveyHasError: boolean = false;
  surveyLoaded: boolean = true;
  saveChanges: boolean = false;
  errorMsg: string;
  isEditMode: boolean;
  currentViewTitle: string;
  navigateAway: Subject<boolean> = new Subject<boolean>();
  @Input() json: any;
  @Input() response: any;
  @Output() surveySaved: EventEmitter<Object> = new EventEmitter();

  constructor(
    private surveyService: SurveyService,
    private route: ActivatedRoute,
    private modalService: NgbModal,
    private _location: Location,
    private utils: Utils
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.surveyId = params.id;
      this.surveyId
        ? this.getEditModeSurveyData()
        : this.loadNewSurveyCreator();
    });
    window.scrollTo(0, 0);

  }

  public back(): void{
    this._location.back();
  }

  public setCurrViewBreadCrumb():void{
    this.surveyId 
      ? this.currentViewTitle = this.surveyName
      : this.currentViewTitle = 'Create New Form'
  }

  public getEditModeSurveyData(): void {
    this.isEditMode = true;
    this.surveyService.getSurvey(parseInt(this.surveyId)).subscribe(data => {
      this.json = data.structure;
      this.surveyName = data.name;
      this.setCurrViewBreadCrumb();
      this.loadNewSurveyCreator();
    });
  }

  public loadNewSurveyCreator(): void {
    this.setCurrViewBreadCrumb()
    SurveyKo.JsonObject.metaData.addProperty(
      'questionbase',
      'popupdescription:text'
    );
    SurveyKo.JsonObject.metaData.addProperty('page', 'popupdescription:text');

    let options = {
      showEmbededSurveyTab: false,
      generateValidJSON: true,
      showTestSurveyTab: false,
      showJSONEditorTab: false,
      showPropertyGrid: 'right',
      showToolbox: 'right',
      rightContainerActiveItem: "toolbox"
    };

    SurveyCreator.StylesManager.applyTheme('stone');
    this.surveyCreator = new SurveyCreator.SurveyCreator(
      'surveyCreatorContainer',
      options
    );


    this.surveyCreator.showToolbox = "right";
    this.surveyCreator.showPropertyGrid = "right";
    this.surveyCreator.rightContainerActiveItem("toolbox");
    this.surveyCreator.text = JSON.stringify(this.json);
    this.surveyCreator.saveSurveyFunc = this.saveSurvey;

    this.surveyCreator.onModified.add(sender => {
      let changedSurveyStructure = sender;
      localStorage.setItem('surveyStructureDataChanged', 'true');
    });
  }

  public saveSurvey = (): void => {
    const surveyName = this.surveyName;
    if(_.isEmpty(surveyName)){
      this.errorMsg = 'Survey name cannot be blank!';
      this.surveyHasError = true;
      return;
    }

    this.surveySaved.emit(JSON.parse(this.surveyCreator.text));
    this.surveyData = JSON.parse(this.surveyCreator.text);

    const survey = {
      id: parseInt(this.surveyId) || '',
      name: surveyName.trim(),
      structure: this.surveyData
    };

    if (this.isEditMode) {
      this.surveyService.updateSurvey(survey).subscribe(
        (response) => {
          localStorage.removeItem('surveyStructureDataChanged');
          this.utils.generateSuccessToastrMsg('Survey was updated!');
          this.surveyName = response.name;
          this.setCurrViewBreadCrumb();
          this.navigateAway.next(true);
        },
        error => {
          this.utils.generateErrorToastrMsg(error.message);
        }
      );
    } else {
      this.surveyService.saveSurvey(survey).subscribe(
        () => {
          if (this.surveyHasError) this.surveyHasError = false;
          this.loadNewSurveyCreator();
          this.utils.generateSuccessToastrMsg('Survey was created!');
          this.surveyName = '';
        },
        error => {
          this.errorMsg = error.message;
          this.surveyHasError = true;
        }
      );
    }
  };

  canDeactivate(): boolean | Observable<boolean> | Promise<boolean> {
    if (
      this.surveyNameUpdated ||
      localStorage.hasOwnProperty('surveyStructureDataChanged')
    ) {
      this.openSaveDialog();
      return this.navigateAway;
    } else {
      return true;
    }
  }

  private openSaveDialog(): void {
     const dialogOptions: DialogOptions  = {
      headerText: 'Confirm Navigation',
      bodyText: `You have unsaved changes that will be lost if you decide to continue. 
      Are you sure you want to leave this page?`,
      primaryActionText: 'Save',
      cancelBtnText: 'Yes, Exit',
      btnClass: 'success',
      saveChanges: false
    }

    const dialog = this.modalService.open(DialogComponent);
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((choice: boolean) => {
      if (choice === true) {
        this.saveSurvey();
      } else {
        this.navigateAway.next(true);
      }
      this.isEditMode = false;
      localStorage.removeItem('surveyStructureDataChanged');
    });
  }

  public isSurveyNameUpdated(event): void {
    this.surveyNameUpdated = event === this.surveyName ? true : false;
  }
}