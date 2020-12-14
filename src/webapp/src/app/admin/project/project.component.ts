import { Component, OnInit } from '@angular/core';
import { AdminService  } from '../../_services';
import { Utils } from '../../_helpers';
import { FormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { dateValidator } from '../../_helpers';
import { Project } from '../../_models';

@Component({
  selector: 'app-project',
  templateUrl: './project.component.html',
  styleUrls: ['./project.component.css']
})
export class ProjectComponent implements OnInit {
  editProjectMode: boolean = false;
  isProjectLoaded: boolean = false;
  savingProjectData: boolean = false;
  submitted: boolean = false;
  projectForm: FormGroup;
  project: Project;

  constructor(private utils: Utils, private adminService: AdminService, private formBuilder: FormBuilder) { 
    this.projectForm = this.formBuilder.group({
      name: new FormControl(null, Validators.required),
      organization: new FormControl(null, Validators.required),
      title: new FormControl(null, Validators.required),
      agreement_number: new FormControl(null, Validators.required),
      start_date: new FormControl(null, Validators.required),
      end_date: new FormControl(null, Validators.required),
      funding_amount: new FormControl(null, Validators.required),
      location: new FormControl(null, Validators.required)
    },{
      validator: dateValidator('start_date', 'end_date')
    });
  }

  ngOnInit() {
    this.getProjectData();
  }

  get form() {
    return this.projectForm.controls;
  }

  public formatDate(_date: string): string {
    return _date ? this.utils.generateQueueDateFormat(_date) : '';
  }

  public getProjectData():void {
    this.adminService.getProject().subscribe(
      (data) => {
           this.project = data;
           this.isProjectLoaded = true;
         },
         error => {
           console.log(error.message);
         }
       );
  }

  public setEditProjectMode(): void {
    this.editProjectMode = this.editProjectMode ? false : true;
    const {
      name,
      organization,
      title,
      funding_amount,
      start_date,
      end_date,
      agreement_number,
      location,
    } = this.project;


    if (this.editProjectMode) {
      this.projectForm.patchValue({
        name,
        title,
        organization,
        funding_amount,
        agreement_number,
        location,
        start_date,
        end_date
      });
    }
  }

  public save(): void {
    let projectDataObj = {
      name: this.projectForm.value.name,
      title: this.projectForm.value.title,
      organization: this.projectForm.value.organization,
      agreement_number: this.projectForm.value.agreement_number,
      location: this.projectForm.value.location,
      start_date: this.projectForm.value.start_date,
      end_date: this.projectForm.value.end_date,
      funding_amount: this.projectForm.value.funding_amount

    };

    this.savingProjectData = true;
    this.submitted = true;
    
    if (this.projectForm.invalid) {
      this.savingProjectData = false;
    } else {
      this.adminService.updateRole(projectDataObj).subscribe(() => {
        this.savingProjectData = this.editProjectMode = false;
        this.utils.generateSuccessToastrMsg('Successsfully updated your project information', '');
        this.getProjectData();
      }); 
    }
  }
}
