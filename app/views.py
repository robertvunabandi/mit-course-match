from flask import render_template, request, json, send_from_directory
from app import app
import app.db.database as database
import os


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
			"choices": [{
				"choice": choice,
				"aid": aid,
			} for aid, choice, _ in answers]
		})
	return json.dumps(json_data)


@app.route("/favicon.ico")
def favicon():
	return send_from_directory(
		os.path.join(app.root_path, "static"),
		"favicon.ico",
		mimetype="image/vnd.microsoft.icon"
	)


@app.errorhandler(404)
def not_found(error):
	print(error)
	return render_template("error.html", error=error), 404
