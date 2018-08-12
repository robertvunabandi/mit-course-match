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
  minQuestionToAnswer: 1,
};

window.addEventListener(APP.events.mainDone.type, loadQuiz);

function loadQuiz() {
  // load questions via API call, todo - write API from 6.148
  /* jshint ignore:start */
  const quiz = <Quiz questions={[{
    question: "hello there",
    qid: 35,
    answers: [
      {choice: "Lemon", aid: 46},
      {choice: "Almond", aid: 55}
    ]
  },
    {
      question: "okay tell me",
      qid: 24,
      answers: [
        {choice: "No", aid: 41},
        {choice: "Yes", aid: 31}
      ]
    }]}/>;
  /* jshint ignore:end */

  ReactDOM.render(quiz, document.querySelector("#" + APP.ids.content));
}


class Quiz extends React.Component { // jshint ignore:line
  constructor(props) {
    super(props);
    const self = this;
    self.state = {
      answered: 0,
      total: props.questions.length,
      questions: [],
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
    return UTIL.randomFromList(
      this.state.questions
        .map((question, index) => !question.answer_aid ? index : -1)
        .filter((index) => index > -1)
    );
  }

  render() {
    /* jshint ignore:start */
    return (
      <div className={"quiz"}>
        <QuizState total={this.state.total} answered={this.state.answered}/>
        <RCSeparator/>
        <QuizQuestionDisplay
          question={this.state.questions[this.getUnansweredQuestionIndex()]}
        />
      </div>
    );
    /* jshint ignore:end */
  }
}

/**
 * the QuizState gives context about the state of the app so far.
 * i.e., it provides percentage completed, whether one can submit
 * questions for predictions (since one doesn't have to answer
 * everything), etc. */
class QuizState extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return (
      <div className={"quiz-state"}>
        <div>Progress:</div>
        <QuizProgressBar percentage={this.props.answered / this.props.total}/>
        <div>Answered {this.props.answered} out of {this.props.total}</div>
      </div>);
    /* jshint ignore:end */
  }
}

class QuizProgressBar extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return (
      <div className={"quiz-progress-bar"}>
        <span>
          {(this.props.percentage.toFixed(4) * 100)}%
        </span>
      </div>);
    /* jshint ignore:end */
  }
}

/**
 * with the question display, we display one question at a time that is
 * passed in as a parameter.
 * */
class QuizQuestionDisplay extends React.Component { // jshint ignore:line
  constructor(props) {
    super(props);
    this.state = props.question;
  }

  render() {
    /* jshint ignore:start */
    return (
      <span className={"quiz-question-display"}>
        <QuizQuestion
          question={this.props.question.question}
          qid={this.props.question.qid}
        />
        <span className={"quiz-choices"}>
          {this.props.question.answers.map(
            (answer) => {
              return (
                <QuizAnswerChoice choice={answer.choice} aid={answer.aid} />
              );
            }
          )}
        </span>
      </span>
    );
    /* jshint ignore:end */
  }
}

class QuizQuestion extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return (
      <span className={"quiz-question"}>
        <QuizQuestionQSymbol />
        <span>{this.props.question}</span>
      </span>
    );
    /* jshint ignore:end */
  }
}

class QuizQuestionQSymbol extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    // TODO - create this symbol
    return <span className={"quiz-question-q-symbol"}>QSymbol</span>;
    /* jshint ignore:end */
  }
}

class QuizAnswerChoice extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return <span className={"quiz-answer-choice"}>{this.props.choice}</span>;
    /* jshint ignore:end */
  }
}
