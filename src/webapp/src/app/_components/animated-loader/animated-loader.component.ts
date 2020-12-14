import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-animated-loader',
  templateUrl: './animated-loader.component.html',
  styleUrls: ['./animated-loader.component.css']
})
export class AnimatedLoaderComponent {
  @Input() msgs: string;

  constructor() {}
}
