# EPS Angular UI

This project was generated with [Angular CLI](https://github.com/angular/angular-cli)

## Development server

 Run `npm i` to install all of the node packages then, Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running unit test and running the code coverage generator

Run `ng test --code-coverage` to execute code coverage and run test.
view code coverage `web-app/coverage/index.html`

## Deploying

The instructions below are still valid for the development branch and site; you
can deploy the app the way it is described below. However, auto devops haa
been setup for the `develop` and `master` branches. If you push to those
branches the app will automatically be deployed according to the table below.

| Branch    | Deployment Destination |
|-----------|------------------------|
| `develop` | development site - [http://eps-dev.dbmspilot.org.s3-website-us-east-1.amazonaws.com](http://eps-dev.dbmspilot.org.s3-website-us-east-1.amazonaws.com) |
| `master`  | demo site - [https://eps-demo.dbmspilot.org](https://eps-demo.dbmspilot.org) |

It is assumed you have configured the AWS CLI for access to the ILAB Toolkit
account.

Please see the following for configuring the AWS CLI.

[Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

### Dev App

After the preject has been built. Run the following command to deploy to the
development app.

`$ aws s3 sync dist/ s3://eps-dev.dbmspilot.org --delete`

This will:

1. delete the contents of the dev app's S3 bucket
1. copy the contents of the `dist/` directory to the dev app's S3 bucket

If you have multiple AWS accounts/profiles configured you can specify the
profile using this command.

`$ aws s3 sync dist/ s3://eps-dev.dbmspilot.org --delete --profile <profile_name>`

```text
s3://eps-deployments/production/eps-ui.zip

aws deploy push --application-name EPS --s3-location s3://eps-deployments/production/eps-ui.zip --ignore-hidden-files --source dist --profile ilab-jclements

aws deploy create-deployment --application-name EPS --s3-location bucket=eps-deployments,key=production/eps-ui.zip,bundleType=zip,eTag=c45c882c6d1f05d569614af77e9742f2-3,version=BT_Z.DBvgBsUX2wB7kY0nThafa1jv5bm --deployment-group-name EPSDemoDeploymentGroup -- profile aws deploy push --application-name EPS --s3-location s3://eps-deployments/production/eps-ui.zip --ignore-hidden-files --source dist --profile ilab-jclements



aws deploy create-deployment --application-name EPS --s3-location bucket=eps-deployments,key=production/eps-ui.zip,bundleType=zip,eTag=c45c882c6d1f05d569614af77e9742f2-3,version=b32knJYQtTiiOXrWyfal2E4gTb_GVWTZ --deployment-group-name EPSDemoDeploymentGroup --profile ilab-jclements

aws deploy create-deployment --application-name EPS --s3-location bucket=eps-deployments,key=production/eps-ui.zip,bundleType=zip,eTag=4264079ad2d68b372f7f4731b0c86ab4-3,version=B1BMJB4USn_QLKizjmkzP.V_q9yvVqLY --deployment-group-name EPSDemoDeploymentGroup --profile ilab-jclements
```

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).

## Manual Version Update

Manually update the version of the app based on the current sprint version, located in the  src/app/login/login.component.ts
