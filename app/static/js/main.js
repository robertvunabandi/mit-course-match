"use strict";
/**
 * This is the main js file that will have parameters that are shared
 * with every pages. This js file must be loaded in every html page.
 * */

// the main function is declared at the end of this file

window.addEventListener("load", main);

/**
 * contains constants used throughout the application
 * */
const APP = {
  // custom HTML events that can be triggered by the application
  events: {
    mainDone: new Event("mit-course-match-loaded")
  },
  // ids of various HTML elements
  ids: {
    navigationBar: "navigation-bar",
    content: "content",
    footer: "footer"
  }
};

/**
 * below we define a set of reusable component across the site.
 * all these class will start with the prefix "RC", which stands
 * for "Reusable Component". */
function RCSeparator() {
  return React.createElement("div", { className: "rc-separator" });
}

function RCLineSeparator() {
  return React.createElement("div", { className: "rc-line-separator" });
}

function RCPaddedLineSeparator() {
  return React.createElement(
    "span",
    null,
    React.createElement(RCSeparator, null),
    React.createElement(RCLineSeparator, null),
    React.createElement(RCSeparator, null)
  );
}

/**
 * the main function call. this gets called at the start of every
 * page in this app.
 * */
function main() {
  window.dispatchEvent(APP.events.mainDone);
}