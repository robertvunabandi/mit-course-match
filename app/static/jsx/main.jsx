/**
 * This is the main js file that will have parameters that are shared
 * with every pages. This js file must be loaded in every html page.
 * */
"use strict";
window.addEventListener("load", main);

const APP = {
  events: {
    mainDone: new Event("mit-course-match-loaded"),
  },
};

function main() {
    window.dispatchEvent(APP.events.mainDone);
}