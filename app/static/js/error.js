"use strict";
/* global React, ReactDOM, APP, UTIL, API */
/* global RCSeparator, RCLineSeparator, RCPaddedLineSeparator */
/* global RCEqualWidthComponent */
/* global ERROR */

window.addEventListener(APP.events.mainDone.type, () => {
  ReactDOM.render(React.createElement(
    "span",
    { className: "error" },
    ERROR
  ), document.querySelector("#" + APP.ids.content));
});