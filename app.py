
import cloudinary
import cloudinary.uploader
import os
from flask import Flask, request, redirect, render_template
from database import init_db, add_feedback, delete_feedback, get_connection, get_images_for_feedback

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
        project = request.form["project"]
        tipo = request.form["tipo"]
        titolo = request.form["titolo"]
        descrizione = request.form["descrizione"]
        priorita = request.form["priorita"]
        fonte = request.form["fonte"]
        stato = request.form["stato"]

        files = request.files.getlist("image")
        print("FILES:", files)

        image_urls = []

        for file in files:
            print("FILES:", files)
            if file and file.filename != "":
                result = cloudinary.uploader.upload(file)
                image_urls.append(result["secure_url"])

        feedback_id = add_feedback(
            project,
            disciplina,
            tipo,
            titolo,
            descrizione,
            priorita,
            fonte,
            stato,
            None
        )

        conn = get_connection()
        cursor = conn.cursor()

        for url in image_urls:
            cursor.execute("""
                INSERT INTO feedback_images (feedback_id, image_url)
                VALUES (%s, %s)
            """, (feedback_id, url))

        conn.commit()
        conn.close()

        return redirect("/")

    tipo = request.args.get("tipo")
    priorita = request.args.get("priorita")
    stato = request.args.get("stato")
    fonte = request.args.get("fonte")

    query = """
    SELECT id, disciplina, tipo, titolo, descrizione, priorita, fonte, stato, image_url
    FROM feedback
    WHERE 1=1
    """

    params = []

    if tipo:
        query += " AND tipo = %s"
        params.append(tipo)

    if priorita:
        query += " AND priorita = %s"
        params.append(priorita)

    if stato:
        query += " AND stato = %s"
        params.append(stato)

    if fonte:
        query += " AND fonte ILIKE %s"
        params.append(f"%{fonte}%")

    query += " ORDER BY id DESC"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    feedback = []

    for f in rows:
        images = get_images_for_feedback(f[0])

        feedback.append({
            "id": f[0],
            "disciplina": f[1],
            "tipo": f[2],
            "titolo": f[3],
            "descrizione": f[4],
            "priorita": f[5],
            "fonte": f[6],
            "stato": f[7],
            "images": images
        })

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

        files = request.files.getlist("image")
        remove_image = request.form.get("remove_image")

        conn = get_connection()
        cursor = conn.cursor()

        #recupero immagine attuale
        cursor.execute("SELECT image_url FROM feedback WHERE id = %s", (feedback_id,))
        current_image = cursor.fetchone()[0]

        image_url = current_image

        #se checkbox selezionata → rimuovi immagine
        if remove_image == "yes":
            image_url = None

        #update completo
        cursor.execute("""
            UPDATE feedback
            SET disciplina=%s, tipo=%s, titolo=%s, descrizione=%s, priorita=%s, fonte=%s, stato=%s, image_url=%s
            WHERE id=%s
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

        images_to_delete = request.form.getlist("delete_images")

        for img_url in images_to_delete:
            cursor.execute("""
                        DELETE FROM feedback_images
                        WHERE feedback_id = %s AND image_url = %s
                    """, (feedback_id, img_url))

        for file in files:
            if file and file.filename != "":
                result = cloudinary.uploader.upload(file)
                new_image_url = result["secure_url"]

                cursor.execute("""
                    INSERT INTO feedback_images (feedback_id, image_url)
                    VALUES (%s, %s)
                """, (feedback_id, new_image_url))

        conn.commit()
        conn.close()

        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE id = %s", (feedback_id,))
    feedback = cursor.fetchone()

    conn.close()

    images = get_images_for_feedback(feedback_id)

    return render_template("edit.html", feedback=feedback, images=images)


if __name__ == "__main__":
    app.run(debug=True)