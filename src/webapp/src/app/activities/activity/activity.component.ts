import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { Utils } from "app/_helpers";
import { ActivityAPI, Note, User } from "app/_models";
import { AuthenticationService } from "app/_services";
import { ActivityService } from "app/_services/activity.service";

@Component({
  selector: "app-activity",
  templateUrl: "./activity.component.html",
  styleUrls: ["./activity.component.css"],
})
export class ActivityComponent implements OnInit {
  activityID: number;
  activity: ActivityAPI;
  isLoading: boolean = true;
  currentUser: User = this.authService.currentUserValue;
  latitude: number;
  longitude: number;

  constructor(
    private activityService: ActivityService,
    private authService: AuthenticationService,
    public route: ActivatedRoute,
    private utils: Utils
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.activityID = params.id;
      this.getActvity(this.activityID);
      this.currentUser.first_initial = this.utils.generateFirstInitalFromUserName(
        this.currentUser.username
      );
      this.currentUser.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
    });
    this.getLocation();
  }

  private getActvity(id: number): void {
    this.isLoading = true;
    this.activityService.getActivity(id).subscribe(
      (data) => {
        this.activity = data;
        //this.documents = this.case.documents;
        //this.currCaseName = this.case.name;
        //this.customFields = this.case.custom_fields;
        this.activity.notes.map((note) => {
          note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
            note.created_by.username
          );
          note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
        });
        this.activity.notes = this.sortCaseNotes(this.activity.notes);

        this.isLoading = false;
      },
      (error) => {
        console.log(
          `[ActivityComponent] error getting activity: ${error.message}`
        );
      }
    );
  }

  private getLocation(): void {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.latitude = position.coords.latitude;
          this.longitude = position.coords.longitude;
        },
        (err) => {
          this.latitude = null;
          this.longitude = null;
          console.log(`[ActivityComponent] ERROR(${err.code}): ${err.message}`);
        }
      );
    } else {
      this.latitude = null;
      this.longitude = null;
      console.log("[ActivityComponent] No support for geolocation");
    }
  }

  // pull out and place into helper class
  private sortCaseNotes(notes: Note[]) {
    return (notes = notes.sort(
      (noteA, noteB) =>
        Date.parse(noteB["created_at"]) - Date.parse(noteA["created_at"])
    ));
  }

  onActivityNameChanged(newName: string): void {
    console.log(`[ActivityComponent] received new name = ${newName}`);

    const data = {
      name: newName,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    this.activityService.updateActivity(this.activity.id, data).subscribe(
      (responseData) => {
        this.activity = responseData;
        this.activity.notes.map((note) => {
          note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
            note.created_by.username
          );
          note.created_by.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
        });
        this.activity.notes = this.sortCaseNotes(this.activity.notes);
        this.utils.generateSuccessToastrMsg(
          "Activity name successfully updated!",
          ""
        );
      },
      (error) => {
        console.log(
          `[ActivityComponent] error saving activity name : error.message`
        );
        this.utils.generateErrorToastrMsg(
          error.message,
          "Error saving activity name"
        );
      }
    );
  }

  onActivityDescriptionChanged(newDescription: string): void {
    console.log(
      `[ActivityComponent] received new description = ${newDescription}`
    );

    const data = {
      description: newDescription,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    this.activityService.updateActivity(this.activity.id, data).subscribe(
      (responseData) => {
        this.activity = responseData;
        this.activity.notes.map((note) => {
          note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
            note.created_by.username
          );
          note.created_by.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
        });
        this.activity.notes = this.sortCaseNotes(this.activity.notes);
        this.utils.generateSuccessToastrMsg(
          "Activity description successfully updated!",
          ""
        );
      },
      (error) => {
        console.log(
          `[ActivityComponent] error saving activity description : error.message`
        );
        this.utils.generateErrorToastrMsg(
          error.message,
          "Error saving activity description"
        );
      }
    );
  }

  onActivityNoteAdded(note: string): void {
    console.log(`[ActivityComponent] received new description = ${note}`);

    this.activityService.saveNote(this.activity.id, note).subscribe(
      (responseData) => {
        this.utils.generateSuccessToastrMsg("Note successfully added", "");
        this.getActvity(this.activityID);
      },
      (error) => {
        console.log(`[ActivityComponent] error adding note : error.message`);
        this.utils.generateErrorToastrMsg(error.message, "Error saving note");
      }
    );
  }

  onActivityIsCompleteChanged(isComplete: boolean): void {
    console.log(`[ActivityComponent] received new isComplete = ${isComplete}`);

    const data = {
      is_complete: isComplete,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    this.activityService.updateActivity(this.activity.id, data).subscribe(
      (responseData) => {
        this.activity = responseData;
        this.activity.notes.map((note) => {
          note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
            note.created_by.username
          );
          note.created_by.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
        });
        this.activity.notes = this.sortCaseNotes(this.activity.notes);
        this.utils.generateSuccessToastrMsg(
          `Activity successfully set as ${isComplete ? "complete" : "incomplete"}.`,
          ""
        );
      },
      (error) => {
        console.log(
          `[ActivityComponent] error changing activity completion flag : error.message`
        );
        this.utils.generateErrorToastrMsg(
          error.message,
          "Error changing activity completion flag."
        );
      }
    );
  }

  onActivityDocumentUpload(): void {
    console.log(`[ActivityComponent] received document uploaded`);
    this.getActvity(this.activityID);
  }

  onActivityDocumentDeleted(): void {
    console.log(`[ActivityComponent] received document deleted`);
    this.getActvity(this.activityID);
  }

}
