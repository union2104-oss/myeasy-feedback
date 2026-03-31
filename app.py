
import sqlite3
from flask import Flask, request, redirect, render_template
from database import init_db, add_feedback, get_all_feedback, delete_feedback

app = Flask(__name__)

# inizializza il database
init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        disciplina = request.form["disciplina"]
        tipo = request.form["tipo"]
        titolo = request.form["titolo"]
        descrizione = request.form["descrizione"]
        priorita = request.form["priorita"]
        fonte = request.form["fonte"]
        stato = request.form["stato"]

        add_feedback(disciplina, tipo, titolo, descrizione, priorita, fonte, stato)
        return redirect("/")

    feedback = get_all_feedback()
    return render_template("index.html", feedback=feedback)

@app.route("/delete/<int:feedback_id>")
def delete(feedback_id):
    delete_feedback(feedback_id)
    return redirect("/")

@app.route("/edit/<int:feedback_id>", methods=["GET", "POST"])
def edit(feedback_id):

    if request.method == "POST":
        disciplina = request.form["disciplina"]
        tipo = request.form["tipo"]
        titolo = request.form["titolo"]
        descrizione = request.form["descrizione"]
        priorita = request.form["priorita"]
        fonte = request.form["fonte"]
        stato = request.form["stato"]

        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE feedback
            SET disciplina=?, tipo=?, titolo=?, descrizione=?, priorita=?, fonte=?, stato=?
            WHERE id=?
        """, (disciplina, tipo, titolo, descrizione, priorita, fonte, stato, feedback_id))

        conn.commit()
        conn.close()

        return redirect("/")

    # GET → carico dati esistenti
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
    feedback = cursor.fetchone()

    conn.close()

    return render_template("edit.html", feedback=feedback)


if __name__ == "__main__":
    app.run(debug=True)