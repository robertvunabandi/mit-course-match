/*
 * This is the main js file that will have parameters that are shared
 * with every pages. This js file must be loaded in every html page.
 * */
"use strict";

window.addEventListener("load", main);

/** APP contains constants used throughout the application. */
const APP = {
  // custom HTML events that can be triggered by the application
  events: {
    mainDone: new Event("mit-course-match-loaded")
  },
  // HTML ids of various elements
  ids: {
    navigationBar: "navigation-bar",
    root: "root",
    footer: "footer"
  }
};

function main() {
  window.dispatchEvent(APP.events.mainDone);
}

/** utility functions */
const UTIL = {
  // converts string to an HTML id selector
  id(string) {
    return "#" + string;
  }
};