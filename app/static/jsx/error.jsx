"use strict";
/* global React, ReactDOM, APP, UTIL, API */
/* global RCSeparator, RCLineSeparator, RCPaddedLineSeparator */
/* global RCEqualWidthComponent */
/* global ERROR */
window.addEventListener(APP.events.mainDone.type, () => {
  ReactDOM.render(
    <span className="error">{ERROR}</span>,
    document.querySelector("#" + APP.ids.content)
  );
});