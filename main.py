from flask import Flask, render_template, request, jsonify, session, redirect
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import (
    check_password_hash
)

from config import get_client
from emergency import check_emergency
from bmi import extract_bmi_data, calculate_bmi
from database import get_db, hash_password
from flask_mail import Mail, Message
import random

load_dotenv()

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPPRESS_SEND'] = False

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
mail = Mail(app) 

app.secret_key = os.getenv("SECRET_KEY")

client = get_client()


def save_to_history(user_id, user_msg, bot_msg):
    conn = get_db()
    conn.execute("""
        INSERT INTO chat_history (user_id, user_message, bot_reply, timestamp) 
        VALUES (?, ?, ?, ?)
    """, (user_id, user_msg, bot_msg, datetime.now().isoformat()))
    conn.commit()
    conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user['password'],
            password
        ):

            session['user_id'] = user['id']
            session['email'] = user['email']

            return redirect('/')

        else:

            return (
                "Invalid credentials. "
                "<a href='/login'>Try again</a>"
            )

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():

    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return "Email and password required"

    # CHECK EXISTING USER
    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if existing:
        return "Email already exists"
    # GENERATE OTP
    otp = str(random.randint(100000, 999999))

    # SAVE TEMP DATA
    session['temp_email'] = email
    session['temp_password'] = hash_password(password)
    session['otp'] = otp
    session['otp_expiry'] = (
        
    datetime.now() + timedelta(minutes=5)
    ).isoformat()

    try:

        msg = Message(
            'MediChat OTP Verification',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f'''
━━━━━━━━━━━━━━━━━━━
        MediChat 💙
Your Smart Healthcare Assistant
━━━━━━━━━━━━━━━━━━━

Hello,

Welcome to MediChat 👋

Thank you for creating your account.

To complete your registration,
please verify your email address
using the OTP below:

━━━━━━━━━━━━━━━━━━━

        OTP: {otp}

━━━━━━━━━━━━━━━━━━━

⏳ This OTP is valid for 5 minutes.

🔒 For security reasons:
• Never share this OTP with anyone
• If you did not request this code,
  please ignore this email

After verification, you can:
✔ Chat with AI healthcare assistant
✔ Track your health conversations
✔ Get BMI analysis
✔ Receive basic health guidance
✔ Access your conversation history

Thank you for choosing MediChat 💙

Stay healthy,
MediChat Team
━━━━━━━━━━━━━━━━━━━
'''

        mail.send(msg)

        return redirect('/verify')

    except Exception as e:
        print(e)
        return str(e)

@app.route('/verify', methods=['GET', 'POST'])
def verify():

    if request.method == 'POST':

        user_otp = request.form.get('otp')

        saved_otp = session.get('otp')
        expiry = session.get('otp_expiry')

        # CHECK OTP EXISTS
        if not saved_otp or not expiry:
            return "OTP session expired. Please register again."

        # CHECK TIME
        expiry_time = datetime.fromisoformat(expiry)

        if datetime.now() > expiry_time:

            session.pop('otp', None)
            session.pop('otp_expiry', None)

            return "OTP expired. Please request a new OTP."

        # VERIFY OTP
        if user_otp == saved_otp:

            conn = get_db()

            conn.execute(
                """
                INSERT INTO users
                (email, password, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    session['temp_email'],
                    session['temp_password'],
                    datetime.now().isoformat()
                )
            )

            conn.commit()
            conn.close()

            # CLEAR OTP DATA
            session.pop('otp', None)
            session.pop('otp_expiry', None)
            session.pop('temp_password', None)
            session.pop('temp_email', None)

            return redirect('/login')

        else:

            return "Invalid OTP"

    return render_template('verify.html')

@app.route('/resend_otp')
def resend_otp():

    email = session.get('temp_email')

    if not email:
        return redirect('/login')

    # CREATE NEW OTP
    otp = str(random.randint(100000, 999999))

    # SAVE NEW OTP
    session['otp'] = otp

    # NEW EXPIRY
    session['otp_expiry'] = (
        datetime.now() + timedelta(minutes=5)
    ).isoformat()

    try:

        msg = Message(
            'MediChat OTP Verification',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f'''
━━━━━━━━━━━━━━━━━━━
        MediChat 💙
OTP Verification Request
━━━━━━━━━━━━━━━━━━━

Hello,

You requested a new OTP for your MediChat account.

Your new verification code is:

━━━━━━━━━━━━━━━━━━━

        OTP: {otp}

━━━━━━━━━━━━━━━━━━━

⏳ This OTP will expire in 5 minutes.

🔒 Security Tips:
• Never share this OTP with anyone
• If you did not request this OTP,
  please ignore this email

Please enter this code in the verification page
to continue your registration securely.

Thank you for choosing MediChat 💙

Stay safe and healthy,
MediChat Team
━━━━━━━━━━━━━━━━━━━
'''

        mail.send(msg)

        return "New OTP sent successfully."

    except Exception as e:

        print(e)

        return "Failed to resend OTP"
    
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email')

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if not user:
            return "Email not registered"

        # GENERATE OTP
        otp = str(random.randint(100000, 999999))

        session['reset_email'] = email
        session['reset_otp'] = otp
        session['reset_expiry'] = (
            datetime.now() + timedelta(minutes=5)
        ).isoformat()

        try:

            msg = Message(
                'MediChat Password Reset OTP',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )

            msg.body = f'''
━━━━━━━━━━━━━━━━━━━
MediChat 💙
Password Reset Request
━━━━━━━━━━━━━━━━━━━

Hello,
We received a request to reset your MediChat account password.
Your password reset OTP is:

━━━━━━━━━━━━━━━━━━━

```
    OTP: {otp}
```

━━━━━━━━━━━━━━━━━━━

⏳ This OTP will expire in 5 minutes.

🔒 Security Reminder:
• Never share this OTP with anyone
• MediChat will never ask for your OTP
• If you did not request this reset, please ignore this email

Use this verification code to securely create a new password for your account.

Thank you for using MediChat 💙

Stay safe and healthy,
MediChat Team
━━━━━━━━━━━━━━━━━━━
'''

            mail.send(msg)

            return redirect('/reset_verify')

        except Exception as e:

            print(e)

            return "Failed to send OTP"

    return render_template('forgot_password.html')
    
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'index.html',
        email=session.get('email', '')
    )

@app.route('/reset_verify', methods=['GET', 'POST'])
def reset_verify():

    if request.method == 'POST':

        user_otp = request.form.get('otp')

        saved_otp = session.get('reset_otp')
        expiry = session.get('reset_expiry')

        if not saved_otp or not expiry:
            return "OTP expired"

        expiry_time = datetime.fromisoformat(expiry)

        if datetime.now() > expiry_time:
            return "OTP expired"

        if user_otp == saved_otp:
            return redirect('/new_password')

        else:
            return "Invalid OTP"

    return render_template('reset_verify.html')

@app.route('/new_password', methods=['GET', 'POST'])
def new_password():

    if request.method == 'POST':

        password = request.form.get('password')

        hashed = hash_password(password)

        conn = get_db()

        conn.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (
                hashed,
                session['reset_email']
            )
        )

        conn.commit()
        conn.close()

        # CLEAR RESET SESSION
        session.pop('reset_email', None)
        session.pop('reset_otp', None)
        session.pop('reset_expiry', None)

        return redirect('/login')

    return render_template('new_password.html')


@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"reply": "Please login first"}), 401

    user_input = request.json.get('message', '').strip()
    # Get previous chats for conversation memory
    conn = get_db()

    old_chats = conn.execute("""
    SELECT user_message, bot_reply
    FROM chat_history
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 5
    """, (session['user_id'],)).fetchall()

    conn.close()

    conversation = ""

    for chat in reversed(old_chats):

        conversation += f"""
        User: {chat['user_message']}
        AI: {chat['bot_reply']}
    """
    if not user_input:
        return jsonify({"reply": "Please type something..."})

    # Default reply
    bot_reply = "Sorry, I'm having trouble responding right now."

    
        # BMI Check
    weight, height_cm = extract_bmi_data(user_input)

    if weight is not None and height_cm is not None:

        bmi, category = calculate_bmi(
            weight,
            height_cm
        )

        if bmi:

            advice = (
                "Eat nutritious food..."
                if category == "Underweight"
                else "Maintain healthy lifestyle."
            )

            bot_reply = (
                f"🧮 BMI: {bmi}\n"
                f"Category: {category}\n"
                f"Advice: {advice}"
            )

    elif "kg" in user_input.lower():

        bot_reply = (
            "Please enter valid weight and height.\n\n"
            "Example:\n"
            "70 kg and 170 cm\n"
            "or\n"
            "70 kg and 5.8 feet"
        )

    # Emergency Check
    else:

        emergency_level, _ = check_emergency(user_input)

        if emergency_level == "Critical":

            bot_reply = (
                "🚨 EMERGENCY! "
                "Please go to hospital immediately."
            )

        elif emergency_level == "High Risk":

            bot_reply = (
                "⚠️ High Risk! "
                "Please see a doctor soon."
            )

        else:

            try:

                prompt = f"""
You are MediChat, a friendly AI healthcare assistant.

IMPORTANT RULES:
- Talk naturally like a caring human assistant.
- Avoid repeating the same advice.
- Keep answers short and conversational.
- Use emotional understanding.
- Remember previous conversation context.
- Do not always explain causes unless needed.
- Give practical advice first.
- If symptoms are serious, suggest doctor immediately.
- Never say the exact same sentences repeatedly.
- Use simple English.
- Avoid bullet points unless necessary.
- Sometimes ask follow-up questions.
- Never repeat the same phrases often.
- Avoid long paragraphs.
- Do not use markdown.
- Always try to be helpful and empathetic.
- If you don't know the answer, say "I'm not sure, but I recommend seeing a doctor."
- If the user seems distressed, respond with extra empathy and support.
-do not prescribe any medication,and diagnostic test, just give general advice and suggest doctor if needed.
Previous Conversation:
{conversation}

Current User Message:
{user_input}

Now respond naturally as MediChat.
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"temperature": 0.8}
                )

                if response.text:
                    bot_reply = response.text.strip()
                    import random

                else:
                    bot_reply = "AI response unavailable."

            except Exception as e:

                print("AI ERROR:", e)

                bot_reply = (
                    "Server error. "
                    "Please try again."
                )
    save_to_history(
        session['user_id'],
        user_input,
        bot_reply
    )


    return jsonify({"reply": bot_reply})
    

