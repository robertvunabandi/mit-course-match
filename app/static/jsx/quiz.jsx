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
  ReactDOM.render(quiz, document.querySelector("#" + APP.ids.root));
}


class Quiz extends React.Component { // jshint ignore:line
  constructor(props) {
    super(props);
    this.state = {
      answered: 0,
      total: props.questions.length,
    };
  }

  render() {
    /* jshint ignore:start */
    return (
      <div>
        <QuizState total={this.state.total} answered={this.state.answered}/>
        <QuizQuestionManager questions={this.props.questions}/>
      </div>
    );
    /* jshint ignore:end */
  }
}

class QuizState extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return (
      <div>
        <div>Your Progress: </div>
        <QuizProgressBar
          percentageCompleted={this.props.answered / this.props.total}
          totalQuestionCount={this.props.total} />
      </div>);
    /* jshint ignore:end */
  }
}

class QuizProgressBar extends React.Component { // jshint ignore:line
  constructor(props) {
    super(props);
  }
  static getColor(percentage_completed, total_question_count) {
    const min_completion_rate =
      QuizConfig.minQuestionToAnswer / total_question_count;
    // TODO - redefine colors better
    if (percentage_completed < min_completion_rate) {
      return "#F00";
    }
    return "#0F0";
  }

  render() {
    const divStyle = {minHeight: "10px"};
    const progressStyle = {
      backgroundColor: QuizProgressBar.getColor(
        this.props.percentageCompleted,
        this.props.totalQuestionCount,
      ),
      minWidth: (this.props.percentageCompleted.toFixed(4) * 100) + "%",
      minHeight: "10px",
      display: "inline-block",
    };
    console.log(this.props.percentageCompleted, this.props.totalQuestionCount);
    /* jshint ignore:start */
    return (
      <div style={divStyle}>
        <span style={progressStyle}>
          {(this.props.percentageCompleted.toFixed(4) * 100)}%
        </span>
      </div>);
    /* jshint ignore:end */
  }
}
class QuizQuestionManager extends React.Component { // jshint ignore:line
  render() {
    /* jshint ignore:start */
    return <div>In Development</div>;
    /* jshint ignore:end */
  }
}

class QuizQuestion extends React.Component { // jshint ignore:line
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
    return <div>In Development</div>;
    /* jshint ignore:end */
  }

}