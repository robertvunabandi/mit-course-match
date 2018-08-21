"use strict";
/**
 * utility functions
 * */


const UTIL = {};
UTIL.invariant = function (bool, msg) {
  if (!bool) {
    throw msg || "invariant failure";
  }
};
UTIL.isInteger = function (el) {
  if (typeof el !== "number" || isNaN(el)) {
    return false;
  }
  return Math.floor(el) === el;
};
// similar to python range
UTIL.range = function (...args) {
  let [min, max, step] = args;
  if (!step) {
    step = 1;
    if (!max) {
      max = min;
      min = 0;
    }
  }
  UTIL.invariant(UTIL.isInteger(min), "min must be an integer");
  UTIL.invariant(UTIL.isInteger(max), "max must be an integer");
  UTIL.invariant(UTIL.isInteger(step), "step must be an integer");
  UTIL.invariant(step !== 0, "step cannot be 0");
  UTIL.invariant(
    step < 0 ? max < min : min < max,
    `if the step is ${step < 0 ? "negative" : "positive"}, ` +
    `the max must be ${step < 0 ? "smaller" : "larger"} than min`
  );
  let count = Math.ceil((max - min) / step);
  return Array.from(Array(count)).map((_, i) => (step * i) + min);
};
UTIL.randomFloatInInclusiveRange = function (min, max) {
  return Math.random() * (max - min) + min;
};
UTIL.randomIntInInclusiveRange = function (min, max) {
  return Math.round(UTIL.randomFloatInInclusiveRange(min, max));
};
UTIL.randomFromList = function (list) {
  return list[UTIL.randomIntInInclusiveRange(0, list.length - 1)];
};
UTIL.shallowArrayCopy = (array) => array.map((el) => el);
// performs Fisher-Yates (Knuth) shuffle algorithm and makes a copy
UTIL.shuffleList = function (array) {
  let array_copy = UTIL.shallowArrayCopy(array);
  let temp, random_index;
  for (let index = array_copy.length; index > 0; index -= 1) {
    random_index = Math.floor(Math.random() * index);
    temp = array_copy[index - 1];
    array_copy[index - 1] = array_copy[random_index];
    array_copy[random_index] = temp;
  }
  return array_copy;
};