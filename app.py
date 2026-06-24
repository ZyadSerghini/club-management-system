
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)
import psycopg2
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def get_db_connection():
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    conn.autocommit = True
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pid = request.form['pid']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM SAO_Admin WHERE P_ID = %s AND ADM_PASSWORD = %s', (pid, password))
        admin = cur.fetchone()
        if admin:
            session['user_type'] = 'sao_admin'
            session['p_id'] = pid
            cur.close()
            conn.close()
            return redirect('/dashboard')

        cur.execute('SELECT * FROM SAO_Leader WHERE P_ID = %s AND LDR_PASSWORD = %s', (pid, password))
        leader = cur.fetchone()
        if leader:
            session['user_type'] = 'sao_leader'
            session['p_id'] = pid
            cur.close()
            conn.close()
            return redirect('/dashboard')

        cur.execute('SELECT * FROM Board_Member WHERE P_ID = %s AND BRD_PASSWORD = %s', (pid, password))
        board = cur.fetchone()
        if board:
            session['user_type'] = 'board_member'
            session['p_id'] = pid
            session['club_id'] = board[1]
            cur.close()
            conn.close()
            return redirect('/dashboard')

        cur.close()
        conn.close()
        flash('Invalid credentials', 'error')
        return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_type' not in session:
        return redirect('/login')

    if session['user_type'] == 'sao_admin':
        return render_template('admin_dashboard.html')
    
    elif session['user_type'] == 'sao_leader':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT event_name, event_date, event_venue, event_start_time, event_end_time, event_id
        FROM Event
        WHERE ldr_id = %s
        ORDER BY event_date
        """, (session['p_id'],))
        events = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leader_dashboard.html', events=events)

    
    elif session['user_type'] == 'board_member':
        conn = get_db_connection()
        cur = conn.cursor()

        club_id = session['club_id']

        cur.execute("SELECT club_name FROM Club WHERE club_id = %s", (club_id,))
        club = cur.fetchone()
        club_name = club[0] if club else "Unknown Club"

        cur.execute("""
            SELECT event_name, event_date, event_venue 
            FROM Event 
            WHERE club_id = %s 
            ORDER BY event_date
        """, (club_id,))
        events = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('board_dashboard.html', club_name=club_name, events=events)

    else:
        flash('Unknown role', 'error')
        return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect('/login')

@app.route('/clubs')
def clubs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT club_id, club_name, club_type FROM Club ORDER BY club_id")
    clubs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('clubs.html', clubs=clubs)

@app.route('/events')
def events():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT event_id, event_name, event_date FROM Event ORDER BY event_date")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('events.html', events=events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Event WHERE event_id = %s", (event_id,))
    event = cur.fetchone()
    cur.close()
    conn.close()
    if event is None:
        abort(404)
    return render_template('event_detail.html', event=event)

@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        venue = request.form['venue']
        date = request.form['date']
        start = request.form['start']
        end = request.form['end']
        club_id = request.form['club_id']
        ldr_id = request.form['ldr_id']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Event (club_id, ldr_id, event_name, event_desc, event_venue, event_date, event_start_time, event_end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (club_id, ldr_id, name, desc, venue, date, start, end))
        cur.close()
        conn.close()
        return redirect(url_for('events'))

    return render_template('add_event.html')

@app.route('/attendance/<int:event_id>', methods=['GET', 'POST'])
def add_attendance(event_id):
    if request.method == 'POST':
        std_id = request.form['std_id']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Attendance (std_id, event_id)
            VALUES(%s, %s)
        """, (std_id, event_id))
        cur.close()
        conn.close()

        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT event_name FROM Event WHERE event_id = %s", (event_id,))
    event = cur.fetchone()
    cur.close()
    conn.close()

    event_name = event[0] if event else "Unknown Event"
    return render_template('add_attendance.html', event_name=event_name)

@app.route('/clubs/<int:club_id>')
def club_detail(club_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT C.*, P.P_FNAME, P.P_LASTNAME
    FROM Club C
    JOIN Professor PR ON C.adv_id = PR.P_ID
    JOIN Person P ON PR.P_ID = P.P_ID
    WHERE C.club_id = %s
    """, (club_id,))
    club = cur.fetchone()

    cur.close()
    conn.close()

    if club is None:
        abort(404)
    return render_template('club_detail.html', club=club)

@app.route('/add_club', methods=['GET', 'POST'])
def add_club():
    if 'user_type' not in session or session['user_type'] != 'sao_admin':
        flash('Access denied.')
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        ctype = request.form['type']
        semester = request.form['semester']
        desc = request.form['desc']
        advisor_id = request.form['advisor_id']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Club (club_name, club_type, club_formation_sem, club_desc, adv_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, ctype, semester, desc, advisor_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/clubs')

    return render_template('add_club.html')

@app.route('/edit_club/<int:club_id>', methods=['GET', 'POST'])
def edit_club(club_id):
    if 'user_type' not in session:
        flash('Access denied.')
        return redirect('/login')

    if session['user_type'] == 'board_member' and session['club_id'] != club_id:
        flash("❌ Sorry, you cannot edit info for this club.")
        return redirect(url_for('club_detail', club_id=session['club_id']))

    if session['user_type'] != 'sao_admin' and session['user_type'] != 'board_member':
        flash("Access denied.")
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        ctype = request.form['type']
        semester = request.form['semester']
        desc = request.form['desc']
        advisor_id = request.form['advisor_id']

        cur.execute("""
            UPDATE Club
            SET club_name = %s, club_type = %s, club_formation_sem = %s, club_desc = %s, adv_id = %s
            WHERE club_id = %s
        """, (name, ctype, semester, desc, advisor_id, club_id))
        conn.commit()
        cur.close()
        conn.close()
        if session['user_type'] == 'board_member':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('club_detail', club_id=club_id))

    cur.execute("SELECT * FROM Club WHERE club_id = %s", (club_id,))
    club = cur.fetchone()
    cur.close()
    conn.close()
    if club is None:
        abort(404)
    return render_template('edit_club.html', club=club)




@app.route('/delete_club/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    if 'user_type' not in session or session['user_type'] != 'sao_admin':
        flash('Access denied.')
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Club WHERE club_id = %s", (club_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/clubs')

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if 'user_type' not in session or session['user_type'] != 'board_member':
        flash("Access denied.")
        return redirect('/login')

    club_id = session['club_id']

    if request.method == 'POST':
        std_id = request.form['std_id']
        mbr_status = request.form['mbr_status'] == 'true'
        join_date = request.form['mbr_join_date']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Membership (std_id, club_id, mbr_status, mbr_join_date)
            VALUES (%s, %s, %s, %s)
        """, (std_id, club_id, mbr_status, join_date))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('view_members'))

    return render_template('add_member.html')

@app.route('/members')
def view_members():
    if 'user_type' not in session or session['user_type'] != 'board_member':
        flash("Access denied.")
        return redirect('/login')

    club_id = session['club_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT Membership.std_id, Person.p_fname, Person.p_lastname, mbr_status, mbr_join_date
        FROM Membership 
        JOIN Student ON Membership.std_id = Student.p_id
        JOIN Person ON Person.p_id = Student.p_id
        WHERE club_id = 201
        ORDER BY mbr_join_date DESC
    """, (club_id,))
    members = cur.fetchall()
    cur.execute("""
        SELECT* FROM ActiveMembers;
    """, (club_id,))
    active = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('view_members.html', members=members, active=active)


if __name__ == '__main__':
    app.run(debug=True)

