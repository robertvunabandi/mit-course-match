from flask import render_template, request, json
from app import app


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/quiz")
def quiz():
	return render_template("quiz.html")


def get_questions():
	return [
		{
			"question": "hello there",
			"qid": 35,
			"choices": [
				{"choice": "Lemon", "aid": 46},
				{"choice": "Almond", "aid": 55}
			]
		},
		{
			"question": "okay tell me",
			"qid": 24,
			"choices": [
				{"choice": "No", "aid": 41},
				{"choice": "Yes", "aid": 31}
			]
		}
	]


@app.route("/questions", methods=["GET"])
def questions():
	"""
	fetches all the questions for a quiz
	:return: json of the format
		List[Dict["question": String, "qid": Int, "answers": AnswerList]]
		AnswerList: List[Dict["choice": String, "aid": Int]]
	"""
	# TODO - replace this with the correct method that makes a call to the db
	return json.dumps(get_questions())


@app.errorhandler(404)
def not_found(error):
	print(error)
	return render_template("error.html"), 404
