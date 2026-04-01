
import sqlite3
import cloudinary
import cloudinary.uploader
import os
from flask import Flask, request, redirect, render_template
from database import init_db, add_feedback, get_all_feedback, delete_feedback

app = Flask(__name__)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

#inizializza il database
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

        file = request.files.get("image")

        image_url = None

        if file and file.filename != "":
            result = cloudinary.uploader.upload(file)
            image_url = result["secure_url"]

        add_feedback(
            disciplina,
            tipo,
            titolo,
            descrizione,
            priorita,
            fonte,
            stato,
            image_url
        )

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

        file = request.files.get("image")
        remove_image = request.form.get("remove_image")

        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        #recupero immagine attuale
        cursor.execute("SELECT immagine FROM feedback WHERE id = ?", (feedback_id,))
        current_image = cursor.fetchone()[0]

        image_url = current_image

        #se checkbox selezionata → rimuovi immagine
        if remove_image == "yes":
            image_url = None

        #se carico nuova immagine → override
        elif file and file.filename != "":
            result = cloudinary.uploader.upload(file)
            image_url = result["secure_url"]

        #update completo
        cursor.execute("""
            UPDATE feedback
            SET disciplina=?, tipo=?, titolo=?, descrizione=?, priorita=?, fonte=?, stato=?, immagine=?
            WHERE id=?
        """, (
            disciplina,
            tipo,
            titolo,
            descrizione,
            priorita,
            fonte,
            stato,
            image_url,
            feedback_id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
    feedback = cursor.fetchone()

    conn.close()

    return render_template("edit.html", feedback=feedback)


if __name__ == "__main__":
    app.run(debug=True)