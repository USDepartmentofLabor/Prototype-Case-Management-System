import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import * as _ from "lodash";
import { ActivityAPI } from "app/_models";
import { UploadDocumentsModalComponent } from "app/_components";
import {
  ModalDismissReasons,
  NgbModal,
  NgbModalOptions,
} from "@ng-bootstrap/ng-bootstrap";
import { ActivityService } from "app/_services/activity.service";
import { Utils } from 'app/_helpers';

@Component({
  selector: "app-left-pane",
  templateUrl: "./left-pane.component.html",
  styleUrls: ["./left-pane.component.css"],
})
export class LeftPaneComponent implements OnInit {
  @Input() activity: ActivityAPI;
  @Output() activityNameChanged = new EventEmitter<string>();
  @Output() activityDescriptionChanged = new EventEmitter<string>();
  @Output() activityNoteAdded = new EventEmitter<string>();
  @Output() documentUploaded = new EventEmitter();
  @Output() documentDeleted = new EventEmitter();
  primaryModalOptions: NgbModalOptions = {
    backdrop: "static",
  };
  closeResult: string;

  constructor(
    private modalService: NgbModal,
    private activityService: ActivityService,
    private utils: Utils
  ) {}

  ngOnInit() {}

  onActivityNameChanged(newName: string): void {
    console.log(`[LeftPaneComponent] received new name = ${newName}`);
    console.log("[LeftPaneComponent] emitting activityNameChanged");
    this.activityNameChanged.emit(newName);
  }

  onActivityDescriptionChanged(newDescription: string): void {
    console.log(
      `[LeftPaneComponent] receieved new description = ${newDescription}`
    );
    console.log(`[LeftPaneComponent] emitting activityDescriptionChanged`);
    this.activityDescriptionChanged.emit(newDescription);
  }

  onActivityNoteAdded(note: string): void {
    console.log(`[LeftPaneComponent] receieved new note = ${note}`);
    console.log(`[LeftPaneComponent] emitting activityNoteAdded`);
    this.activityNoteAdded.emit(note);
  }

  public generateDocumentRequiredTxt(option: boolean): string {
    return option === true ? " -(Required)" : "";
  }

  public hasDocuments(): boolean {
    return this.activity.documents.length > 0;
  }

  public openFileUploadModal(docId: number, type: string): void {
    const modalOptions = {
      dialogHeaderTxt: "Upload a file",
      activityId: this.activity.id,
      isActivityFileUpload: true,
      docId: type === "document" ? docId : "",
      uploadType: type,
    };

    const modalRef = this.modalService.open(
      UploadDocumentsModalComponent,
      this.primaryModalOptions
    );
    modalRef.componentInstance.modalOptions = modalOptions;
    modalRef.result.then(
      (result) => {
        result ? this.documentUploaded.emit() : console.log("No new obj");
      },
      (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  public downloadDocument(_docId: number) {
    this.activityService.downloadFile(_docId).subscribe(
      (responseData) => {
        if (responseData) {
          const _a = document.createElement("a");
          _a.href = responseData["url"];
          _a.setAttribute("target", "_blank");
          _a.click();
          _a.remove();
        }
      },
      (error) => {
        console.log("error accessing file url", error);
      }
    );
  }

  public deleteDocument(_docId: number) {
    this.activityService.deleteFile(_docId).subscribe(
        (responseData) => {
            if (responseData) {
                this.documentDeleted.emit();
                this.utils.generateSuccessToastrMsg(
                    'Document Successfully Deleted',
                    ''
                );
            }
        },
        (error) => {
            console.log(error.message);
        }
    );
}

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return "by pressing ESC";
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return "by clicking on a backdrop";
    } else {
      return `with: ${reason}`;
    }
  }
}
