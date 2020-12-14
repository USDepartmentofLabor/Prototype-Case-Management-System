import { Component, OnInit } from '@angular/core';
import { GeneralService } from '../../_services';
import { Dashboard } from '../../_models';
import { Utils } from '../../_helpers';

@Component({
    selector: 'app-default-dashboard',
    templateUrl: './default-dashboard.component.html',
    styleUrls: ['./default-dashboard.component.css']
})
export class DefaultDashboardComponent implements OnInit {
    dashboards: Dashboard[] = [];

    constructor(private generalService: GeneralService, private utils: Utils) {
    }

    ngOnInit() {
        this.getAllDashboards();
    }

    getAllDashboards(): void {
        this.generalService.getDashboards().subscribe(
            (data) => {
                this.dashboards = data;
            },
            (error) => {
                console.log(`error getting all dashboards: ${error}`);
            }
        );
    }

    setDefaultDashboard(dashboardID: number): void {
        this.generalService.setDefaultDashboard(dashboardID).subscribe(
            (data) => {
                this.dashboards = data;
                this.utils.generateSuccessToastrMsg("Successfully saved the default dashboard.", "");
            },
            (error) => {
                console.log(`error getting all dashboards: ${error}`);
            }
        );
    }

}
