"use strict";
/**
 * this is the mainDone quiz component block.
 * this block handles rendering and answering the questions.
 *
 * some things to note:
 * - Storing question answers will be done externally.
 * - This quiz component will not know about who is answering the
 *   questions. It will store answers locally and the answers can
 *   be fetched from it.
 * - The quiz will take in questions and then manage itself with a
 *   few external endpoints to get answered questions and such.
 * */
/* global React, ReactDOM, APP, UTIL, API */
/* global RCSeparator, RCLineSeparator, RCPaddedLineSeparator */

const QuizConfig = {
  minQuestionToAnswer: 1
};

window.addEventListener(APP.events.mainDone.type, loadQuiz);

function loadQuiz() {
  API.get("/questions", {}, function (questions) {
    const quiz = React.createElement(Quiz, { questions: questions });
    ReactDOM.render(quiz, document.querySelector("#" + APP.ids.content));
  });
}

class Quiz extends React.Component {
  constructor(props) {
    super(props);
    const self = this;
    self.state = {
      answered: 0,
      total: props.questions.length,
      questions: [],
      answers: {}
    };
    props.questions.forEach(function (question) {
      self.state.questions.push(question);
    });
  }

  getAnsweredQuestionsCount(answers) {
    let count = 0;
    const self = this;
    this.state.questions.forEach(function (question) {
      if (answers[question.qid]) {
        count += 1;
      }
    });
    return count;
  }

  /**
   * picks, among the questions that are not answered, one at random
   * and returns its index. if no unanswered question is found, this
   * will return -1.
   *
   * @return int
   * */
  getUnansweredQuestionIndex() {
    let index = UTIL.randomFromList(this.state.questions.map((question, index) => !this.state.answers[question.qid] ? index : -1).filter(index => index > -1));
    if (index === undefined) {
      return -1;
    }
    return index;
  }

  setAnswer(qid, aid) {
    const self = this;
    this.setState((prevState, props) => {
      const update = { answers: {} };
      update.answers[qid] = aid;
      for (let qid_ans in prevState.answers) {
        if (Object.prototype.hasOwnProperty.call(prevState.answers, qid_ans)) {
          update.answers[qid_ans] = prevState.answers[qid_ans];
        }
      }
      update.answered = self.getAnsweredQuestionsCount(update.answers);
      return update;
    });
  }

  render() {
    const index = this.getUnansweredQuestionIndex();
    let quiz_display = null;
    if (index > -1) {
      const question = this.state.questions[index];
      quiz_display = React.createElement(QuizQuestionDisplay, {
        question: question.question,
        qid: question.qid,
        choices: question.choices,
        setAnswer: (qid, aid) => this.setAnswer.call(this, qid, aid)
      });
    } else {
      quiz_display = React.createElement(QuizQuestionDisplayCompleted, { total: this.state.total });
    }
    return React.createElement(
      "div",
      { className: "quiz" },
      React.createElement(QuizState, { total: this.state.total, answered: this.state.answered }),
      React.createElement(RCSeparator, null),
      quiz_display
    );
  }
}

/**
 * the QuizState gives context about the state of the app so far.
 * i.e., it provides percentage completed, whether one can submit
 * questions for predictions (since one doesn't have to answer
 * everything), etc. */
class QuizState extends React.Component {
  render() {
    return React.createElement(
      "div",
      { className: "quiz-state" },
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
  }
}

class QuizProgressBar extends React.Component {
  render() {
    console.log(this.props.percentage.toFixed(4) * 100);
    return React.createElement(
      "div",
      { className: "quiz-progress-bar" },
      React.createElement(
        "span",
        { style: { width: this.props.percentage.toFixed(4) * 100 + "%" } },
        this.props.percentage.toFixed(4) * 100,
        "%"
      )
    );
  }
}

/**
 * with the question display, we display one question at a time that
 * is passed in as a parameter.
 * */
class QuizQuestionDisplay extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const self = this;
    return React.createElement(
      "span",
      { className: "quiz-question-display" },
      React.createElement(QuizQuestion, {
        question: this.props.question,
        qid: this.props.qid
      }),
      React.createElement(
        "span",
        { className: "quiz-choices" },
        this.props.choices.map(answer => {
          return React.createElement(QuizAnswerChoice, {
            choice: answer.choice,
            aid: answer.aid,
            onClick: () => self.props.setAnswer.call(self, self.props.qid, answer.aid)
          });
        })
      )
    );
  }
}

function QuizQuestionDisplayCompleted(props) {
  return React.createElement(
    "span",
    { className: "quiz-question-display" },
    "You answered all ",
    props.total,
    " questions in this quiz!"
  );
}

class QuizQuestion extends React.Component {
  render() {
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
  }
}

class QuizQuestionQSymbol extends React.Component {
  render() {
    // todo - create this symbol
    return React.createElement(
      "span",
      { className: "quiz-question-q-symbol" },
      "QSymbol"
    );
  }
}

class QuizAnswerChoice extends React.Component {
  render() {
    return React.createElement(
      "span",
      {
        className: "quiz-answer-choice",
        onClick: this.props.onClick },
      this.props.choice
    );
  }
}