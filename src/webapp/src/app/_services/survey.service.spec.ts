/* tslint:disable:no-unused-variable */

import { TestBed } from '@angular/core/testing';
import { SurveyService } from '../_services/survey.service';
import {
  HttpClientTestingModule,
  HttpTestingController
} from '@angular/common/http/testing';
import { dxSurveyService } from 'survey-angular';

describe('Service: SurveyService', () => {
  let httpTestingController: HttpTestingController;
  let service: SurveyService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [dxSurveyService],
      imports: [HttpClientTestingModule]
    });

    // We inject our service (which imports the HttpClient) and the Test Controller
    httpTestingController = TestBed.get(HttpTestingController);
    service = TestBed.get(SurveyService);
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should fetch all surveys from API via GET', () => {
    const data = [
      {
        created_at: '2019-08-30T16:01:10.510338+00:00',
        id: 7,
        name: 'Testing two or more surveys.',
        response: [5],
        structure:
          '{"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1", "title": "This is another test"}]}, {"name": "page2", "elements": [{"type": "text", "name": "question2", "title": "This is another question"}]}]}',
        updated_at: '2019-08-30T16:01:10.510346+00:00'
      },
      {
        created_at: '2019-08-30T18:28:51.787122+00:00',
        id: 8,
        name: 'Election survey',
        response: [],
        structure:
          '{"pages": [{"name": "page1", "elements": [{"type": "checkbox", "name": "question1", "title": "Who will win the 2020 election?", "choices": [{"value": "item1", "text": "Mickey Mouse"}, {"value": "item2", "text": "Superman"}, {"value": "item3", "text": "Spiderman"}]}]}]}',
        updated_at: '2019-08-30T18:28:51.787128+00:00'
      }
    ];

    service.getAllSurveys().subscribe(surveys => {
      expect(surveys.length).toBe(2);
      //expect(surveys).toBe('json');
    });

    const req = httpTestingController.expectOne(`${service.remoteAPI}/surveys/?archived=none`);

    expect(req.request.method).toEqual('GET');

    req.flush(data);
  });

  // it('should fetch a survey by id from API via GET', () => {
  //   const surveyID = 7;
  //   const data = {
  //     created_at: "2019-08-30T16:01:10.510338+00:00",
  //     id: 7,
  //     name: "Testing two or more surveys.",
  //     response: [
  //       5
  //     ],
  //     structure: "{\"pages\": [{\"name\": \"page1\", \"elements\": [{\"type\": \"text\", \"name\": \"question1\", \"title\": \"This is another test\"}]}, {\"name\": \"page2\", \"elements\": [{\"type\": \"text\", \"name\": \"question2\", \"title\": \"This is another question\"}]}]}",
  //     updated_at: "2019-08-30T16:01:10.510346+00:00"
  //   };


    // service.getSurvey(surveyID).subscribe(survey => {
    //   expect(survey).toBe(data);
    // });

  //   const req = httpTestingController.expectOne(`${service.remoteAPI}/surveys/${surveyID}`);

  //   expect(req.request.method).toEqual('GET');

  //   req.flush(data);
  // });

  it('should save a new survey to API via POST', () => {
    const data = {
        structure: [
            {
                "name": "question2",
                "title": "Who will win the 2021 election?",
                "type": "text"
            }
        ],
        name: "page2"
    };
    
    service.saveSurvey(data).subscribe(survey => {
      expect(survey).toEqual(data);
    });

    const req = httpTestingController.expectOne(`${service.remoteAPI}/surveys/`);

    expect(req.request.method).toEqual('POST');

    req.flush(data);

  });

  // Still needs work!
  /*
  it('should save survey response to API via POST', () => {
    let surveyID = 9;
    const data = {
        structure: {
            "question1": "another one"
        }
    };
    
    service.saveSurveyResponse(data).subscribe(survey => {
      expect(survey).toEqual(data);
    });

    const req = httpTestingController.expectOne(`${service.API_URL}/surveys/${surveyID}/responses`);
  
    expect(req.request.method).toEqual('POST');

    req.flush(data);

  });
  */
});
