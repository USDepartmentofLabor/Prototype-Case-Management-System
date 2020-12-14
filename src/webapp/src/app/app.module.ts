import { JwtInterceptor } from './_helpers';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { ToastrModule } from 'ngx-toastr';
import { NgbModule, } from '@ng-bootstrap/ng-bootstrap';
import { AppComponent } from './app.component';
import { ProfileComponent, ProfileSkeletonComponent } from './profile/profile.component';
import { HeaderComponent } from './_components/header/header.component';
import { Interceptor } from './_helpers';
import { AuthGuard, CanDeactivateGuard, HasPermDirective } from './_guards';
import { LoginComponent } from './login/login.component';
import { Angular2FontawesomeModule } from 'angular2-fontawesome';
import { FileUploadModule } from 'ng2-file-upload';
import { NgxSortableModule } from 'ngx-sortable';
import { AvatarModule } from 'ngx-avatar';
import { DataTablesModule } from 'angular-datatables';

import {
    SurveyComponent,
    SurveyCreatorComponent,
    ListSurveysComponent,
    ListSurveySkeletonComponent,
    ViewSurveyComponent,
    SurveyResponseComponent
} from './survey';
import {
    AnimatedLoaderComponent,
    AddDocumentsModalComponent,
    ChangePasswordModalComponent,
    DialogComponent,
    AddUserModalComponent,
    UploadDocumentsModalComponent,
    AddCustomFieldModalComponent,
    StatusBadgeComponent,
    CustomFieldsCreatorComponent,
    RenderCustomFieldsComponent
} from './_components';
import {
    DashboardComponent,
    DashboardSkeletonComponent
} from './admin';
import {
    CaseDefinitionsComponent,
    NewCaseDefinitionComponent,
    CasesComponent,
    NewCaseComponent,
    EditCaseComponent
} from './case';
import { RolesComponent, ProjectComponent, UsersComponent, UsersSkeletonComponent } from './admin';
import { TextCustomFieldComponent } from './_components';
import { NumberCustomFieldComponent } from './_components';
import { DateCustomFieldComponent } from './_components';
import { TextareaCustomFieldComponent } from './_components';
import { SelectCustomFieldComponent } from './_components';
import { CheckboxCustomFieldComponent } from './_components';
import {
    RadioButtonCustomFieldComponent
} from './_components';
import { RankListCustomFieldComponent } from './_components';
import { DefaultDashboardComponent } from './admin/default-dashboard/default-dashboard.component';
import { LandingPageComponent } from './_components';
import { MetabaseDashboardComponent } from './_components';
import { NoPermissionComponent } from './_components/no-permission/no-permission.component';
import { ResetPasswordComponent } from './_components/reset-password/reset-password.component';
import { ActivityComponent } from './activities/activity/activity.component';
import { LeftPaneComponent } from './activities/activity/left-pane/left-pane.component';
import { RightPaneComponent } from './activities/activity/right-pane/right-pane.component';
import { EpsAvatarComponent } from './_components/eps-avatar/eps-avatar.component';
import { EditActivityNameComponent } from './activities/activity/edit-activity-name/edit-activity-name.component';
import { EditActivityDescriptionComponent } from './activities/activity/edit-activity-description/edit-activity-description.component';
import { NotesComponent } from './_components/notes/notes.component';
import { ActivityDefinitionFormComponent } from './activities/activity_definitions/activity-definition-form/activity-definition-form.component';
import { NewActivityModalComponent } from './activities/new-activity-modal/new-activity-modal.component';
import { HistoryComponent } from './_components/history/history.component';


@NgModule({
    declarations: [
        AppComponent,
        SurveyComponent,
        SurveyCreatorComponent,
        ListSurveysComponent,
        ListSurveySkeletonComponent,
        ViewSurveyComponent,
        HeaderComponent,
        AnimatedLoaderComponent,
        LoginComponent,
        DashboardComponent,
        DashboardSkeletonComponent,
        AddUserModalComponent,
        AddCustomFieldModalComponent,
        ProfileComponent,
        ProfileSkeletonComponent,
        ChangePasswordModalComponent,
        SurveyResponseComponent,
        DialogComponent,
        CasesComponent,
        AddDocumentsModalComponent,
        CaseDefinitionsComponent,
        NewCaseComponent,
        EditCaseComponent,
        NewCaseDefinitionComponent,
        UploadDocumentsModalComponent,
        StatusBadgeComponent,
        CustomFieldsCreatorComponent,
        RenderCustomFieldsComponent,
        RolesComponent,
        ProjectComponent,
        UsersComponent,
        UsersSkeletonComponent,
        HasPermDirective,
        TextCustomFieldComponent,
        NumberCustomFieldComponent,
        DateCustomFieldComponent,
        TextareaCustomFieldComponent,
        SelectCustomFieldComponent,
        CheckboxCustomFieldComponent,
        RadioButtonCustomFieldComponent,
        RankListCustomFieldComponent,
        DefaultDashboardComponent,
        LandingPageComponent,
        MetabaseDashboardComponent,
        NoPermissionComponent,
        ResetPasswordComponent,
        ActivityComponent,
        LeftPaneComponent,
        RightPaneComponent,
        EpsAvatarComponent,
        EditActivityNameComponent,
        EditActivityDescriptionComponent,
        NotesComponent,
        ActivityDefinitionFormComponent,
        NewActivityModalComponent,
        HistoryComponent
    ],
    imports: [
        BrowserModule,
        FormsModule,
        HttpClientModule,
        AppRoutingModule,
        NgbModule,
        Angular2FontawesomeModule,
        ReactiveFormsModule,
        FileUploadModule,
        NgxSortableModule,
        ToastrModule.forRoot({
            timeOut: 50000,
            positionClass: 'toast-top-right',
            preventDuplicates: true
        }),
        BrowserAnimationsModule,
        AvatarModule,
        DataTablesModule
    ],
    providers: [
        {provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true},
        {provide: HTTP_INTERCEPTORS, useClass: Interceptor, multi: true},
        CanDeactivateGuard,
        AuthGuard
    ],
    exports: [HasPermDirective],
    bootstrap: [AppComponent],
    entryComponents: [
        AddUserModalComponent,
        DialogComponent,
        ChangePasswordModalComponent,
        AddDocumentsModalComponent,
        UploadDocumentsModalComponent,
        AddCustomFieldModalComponent,
        NewActivityModalComponent
    ]
})
export class AppModule {
}
