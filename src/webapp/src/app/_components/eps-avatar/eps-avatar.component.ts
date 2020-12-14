import { Component, Input, OnInit } from "@angular/core";
import { Utils } from "app/_helpers";

@Component({
  selector: "app-eps-avatar",
  templateUrl: "./eps-avatar.component.html",
  styleUrls: ["./eps-avatar.component.css"],
})
export class EpsAvatarComponent implements OnInit {
  @Input() username: string;
  @Input() color: string
  firstInitial: string;

  constructor(private utils: Utils) {}

  ngOnInit() {
    this.firstInitial = this.utils.generateFirstInitalFromUserName(
      this.username
    );
  }
}
