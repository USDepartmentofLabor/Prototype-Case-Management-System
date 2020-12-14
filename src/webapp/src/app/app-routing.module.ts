import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { ProfileComponent } from './profile/profile.component';
import { DashboardComponent, ProjectComponent, UsersComponent, RolesComponent } from './admin';
import {
    CaseDefinitionsComponent,
    NewCaseDefinitionComponent,
    CasesComponent,
    NewCaseComponent,
    EditCaseComponent
} from './case';
import {
    SurveyCreatorComponent,
    ListSurveysComponent,
    ViewSurveyComponent,
    SurveyResponseComponent
} from './survey';

import { AuthGuard, CanDeactivateGuard } from './_guards';
import { DefaultDashboardComponent } from './admin/default-dashboard/default-dashboard.component';
import { LandingPageComponent, NoPermissionComponent } from './_components';
import { ResetPasswordComponent } from './_components/reset-password/reset-password.component';
import { ActivityComponent } from './activities/activity/activity.component';

export const routes: Routes = [
    {path: 'login', component: LoginComponent},
    {path: 'reset-password/:token', component: ResetPasswordComponent},
    {path: 'landing-page', component: LandingPageComponent, canActivate: [AuthGuard]},
    {path: 'cases', component: CasesComponent, canActivate: [AuthGuard]},
    {path: 'cases/new', component: NewCaseComponent, canActivate: [AuthGuard]},
    {
        path: 'cases/:id', component: EditCaseComponent, canActivate: [AuthGuard],
        children: [
            {path: 'form-response/:id', component: SurveyResponseComponent, canActivate: [AuthGuard], canDeactivate: [CanDeactivateGuard]},
            {path: 'form/:id', component: ViewSurveyComponent, canActivate: [AuthGuard]}
        ]
    },
    {path: 'cases-definitions', component: CaseDefinitionsComponent, canActivate: [AuthGuard]},
    {path: 'cases-definitions/new', component: NewCaseDefinitionComponent, canActivate: [AuthGuard]},
    {path: 'cases-definition/edit/:id', component: NewCaseDefinitionComponent, canActivate: [AuthGuard]},
    {
        path: 'activities/:id', component: ActivityComponent, canActivate: [AuthGuard],
        children: [
            {path: 'form-responses/:id', component: SurveyResponseComponent, canActivate: [AuthGuard], canDeactivate: [CanDeactivateGuard]},
            {path: 'forms/:id', component: ViewSurveyComponent, canActivate: [AuthGuard]}
        ]
    },
    {path: 'admin/dashboard', component: DashboardComponent, canActivate: [AuthGuard]},
    {path: 'admin/users', component: UsersComponent, canActivate: [AuthGuard]},
    {path: 'admin/roles', component: RolesComponent, canActivate: [AuthGuard]},
    {path: 'admin/project', component: ProjectComponent, canActivate: [AuthGuard]},
    {path: 'admin/default-dashboard', component: DefaultDashboardComponent, canActivate: [AuthGuard]},
    {path: 'profile', component: ProfileComponent, canActivate: [AuthGuard]},
    {path: 'create-form', component: SurveyCreatorComponent, canActivate: [AuthGuard]},
    {path: 'form/edit/:id', component: SurveyCreatorComponent, canActivate: [AuthGuard], canDeactivate: [CanDeactivateGuard]},
    {path: 'forms', component: ListSurveysComponent, canActivate: [AuthGuard]},
    {path: 'form/:id', component: ViewSurveyComponent, canActivate: [AuthGuard]},
    {path: 'form-response/:id', component: SurveyResponseComponent, canActivate: [AuthGuard], canDeactivate: [CanDeactivateGuard]},
    {path: 'no-permission', component: NoPermissionComponent},
    {path: '', redirectTo: 'login', pathMatch: 'full'},
    {path: '**', component: LoginComponent}
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
