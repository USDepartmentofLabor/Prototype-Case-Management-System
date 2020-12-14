import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";
import { Utils } from "app/_helpers";
import { Note, User } from "app/_models";
import { AuthenticationService } from "app/_services";

@Component({
  selector: "app-notes",
  templateUrl: "./notes.component.html",
  styleUrls: ["./notes.component.css"],
})
export class NotesComponent implements OnInit {
  @Input() notes: Note[];
  @Output() noteAdded = new EventEmitter<string>();
  noteForm: FormGroup;
  inNoteEditMode = false;
  isSavingNote = false;
  currentUser: User = this.authService.currentUserValue;

  constructor(
    private formBuilder: FormBuilder,
    private utils: Utils,
    private authService: AuthenticationService
  ) {
    this.noteForm = this.formBuilder.group({
      note: new FormControl(null, [Validators.required]),
    });
  }

  ngOnInit() {}

  onChangeMode() {
    this.inNoteEditMode = !this.inNoteEditMode;
  }

  onSaveNote() {
    console.log(`[NotesComponent] saving note ${this.noteForm.value.note}`);
    this.isSavingNote = true;

    if (this.noteForm.invalid) {
      this.isSavingNote = false;
    } else {
      console.log("[NotesComponent] emitting noteAdded");

      this.noteAdded.emit(this.noteForm.value.note);
      this.noteForm.reset();

      this.isSavingNote = false;
      this.inNoteEditMode = false;
    }
  }

  public formatNoteCreatedAtDate(date: string): string {
    return this.utils.generateDateFormatFromNow(date);
  }
}
