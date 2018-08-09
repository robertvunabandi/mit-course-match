/**
 * This is the mainDone quiz component block.
 * This block handles rendering and answering the questions.
 *
 * Some things to note:
 * - Storing question answers will be done externally.
 * - This quiz component will not know about who is answering the questions.
 *   It will store answers locally and the answers can be fetched from it.
 * - The quiz will take in questions and then manage itself with a few
 *   external endpoints to get answered questions and such.
 * */
"use strict";
/* global React, ReactDOM, APP */

window.addEventListener(APP.events.mainDone.type, loadQuiz);

function loadQuiz() {
  // load questions via API call, todo - write API from 6.148
  /* jshint ignore:start */
  const quiz = React.createElement(Quiz, { questions: [{
      question: "hello there",
      qid: 35,
      answers: [{ choice: "Lemon", aid: 46 }, { choice: "Almond", aid: 55 }]
    }, {
      question: "okay tell me",
      qid: 24,
      answers: [{ choice: "No", aid: 41 }, { choice: "Yes", aid: 31 }]
    }] });
  /* jshint ignore:end */
  ReactDOM.render(quiz, document.getElementById("root"));
}

/* global React */
class Quiz extends React.Component {
  // jshint ignore:line
  constructor(props) {
    super(props);
    this.state = {
      answered: 0,
      total: props.questions.length
    };
  }

  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      null,
      React.createElement(QuizState, { total: this.state.total, answered: this.state.answered }),
      React.createElement(QuizQuestionManager, { questions: this.props.questions })
    );
    /* jshint ignore:end */
  }
}

class QuizState extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      null,
      "In Development"
    );
    /* jshint ignore:end */
  }
}

class QuizQuestionManager extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      null,
      "In Development"
    );
    /* jshint ignore:end */
  }
}

class QuizQuestion extends React.Component {
  // jshint ignore:line
  constructor(props) {
    super(props);
    this.state = {
      answer: null
    };
  }

  isAnswered() {
    return this.state.answer !== null;
  }

  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      null,
      "In Development"
    );
    /* jshint ignore:end */
  }

}