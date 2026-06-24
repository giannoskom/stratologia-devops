import base64
import json
import os
import smtplib
from email.mime.text import MIMEText
import psycopg2
import requests
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "super_devops_secret_key_2026"

# --- DEVOPS CONFIGURATION ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stratologia_db")
DB_USER = os.getenv("DB_USER", "stratologia_user")
DB_PASS = os.getenv("DB_PASS", "stratologia_pass")

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")

# --- KEYCLOAK CONFIGURATION ---
KEYCLOAK_CLIENT_ID = "stratologia-app"
KEYCLOAK_CLIENT_SECRET = os.getenv(
    "KEYCLOAK_CLIENT_SECRET", "tWPJ6V3sdVeEOtl24twZ9Im2TW8WhB6a"
)
KEYCLOAK_REALM = "stratologia-realm"

KEYCLOAK_AUTH_URL = os.getenv("KEYCLOAK_AUTH_URL", "http://localhost:8080")
KEYCLOAK_BACKEND_URL = os.getenv("KEYCLOAK_BACKEND_URL", "http://localhost:8080")
OIDC_REDIRECT_URI = f"{APP_BASE_URL}/callback"


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(150) NOT NULL,
            amka VARCHAR(11) NOT NULL,
            request_type VARCHAR(50) NOT NULL,
            army_branch VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()
    print("📦 [DevOps] DB Schema Verified!")


def send_status_email(citizen_name, amka, new_status, branch):
    recipient = f"citizen_{amka}@hua.gr"
    subject = f"ΓΕΕΘΑ: Ενημέρωση Αίτησης (ΑΜΚΑ: {amka})"
    color = "#198754" if new_status == "APPROVED" else "#dc3545"
    status_text = "ΕΓΚΡΙΘΗΚΕ" if new_status == "APPROVED" else "ΑΠΟΡΡΙΦΘΗΚΕ"
    msg_body = (
        f"Η αίτησή σας για <b>{branch}</b> έγινε δεκτή."
        if new_status == "APPROVED"
        else "Η αίτησή σας απορρίφθηκε."
    )

    html_content = f"""
    <div style="font-family: Arial; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
        <h2 style="color: #0d6efd;">🇬🇷 Στρατολογική Υπηρεσία</h2>
        <p>Αξιότιμε/η <b>{citizen_name}</b>,</p>
        <h3 style="background-color: #f8f9fa; padding: 10px; border-left: 5px solid {color};">
            Κατάσταση: <span style="color: {color};">{status_text}</span>
        </h3>
        <p>{msg_body}</p>
    </div>
    """
    msg = MIMEText(html_content, "html")
    msg["Subject"] = subject
    msg["From"] = "noreply@mod.mil.gr"
    msg["To"] = recipient
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        print(f"📧 [MailHog] Sent to: {recipient}")
    except Exception as e:
        print(f"❌ [MailHog Error]: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/citizen", methods=["GET", "POST"])
def citizen():
    success = False
    if request.method == "POST":
        full_name = request.form["full_name"]
        amka = request.form["amka"]
        request_type = request.form["request_type"]
        army_branch = request.form["army_branch"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO applications (full_name, amka, request_type, army_branch) VALUES (%s, %s, %s, %s)",
            (full_name, amka, request_type, army_branch),
        )
        conn.commit()
        cur.close()
        conn.close()
        success = True
    return render_template("citizen.html", success=success)


@app.route("/officer")
def officer():
    if "user" not in session:
        auth_endpoint = (
            f"{KEYCLOAK_AUTH_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
        )
        return redirect(
            f"{auth_endpoint}?client_id={KEYCLOAK_CLIENT_ID}&response_type=code&redirect_uri={OIDC_REDIRECT_URI}"
        )

    if "officer" not in session.get("roles", []):
        return "❌ Πρόσβαση Απορρίφθηκε: Δεν έχετε δικαιώματα Στρατολόγου.", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, full_name, amka, request_type, army_branch, status FROM applications ORDER BY id DESC;"
    )
    apps = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("officer.html", apps=apps, username=session["user"])


# --- 🚀 Η ΝΕΑ ΕΞΥΠΝΗ CALLBACK (Bypasses Keycloak's existential crisis) ---
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Auth Error: Missing code", 400

    # 1. Παίρνουμε το Token (Αυτό δούλευε πάντα!)
    token_endpoint = f"{KEYCLOAK_BACKEND_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    resp = requests.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": OIDC_REDIRECT_URI,
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        },
    )

    if resp.status_code != 200:
        return f"❌ Token Exchange Failed: {resp.text}", 500

    access_token = resp.json().get("access_token")

    # 2. Αποκωδικοποιούμε το payload τοπικά με καθαρή Python
    try:
        # Το JWT είναι πάντα: header . payload . signature
        payload_b64 = access_token.split(".")[1]

        # Προσθέτουμε το απαραίτητο padding για το Base64 της Python
        padded_payload = payload_b64 + "=" * (-len(payload_b64) % 4)
        decoded_json = base64.urlsafe_b64decode(padded_payload).decode("utf-8")
        user_data = json.loads(decoded_json)

        # Αλιεύουμε τα στοιχεία
        session["user"] = user_data.get("preferred_username")
        session["roles"] = user_data.get("realm_access", {}).get("roles", [])

        return redirect("/officer")

    except Exception as e:
        return f"❌ Σφάλμα αποκωδικοποίησης Token: {e}", 500


@app.route("/logout")
def logout():
    session.clear()
    logout_endpoint = f"{KEYCLOAK_AUTH_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
    return redirect(
        f"{logout_endpoint}?client_id={KEYCLOAK_CLIENT_ID}&post_logout_redirect_uri={APP_BASE_URL}/"
    )


@app.route("/officer/decide/<int:app_id>/<action>", methods=["POST"])
def officer_decide(app_id, action):
    if "officer" not in session.get("roles", []):
        return "Unauthorized", 403

    new_status = "APPROVED" if action == "approve" else "REJECTED"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT full_name, amka, army_branch FROM applications WHERE id = %s",
        (app_id,),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE applications SET status = %s WHERE id = %s",
            (new_status, app_id),
        )
        conn.commit()
        send_status_email(row[0], row[1], new_status, row[2])

    cur.close()
    conn.close()
    return redirect("/officer")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)