@app.route('/history', methods=['GET'])
def get_history():

    if 'user_id' not in session:
        return jsonify({"history": []})

    conn = get_db()

    rows = conn.execute("""
        SELECT user_message, bot_reply, timestamp
        FROM chat_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session['user_id'],)).fetchall()

    conn.close()

    history = []

    for row in rows:
        history.append({
            "user": row["user_message"],
            "bot": row["bot_reply"],
            "time": row["timestamp"]
        })

    return jsonify({"history": history})


@app.route('/clear_history', methods=['POST'])
def clear_history():
    if 'user_id' in session:
        conn = get_db()
        conn.execute("DELETE FROM chat_history WHERE user_id = ?", (session['user_id'],))
        conn.commit()
        conn.close()
    return jsonify({"status": "success"})


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin():

    if 'email' not in session:
        return redirect('/login')

    if session['email'] != 'pabitrajana2020@gmail.com':
        return "Access Denied"

    conn = get_db()

    chats = conn.execute("""

        SELECT users.email,
               chat_history.user_message,
               chat_history.bot_reply,
               chat_history.timestamp

        FROM chat_history

        JOIN users
        ON users.id = chat_history.user_id

        ORDER BY users.email,
                 chat_history.timestamp DESC

    """).fetchall()

    conn.close()

    return render_template(
        'admin.html',
        chats=chats
    )
    

if __name__ == '__main__':
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    print("🚀 MediChat Running with Database")
    print("Open: http://127.0.0.1:5000/login")
    app.run(debug=True)

