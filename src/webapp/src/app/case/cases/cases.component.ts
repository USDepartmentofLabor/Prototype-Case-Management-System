import { Component, OnInit, OnDestroy } from "@angular/core";
import { Subject } from "rxjs";
import { Utils } from "../../_helpers";
import { CaseService } from "../../_services";
import { ActivatedRoute, Router } from "@angular/router";
import { AssignedToAPI, Case, CaseStatus } from "../../_models";

@Component({
  selector: "app-cases",
  templateUrl: "./cases.component.html",
  styleUrls: ["./cases.component.css"],
})
export class CasesComponent implements OnDestroy, OnInit {
  cases: Case[];
  caseList: {
    id: number;
    status?: CaseStatus;
    key: string;
    name: string;
    businessName: string;
    caseType: string;
    assignee?: AssignedToAPI;
    updatedAt: string;
  }[];
  isLoading = false;
  caseDefnIdFilter: number = null;
  breadcrumbLabel = "All Cases";
  dtOptions: DataTables.Settings = {};
  dtTrigger: Subject<any> = new Subject<any>();

  constructor(
    private caseService: CaseService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.dtOptions = {
      pagingType: "full_numbers",
      columnDefs: [
        {
          targets: [0],
          visible: false,
          searchable: false,
        },
      ],
      rowCallback: (row: Node, data: any[] | Object, index: number) => {
        const self = this;
        // Unbind first in order to avoid any duplicate handler
        // (see https://github.com/l-lin/angular-datatables/issues/87)
        $("td", row).off("click");
        $("td", row).on("click", () => {
          self.loadCase(data[0]);
        });
        return row;
      },
    };

    this.route.queryParams.subscribe((params) => {
      this.caseDefnIdFilter = params.case_defn_id as number;
      this.setBreadcrumb();
      this.getAllCases();
    });
  }

  ngOnDestroy(): void {
    // Do not forget to unsubscribe the event
    this.dtTrigger.unsubscribe();
  }

  private getAllCases(): void {
    this.isLoading = true;
    this.caseService.getAllCases().subscribe(
      (data) => {
        this.cases = this.sortCasesByDateCreated(data).filter((c) => {
          if (this.caseDefnIdFilter) {
            if (+c.case_definition.id === +this.caseDefnIdFilter) {
              return true;
            } else {
              return false;
            }
          }
          return true;
        });
        this.caseList = [];
        this.cases.forEach((c) => {
          let businessName = '';
          const businessNameCF = c.custom_fields.find(cf => cf.name === 'Business Name');
          if (businessNameCF) {
            businessName = businessNameCF.value;
          }

          this.caseList.push({
            id: c.id,
            status: c.status,
            key: c.key,
            name: c.name,
            businessName: businessName,
            caseType: c.case_definition.name,
            assignee: c.assigned_to,
            updatedAt: c.updated_at,
          });
        });
        this.isLoading = false;
        this.dtTrigger.next();
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public loadCase(caseId: number): void {
    this.router.navigate([`/cases`, caseId]);
  }

  public formatDateFromNow(_date: string): string {
    return _date ? this.utils.generateDateFormatFromNow(_date) : "";
  }

  private setBreadcrumb(): void {
    if (this.caseDefnIdFilter) {
      this.caseService.getCaseDefinition(this.caseDefnIdFilter).subscribe(
        (cd) => {
          this.breadcrumbLabel = cd.name;
        },
        (error) => {
          console.log(`error getting case definition: ${error.message}`);
        }
      );
    } else {
      this.breadcrumbLabel = "All Cases";
    }
  }

  private sortCasesByDateCreated(_cases: Case[]): Case[] {
    return (_cases = _cases.sort(
      (_caseA, _caseB) =>
        Date.parse(_caseB["created_at"]) - Date.parse(_caseA["created_at"])
    ));
  }
}
