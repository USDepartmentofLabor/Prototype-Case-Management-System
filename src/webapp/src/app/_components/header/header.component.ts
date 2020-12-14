import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import {
  AuthenticationService,
  GeneralService,
  AdminService,
  CaseService,
} from "../../_services";
import { NgbModal, NgbModalOptions } from "@ng-bootstrap/ng-bootstrap";
import { DialogComponent } from "..";
import { Utils } from "../../_helpers";
import { Observable } from "rxjs";
import { DialogOptions } from "../../_models";

@Component({
  selector: "app-header",
  templateUrl: "./header.component.html",
  styleUrls: ["./header.component.css"],
})
export class HeaderComponent implements OnInit {
  appTitle = "CMS";
  currUser = this.authService.currentUserValue;
  returnUrl: string;
  analyticsExternalURL: string;
  isLoggedIn$: Observable<boolean>;
  avatarFirstInitial = this.utils.generateFirstInitalFromUserName(
    this.currUser.username
  );
  userDataLoaded = false;
  primaryDialogOptions: NgbModalOptions = {
    backdrop: "static",
  };
  caseDefinitions: { id: number; name: string }[] = [];

  constructor(
    private router: Router,
    private utils: Utils,
    private authService: AuthenticationService,
    private generalService: GeneralService,
    private adminService: AdminService,
    private modalService: NgbModal,
    private caseService: CaseService
  ) {
    this.isLoggedIn$ = this.authService.isLoggedIn;
  }

  ngOnInit() {
    this.getConfigs();
    this.getCaseDefinitions();
  }

  public generateDisplayEmail(): string {
    return this.currUser.email !== "" ? `${this.currUser.email}` : "My Account";
  }

  private getConfigs(): void {
    this.generalService.getConfigs().subscribe(
      (data) => {
        this.analyticsExternalURL = data.metabase_url;
        this.userDataLoaded = true;
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  private getCaseDefinitions(): void {
    this.caseService.getAllCaseDefinitions().subscribe(
      (data) => {
        this.caseDefinitions = data.map((cd) => {
          return { id: cd.id, name: cd.name };
        });
        this.caseDefinitions.sort((cd1, cd2) => {
          if (cd1.name < cd2.name) {
            return -1;
          } else if (cd1.name > cd2.name) {
            return 1;
          } else {
            return 0;
          }
        });
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public generateLinkToMetabase(): string {
    return this.analyticsExternalURL;
  }

  public logOut(): void {
    this.authService.logout();
    this.returnUrl = `login`;
    this.router.navigate([this.returnUrl]);
  }

  public resetReporting(): void {
    this.adminService.resetReporting().subscribe(
      () => {
        this.utils.generateSuccessToastrMsg(
          "Successfully rebuilt the reporting database",
          ""
        );
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public openReportDialogPrompt(): void {
    const dialogOptions: DialogOptions = {
      headerText: "Rebuild Reporting Database",
      bodyText:
        "Are you sure you want to to rebuild the reporting database and re-synch Metabase?",
      primaryActionText: "Yes, Rebuild",
      cancelBtnText: "Cancel",
      btnClass: "success",
      saveChanges: false,
    };

    const dialog = this.modalService.open(
      DialogComponent,
      this.primaryDialogOptions
    );
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((action: boolean) => {
      if (action) {
        this.resetReporting();
      }
    });
  }
}
