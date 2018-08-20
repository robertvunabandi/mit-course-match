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
      questions: props.questions.map(question => question),
      answers: {},
      order: UTIL.shuffleList(UTIL.range(props.questions.length)).concat([-1]),
      orderIndex: 0,
    };
  }

  componentWillMount() {
    window.addEventListener("keydown", this.handleKeyDownEvent.bind(this));
  }

  handleKeyDownEvent(e) {
    const {altKey, code, ctrlKey, key, keyCode, metaKey, shiftKey} = e;
    console.log({altKey, code, ctrlKey, key, keyCode, metaKey, shiftKey});
  }

  getAnsweredQuestionsCount(answers) {
    let count = 0;
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
    let index = UTIL.randomFromList(
      this.state.questions
        .map((question, index) => !this.state.answers[question.qid] ? index : -1)
        .filter((index) => index > -1)
    );
    if (index === undefined) {
      return -1;
    }
    return index;
  }

  setAnswer(qid, aid) {
    const self = this;
    this.setState((prevState, props) => {
      const update = {answers: {}};
      update.answers[qid] = aid;
      // copy over all the answers only from other questions
      for (let qid_ans in prevState.answers) {
        if (
          Object.prototype.hasOwnProperty.call(prevState.answers, qid_ans) &&
          parseInt(qid_ans) !== qid
        ) {
          update.answers[qid_ans] = prevState.answers[qid_ans];
        }
      }
      update.answered = self.getAnsweredQuestionsCount(update.answers);
      return update;
    });
  }

  previousQuestion() {
    this.setState((prevState, props) => {
      if (prevState.orderIndex > 0) {
        return {orderIndex: prevState.orderIndex - 1};
      }
      return {};
    });
  }

  nextQuestion() {
    this.setState((prevState, props) => {
      if (prevState.orderIndex < prevState.total) {
        return {orderIndex: prevState.orderIndex + 1};
      }
      return {};
    });
  }

  render() {
    const index = this.state.order[this.state.orderIndex];
    let quiz_display = null;
    if (index > -1) {
      const question = this.state.questions[index];
      quiz_display = (
        <QuizQuestionDisplay
          question={question.question}
          qid={question.qid}
          choices={question.choices}
          answer={this.state.answers[question.qid]}
          setAnswer={(qid, aid) => this.setAnswer.call(this, qid, aid)}
        />
      );
    } else {
      quiz_display = (
        <QuizQuestionDisplayCompleted
          answered={this.getAnsweredQuestionsCount(this.state.answers)}
          total={this.state.total}
        />
      );
    }
    return (
      <div className={"quiz"}>
        <QuizState total={this.state.total} answered={this.state.answered}/>
        <RCSeparator/>
        {quiz_display}
        <RCPaddedLineSeparator/>
        <QuizQuestionNavigation
          previous={() => this.previousQuestion.call(this)}
          next={() => this.nextQuestion.call(this)}
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
        <QuizProgressBar percentage={this.props.answered / this.props.total}/>
        <div>Answered {this.props.answered} out of {this.props.total}</div>
      </div>
    );
  }
}

class QuizProgressBar extends React.Component {
  render() {
    return (
      <div className={"quiz-progress-bar"}>
        <span style={{width: this.props.percentage.toFixed(4) * 100 + "%"}}>
          {(this.props.percentage.toFixed(4) * 100)}%
        </span>
      </div>
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
                <QuizAnswerChoice
                  choice={answer.choice}
                  aid={answer.aid}
                  chosen={self.props.answer === answer.aid}
                  onClick={() => self.props.setAnswer.call(self, self.props.qid, answer.aid)}
                />
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

function QuizAnswerChoice(props) {
  const chosen_class = props.chosen ? "quiz-answer-choice-chosen" : "";
  return (
    <span
      className={`quiz-answer-choice ${chosen_class}`}
      onClick={props.onClick}><span>{props.choice}</span></span>
  );
}

function QuizQuestionDisplayCompleted(props) {
  let content = props.answered === props.total ?
    `You answered all ${props.total} questions in this quiz!` :
    `You answered ${props.answered} out of ${props.total} questions`;
  return <span className={"quiz-question-display"}>{content}</span>;
}

function QuizQuestionNavigation(props) {
  return (
    <span className={"quiz-navigation"}>
      <QuizButton onClick={props.previous} text={"Previous"}/>
      <QuizButton onClick={props.next} text={"Next"}/>
    </span>
  );
}

function QuizButton(props) {
  return <span className={"quiz-button"} onClick={props.onClick}>{props.text}</span>;
}