import { Component, OnInit } from "@angular/core";
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { GeneralService } from "../../_services";
import { DefaultDashboard } from "../../_models";

@Component({
  selector: "app-metabase-dashboard",
  templateUrl: "./metabase-dashboard.component.html",
  styleUrls: ["./metabase-dashboard.component.css"],
})
export class MetabaseDashboardComponent implements OnInit {
  defaultDashboard: DefaultDashboard;
  dashboardURL: SafeResourceUrl;
  wasDashboardRetrieved = false;
  isDashboardSet = false;

  constructor(
    private generalService: GeneralService,
    private domSanitizer: DomSanitizer
  ) {}

  ngOnInit() {
    this.getDefaultDashboard();
  }

  private getDefaultDashboard(): void {
    this.generalService.getDefaultDashboard().subscribe((defaultDashboard) => {
      if (defaultDashboard.defaultDashboardID) {
        this.defaultDashboard = defaultDashboard;
        this.dashboardURL = this.domSanitizer.bypassSecurityTrustResourceUrl(
          this.defaultDashboard.defaultDashboardURL
        );
        this.isDashboardSet = true;
      } else {
        this.isDashboardSet = false;
      }
      this.wasDashboardRetrieved = true;
    });
  }
}
