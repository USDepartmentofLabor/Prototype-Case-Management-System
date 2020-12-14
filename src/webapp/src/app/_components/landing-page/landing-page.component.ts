import { Component, OnInit } from '@angular/core';
import { GeneralService } from '../../_services';

@Component({
    selector: 'app-landing-page',
    templateUrl: './landing-page.component.html',
    styleUrls: ['./landing-page.component.css']
})
export class LandingPageComponent implements OnInit {

    isLoading = false;

    constructor(private generalService: GeneralService) {
    }

    ngOnInit() {
        this.getAppLookupData();
    }

    private getAppLookupData(): void {
        this.isLoading = true;
        this.generalService.getLookupsData().subscribe(data => {
                localStorage.setItem('lookupData', JSON.stringify(data));
                this.isLoading = false;
            },
            (error) => {
                console.log(error.message);
            });
    }

}
