"use strict";
/* global React, ReactDOM, APP, UTIL, API */
/* global RCSeparator, RCLineSeparator, RCPaddedLineSeparator */
/* global RCEqualWidthComponent */
/* global ERROR STATUS */

const DEFAULT_ERROR = "An Unknown Error Happened";
window.addEventListener(APP.events.mainDone.type, () => {
  const status_component = React.createElement(
    "span",
    { className: "error-status" },
    "Status Code: ",
    React.createElement(
      "span",
      { className: "error-status-code" },
      STATUS
    )
  );
  ReactDOM.render(React.createElement(
    "span",
    { className: "error" },
    ERROR.length > 0 ? ERROR : DEFAULT_ERROR,
    status_component
  ), document.querySelector("#" + APP.ids.content));
});