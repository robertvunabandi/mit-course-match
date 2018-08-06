// see https://realpython.com/the-ultimate-flask-front-end/#react-round-one
"use strict";
const gulp = require("gulp");
// const gulpBrowser = require("gulp-browser");
// const reactify = require("reactify");
const del = require("del");
const size = require("gulp-size");
const babel = require("gulp-babel");


gulp.task("del", function () {
  return del(["./app/static/js"]);
});


gulp.task("transform", function () {
  return gulp.src("./app/static/jsx/*.jsx")
    .pipe(size())
    .pipe(babel({plugins: ["transform-react-jsx"]}))
    .pipe(gulp.dest("./app/static/js/"));
});

gulp.task(
  "default",
  ["del"],
  function () {
    gulp.start("transform");
    gulp.watch("./app/static/jsx/*.jsx", ["transform"]);
  }
);