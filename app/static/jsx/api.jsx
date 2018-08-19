/**
 * This file contains methods to make "api" calls to the back-end.
 * There is no POST method since this is a static website.
 **/
"use strict";

const API = {};

API.formatParams = function (params) {
  return Object
    .keys(params)
    .map(function (key) {
      return key + "=" + encodeURIComponent(params[key]);
    })
    .join("&");
};

API.get = function (endpoint, params, successCallback, failureCallback) {
  const xhr = new XMLHttpRequest();
  const fullPath = endpoint + "?" + API.formatParams(params);
  xhr.open("GET", fullPath, true);
  xhr.onload = function (error) {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        if (successCallback) {
          successCallback(JSON.parse(xhr.responseText));
        }
      } else if (failureCallback) {
        failureCallback({text: xhr.statusText, url: xhr.responseURL});
      }
    }
  };
  xhr.onerror = function (error) {
    failureCallback({text: xhr.statusText, url: xhr.responseURL, error: error});
  };
  xhr.send(null);
};

API.post = function (endpoint, params, successCallback, failureCallback) {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", endpoint, true);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.withCredentials = true;
  xhr.onload = function (error) {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        if (successCallback) {
          successCallback(JSON.parse(xhr.responseText));
        }
      } else if (failureCallback) {
        failureCallback({text: xhr.statusText, url: xhr.responseURL});
      }
    }
  };
  xhr.onerror = function (error) {
    failureCallback({text: xhr.statusText, url: xhr.responseURL, error: error});
  };
  xhr.send(JSON.stringify(params));
};