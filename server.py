from flask import Flask, render_template, redirect, url_for, request
from database import run_query

import re
from datetime import datetime

app = Flask(__name__)


@app.get("/")
def index():
    latest = run_query(
        """
    SELECT * FROM question
    ORDER BY submission_time DESC
    LIMIT 5;
    """,
        debug=True,
    )
    return render_template("index.html", questions=latest)


@app.get("/question/<int:id>/")
def get_question(id):
    question = run_query(
        """
    SELECT
        q.id,
        q.title,
        q.message,
        array_agg(a.message) AS answer
    FROM question q
    LEFT JOIN answer a
    ON a.question_id = q.id
    WHERE q.id = %(question_id)s
    GROUP BY q.id;
    """,
        {"question_id": id},
        single=True,
        debug=True,
    )

    question["message"] = re.sub(r"\r*\n", "</p><p>", question["message"])

    return render_template("question.html", question=question)


@app.get("/question/<int:id>/delete/")
def delete_question(id):
    to_delete = run_query(
        """
    DELETE FROM comment
    WHERE question_id = %(question_id)s OR answer_id in (
        SELECT id FROM answer
        WHERE question_id = %(question_id)s
    );

    DELETE FROM question_tag
    WHERE question_id = %(question_id)s;

    DELETE FROM answer
    WHERE question_id = %(question_id)s;

    DELETE FROM question
    WHERE id = %(question_id)s
    RETURNING id;
    """,
        {"question_id": id},
        debug=True,
    )

    print(to_delete)

    return redirect(url_for("index"))


@app.get("/new-question/")
def new_question_form():
    return render_template("questionform.html")


@app.post("/")
def add_question():
    title = request.form.get("title")
    message = request.form.get("message")

    id = run_query(
        """
    INSERT INTO question
    (submission_time, title, message)
    VALUES
    (%(time)s, %(title)s, %(message)s)
    RETURNING id;
    """,
        {
            "time": datetime.now(),
            "title": title,
            "message": message,
        },
        single=True,
        debug=True,
    ).get("id")

    return redirect(url_for("get_question", id=id))


@app.get("/question/<int:id>/edit/")
def edit_question_form(id):
    question = run_query(
        """
    SELECT * FROM question
    WHERE id = %(question_id)s;
    """,
        {"question_id": id},
        single=True,
        debug=True,
    )

    return render_template("editquestionform.html", question=question)


@app.post("/question/<int:id>/edit/")
def edit_question(id):

    run_query(
        """
    UPDATE question
    SET
        title = %(title)s,
        message = %(message)s
    WHERE id = %(id)s
    RETURNING id;
    """,
        {
            "id": id,
            "title": request.form.get("title"),
            "message": request.form.get("message"),
        },
        debug=True,
    )

    return redirect(url_for("get_question", id=id))


if __name__ == "__main__":
    app.run(debug=True)
