from flask import render_template, request, json
from app import app
import app.db.database as database


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/quiz")
def quiz():
	return render_template("quiz.html")


@app.route("/questions", methods=["GET"])
def questions():
	"""
	fetches all the questions for a quiz
	:return: json of the format
		List[Dict["question": String, "qid": Int, "answers": AnswerList]]
		AnswerList: List[Dict["choice": String, "aid": Int]]
	"""
	json_data = []
	for qid, question, answers in database.load_questions():
		json_data.append({
			"qid": qid,
			"question": question,
			"response_choices": [{
				"choice": choice,
				"aid": aid,
			} for aid, choice, _ in answers]
		})
	return json.dumps(json_data)


@app.errorhandler(404)
def not_found(error):
	print(error)
	return render_template("error.html"), 404
