/*
 * This is the main js file that will have parameters that are shared
 * with every pages. This js file must be loaded in every html page.
 * */
"use strict";

// the main function is declared at the end of this file

window.addEventListener("load", main);

/**
 * APP contains constants used throughout the application.
 * */

const APP = {
  // custom HTML events that can be triggered by the application
  events: {
    mainDone: new Event("mit-course-match-loaded")
  },
  // HTML ids of various elements
  ids: {
    navigationBar: "navigation-bar",
    content: "content",
    footer: "footer"
  }
};

/**
 * utility functions
 * */

const UTIL = {};
UTIL.randomFloatInInclusiveRange = function (min, max) {
  return Math.random() * (max - min) + min;
};
UTIL.randomIntInInclusiveRange = function (min, max) {
  return Math.round(UTIL.randomFloatInInclusiveRange(min, max));
};
UTIL.randomFromList = function (list) {
  return list[UTIL.randomIntInInclusiveRange(0, list.length - 1)];
};

/**
 * below we define a set of reusable component across the site.
 * all these class will start with the prefix "RC", which stands
 * for "Reusable Component". */
function RCSeparator() {
  /* jshint ignore:start */
  return React.createElement("div", { className: "rc-separator" });
  /* jshint ignore:end */
}

function RCLineSeparator() {
  /* jshint ignore:start */
  return React.createElement("div", { className: "rc-line-separator" });
  /* jshint ignore:end */
}

function RCPaddedLineSeparator() {
  /* jshint ignore:start */
  return React.createElement(
    "span",
    null,
    React.createElement(RCSeparator, null),
    React.createElement(RCLineSeparator, null),
    React.createElement(RCSeparator, null)
  );
  /* jshint ignore:end */
}

function main() {
  window.dispatchEvent(APP.events.mainDone);
}