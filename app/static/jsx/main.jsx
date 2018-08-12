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
    mainDone: new Event("mit-course-match-loaded"),
  },
  // HTML ids of various elements
  ids: {
    navigationBar: "navigation-bar",
    content: "content",
    footer: "footer",
  },
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

/**
 * below we define a set of reusable component across the site.
 * all these class will start with the prefix "RC", which stands
 * for "Reusable Component". */
function RCSeparator() {
  /* jshint ignore:start */
  return <div className={"rc-separator"}></div>;
  /* jshint ignore:end */
}

function RCLineSeparator() {
  /* jshint ignore:start */
  return <div className={"rc-line-separator"}></div>;
  /* jshint ignore:end */
}

function RCPaddedLineSeparator() {
  /* jshint ignore:start */
  return (
    <span>
      <RCSeparator/>
      <RCLineSeparator/>
      <RCSeparator/>
    </span>
  );
  /* jshint ignore:end */
}