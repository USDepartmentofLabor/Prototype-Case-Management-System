import { Component, OnInit, Output, Input, EventEmitter } from "@angular/core";
import { CaseService } from "../../_services";
import { NgbActiveModal } from "@ng-bootstrap/ng-bootstrap";
import { FileUploader } from "ng2-file-upload";
import { Utils } from "../../_helpers";
import { ActivityService } from 'app/_services/activity.service';

@Component({
  selector: "app-upload-documents-modal",
  templateUrl: "./upload-documents-modal.component.html",
  styleUrls: ["./upload-documents-modal.component.css"],
})
export class UploadDocumentsModalComponent implements OnInit {
  @Input() public modalOptions;
  @Output() passEntry: EventEmitter<any> = new EventEmitter();
  uploader: FileUploader;
  hasBaseDropZoneOver: boolean;
  hasAnotherDropZoneOver: boolean;
  response: string;
  isUploading = false;
  errorMsg: string;
  latitude: number;
  longitude: number;

  constructor(
    public activeModal: NgbActiveModal,
    private caseService: CaseService,
    private activityService: ActivityService,
    private utils: Utils
  ) {}

  ngOnInit() {
    this.uploader = new FileUploader({});
    this.getLocation();
  }

  public generateUploadText() {
    return this.isUploading ? "Uploading..." : "Upload file";
  }

  public upload(_file: any) {
    if (this.errorMsg) {
      this.errorMsg = null;
    }
    this.isUploading = true;

    const fileData = {
      file: _file._file,
      fileName: _file._file.name,
      caseId: this.modalOptions.caseId,
      activityId: this.modalOptions.activityId,
      docId:
        this.modalOptions.uploadType === "document"
          ? this.modalOptions.docId
          : "",
      latitude: this.latitude,
      longitude: this.longitude,
    };

    if (this.modalOptions.isActivityFileUpload) {
        this.activityService.uploadFile(fileData).subscribe(
            (response) => {
              if (response) {
                this.choice(true);
              }
            },
            (error) => {
              this.errorMsg = "Error Uploading file...";
              this.isUploading = false;
              console.log(error.message);
            }
          );
    } else {
      this.caseService.uploadFile(fileData).subscribe(
        (response) => {
          if (response) {
            this.choice(true);
          }
        },
        (error) => {
          this.errorMsg = "Error Uploading file...";
          this.isUploading = false;
          console.log(error.message);
        }
      );
    }
  }

  public cancelUpload() {
    this.errorMsg = null;
  }

  private choice(_choice: boolean): void {
    this.passEntry.emit({ choice: true });
    setTimeout(() => {
      this.isUploading = false;
      this.utils.generateSuccessToastrMsg("Document Successfully uploaded", "");
      this.activeModal.close(_choice);
    }, 1000);
  }

  private getLocation(): void {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.latitude = position.coords.latitude;
          this.longitude = position.coords.longitude;
        },
        (err) => {
          this.latitude = null;
          this.longitude = null;
          console.log(`ERROR(${err.code}): ${err.message}`);
        }
      );
    } else {
      this.latitude = null;
      this.longitude = null;
      console.log("No support for geolocation");
    }
  }
}
