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
  minQuestionToAnswer: 1,
};

window.addEventListener(APP.events.mainDone.type, loadQuiz);

function loadQuiz() {
  API.get("/questions", {}, function (questions) {
    const quiz = <Quiz questions={questions}/>;
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
   * picks, among the questions that are not answered, one at random
   * and returns its index. if no unanswered question is found, this
   * will return -1.
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
    const question = this.state.questions[this.getUnansweredQuestionIndex()];
    return (
      <div className={"quiz"}>
        <QuizState total={this.state.total} answered={this.state.answered}/>
        <RCSeparator/>
        <QuizQuestionDisplay
          question={question.question}
          qid={question.qid}
          choices={question.choices}
        />
      </div>
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
    return (
      <div className={"quiz-state"}>
        <div>Progress:</div>
        <QuizProgressBar percentage={this.props.answered / this.props.total}/>
        <div>Answered {this.props.answered} out of {this.props.total}</div>
      </div>);
  }
}

class QuizProgressBar extends React.Component {
  render() {
    return (
      <div className={"quiz-progress-bar"}>
        <span>
          {(this.props.percentage.toFixed(4) * 100)}%
        </span>
      </div>);
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
    return (
      <span className={"quiz-question-display"}>
        <QuizQuestion
          question={this.props.question}
          qid={this.props.qid}
        />
        <span className={"quiz-choices"}>
          {this.props.choices.map(
            (answer) => {
              return (
                <QuizAnswerChoice choice={answer.choice} aid={answer.aid}/>
              );
            }
          )}
        </span>
      </span>
    );
  }
}

class QuizQuestion extends React.Component {
  render() {
    return (
      <span className={"quiz-question"}>
        <QuizQuestionQSymbol/>
        <span>{this.props.question}</span>
      </span>
    );
  }
}

class QuizQuestionQSymbol extends React.Component {
  render() {
    // todo - create this symbol
    return <span className={"quiz-question-q-symbol"}>QSymbol</span>;
  }
}

class QuizAnswerChoice extends React.Component {
  render() {
    return <span className={"quiz-answer-choice"}>{this.props.choice}</span>;
  }
}
