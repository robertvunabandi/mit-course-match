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
/* global React, ReactDOM, APP, UTIL */
/* global RCSeparator, RCLineSeparator, RCPaddedLineSeparator */

const QuizConfig = {
  minQuestionToAnswer: 1
};

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

  ReactDOM.render(quiz, document.querySelector("#" + APP.ids.content));
}

class Quiz extends React.Component {
  // jshint ignore:line
  constructor(props) {
    super(props);
    const self = this;
    self.state = {
      answered: 0,
      total: props.questions.length,
      questions: []
    };
    props.questions.forEach(function (question) {
      question.answer_aid = null;
      self.state.questions.push(question);
    });
  }

  getAnsweredQuestionsCount() {
    let count = 0;
    this.state.questions.forEach(function (question) {
      if (question.answer_aid) {
        count += 1;
      }
    });
    return count;
  }

  /**
   * picks, among the questions that are not answered, one at random and
   * returns its index. if no unanswered question is found, this will
   * return -1.
   *
   * @return int
   * */
  getUnansweredQuestionIndex() {
    return UTIL.randomFromList(this.state.questions.map((question, index) => !question.answer_aid ? index : -1).filter(index => index > -1));
  }

  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      { className: "quiz" },
      React.createElement(QuizState, { total: this.state.total, answered: this.state.answered }),
      React.createElement(RCSeparator, null),
      React.createElement(QuizQuestionDisplay, {
        question: this.state.questions[this.getUnansweredQuestionIndex()]
      })
    );
    /* jshint ignore:end */
  }
}

/**
 * the QuizState gives context about the state of the app so far.
 * i.e., it provides percentage completed, whether one can submit
 * questions for predictions (since one doesn't have to answer
 * everything), etc. */
class QuizState extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      { className: "quiz-state" },
      React.createElement(
        "div",
        null,
        "Progress:"
      ),
      React.createElement(QuizProgressBar, { percentage: this.props.answered / this.props.total }),
      React.createElement(
        "div",
        null,
        "Answered ",
        this.props.answered,
        " out of ",
        this.props.total
      )
    );
    /* jshint ignore:end */
  }
}

class QuizProgressBar extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "div",
      { className: "quiz-progress-bar" },
      React.createElement(
        "span",
        null,
        this.props.percentage.toFixed(4) * 100,
        "%"
      )
    );
    /* jshint ignore:end */
  }
}

/**
 * with the question display, we display one question at a time that is
 * passed in as a parameter.
 * */
class QuizQuestionDisplay extends React.Component {
  // jshint ignore:line
  constructor(props) {
    super(props);
    this.state = props.question;
  }

  render() {
    /* jshint ignore:start */
    return React.createElement(
      "span",
      { className: "quiz-question-display" },
      React.createElement(QuizQuestion, {
        question: this.props.question.question,
        qid: this.props.question.qid
      }),
      React.createElement(
        "span",
        { className: "quiz-choices" },
        this.props.question.answers.map(answer => {
          return React.createElement(QuizAnswerChoice, { choice: answer.choice, aid: answer.aid });
        })
      )
    );
    /* jshint ignore:end */
  }
}

class QuizQuestion extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "span",
      { className: "quiz-question" },
      React.createElement(QuizQuestionQSymbol, null),
      React.createElement(
        "span",
        null,
        this.props.question
      )
    );
    /* jshint ignore:end */
  }
}

class QuizQuestionQSymbol extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    // TODO - create this symbol
    return React.createElement(
      "span",
      { className: "quiz-question-q-symbol" },
      "QSymbol"
    );
    /* jshint ignore:end */
  }
}

class QuizAnswerChoice extends React.Component {
  // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return React.createElement(
      "span",
      { className: "quiz-answer-choice" },
      this.props.choice
    );
    /* jshint ignore:end */
  }
}