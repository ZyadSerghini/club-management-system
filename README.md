# Club Management System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Jinja](https://img.shields.io/badge/Jinja2-templates-B41717?logo=jinja&logoColor=white)

🗃️ **This project has been made as an assignment for my Database Systems class.**

A web application for managing university clubs, their members, board, events, and attendance. The goal was to design a normalized relational schema from an EER model and put a working application on top of it.

The interesting part of the project is the data model: it uses a **supertype/subtype (ISA) hierarchy** rooted at `Person`, three role-based login flows, a junction-table design for the many-to-many relationships, plus a view and a trigger function.

## Tech stack

| Layer    | Choice                                 |
| -------- | -------------------------------------- |
| Backend  | Python + Flask                         |
| Database | PostgreSQL (accessed via `psycopg2`)   |
| Frontend | Jinja2 server-rendered templates + CSS |

DB credentials live in [`config.py`](config.py); the schema is in [`init_db.sql`](init_db.sql) and the seed data in [`add_values.sql`](add_values.sql).

## How it works

### Roles and authentication

There is no generic user table — login is checked against three different role tables, each with its own plaintext password column ([`app.py`](app.py) `login()`):

- **SAO Admin** (Student Affairs Office) — creates, edits, and deletes clubs.
- **SAO Leader** — a _student_ who runs events; sees the events they lead and records attendance.
- **Board Member** — a _student_ on a specific club's board; manages that club's members and can edit their own club.

A user submits their `P_ID` + password; the app tries each table in turn and stores the matched role in the Flask session. Routes then gate access on `session['user_type']` (e.g. only an SAO Admin can reach `/add_club`).

### Sample logins (from the seed data)

| Role         | P_ID | Password   |
| ------------ | ---- | ---------- |
| SAO Admin    | 100  | `nadia123` |
| SAO Leader   | 1    | `sarapass` |
| Board Member | 1    | `pres123`  |

## The data model (ISA hierarchy)

`Person` is the supertype holding the shared identity of everyone in the system. Specializations reference `Person.P_ID` as both their primary key **and** a foreign key — the standard relational mapping of an ISA relationship:

```
                         Person  (P_ID, name, type)
            ┌───────────────┼─────────────────────────┐
         Student         Employee                  SAO_Admin
         (major,        (hire date,               (staff, not
       roles flags)     adv/adm flags)             a student)
            │               │
   ┌────────┴──────┐     Professor
SAO_Leader    Board_Member (advises clubs)
(student-led roles, overlapping — a student can be both)
```

`SAO_Admin` is staff (`P_TYPE = 'A'`); `Professor` is an employee (`P_TYPE = 'E'`) who advises clubs; `Student` (`P_TYPE = 'S'`) is the base for the two student roles, which **overlap** — in the seed data person #1 is simultaneously a Student, an SAO Leader, and a Board Member.

The two many-to-many relationships are resolved with junction tables: `Membership` (Student ↔ Club) and `Attendance` (Student ↔ Event).

## Tables

### `Person` — supertype for every individual

| Column       | Type          | Notes                                               |
| ------------ | ------------- | --------------------------------------------------- |
| `P_ID`       | SERIAL **PK** | Surrogate identity for everyone                     |
| `P_FNAME`    | VARCHAR(50)   | First name                                          |
| `P_LASTNAME` | VARCHAR(50)   | Last name                                           |
| `P_TYPE`     | VARCHAR(1)    | Discriminator: `S` student, `E` employee, `A` admin |

### `Employee` — subtype of `Person`

| Column          | Type            | Notes                                |
| --------------- | --------------- | ------------------------------------ |
| `P_ID`          | INT **PK / FK** | → `Person(P_ID)`                     |
| `EMP_HIRE_DATE` | DATE            | Date hired                           |
| `EMP_IS_ADM`    | BOOLEAN         | Flags an administrative employee     |
| `EMP_IS_ADV`    | BOOLEAN         | Flags an employee who advises a club |

### `Professor` — subtype of `Person` (the club advisors)

| Column        | Type            | Notes            |
| ------------- | --------------- | ---------------- |
| `P_ID`        | INT **PK / FK** | → `Person(P_ID)` |
| `P_OFFICE`    | VARCHAR(10)     | Office number    |
| `P_PHONE_EXT` | VARCHAR(10)     | Phone extension  |

### `SAO_Admin` — Student Affairs Office administrators

| Column         | Type            | Notes                      |
| -------------- | --------------- | -------------------------- |
| `P_ID`         | INT **PK / FK** | → `Person(P_ID)`           |
| `ADM_PASSWORD` | VARCHAR(16)     | Login password (plaintext) |

### `SAO_Leader` — student event leaders

| Column         | Type            | Notes                                      |
| -------------- | --------------- | ------------------------------------------ |
| `P_ID`         | INT **PK / FK** | → `Person(P_ID)`                           |
| `LDR_PASSWORD` | VARCHAR(16)     | Login password                             |
| `ADMIN_ID`     | INT **FK**      | → `SAO_Admin(P_ID)`; the supervising admin |

### `Student` — student details and role flags

| Column             | Type            | Notes                  |
| ------------------ | --------------- | ---------------------- |
| `P_ID`             | INT **PK / FK** | → `Person(P_ID)`       |
| `STU_MAJOR`        | VARCHAR(50)     | Major (CS, EMS, BA, …) |
| `STU_NB_SEMESTERS` | INT             | Semesters enrolled     |
| `STU_IS_LDR`       | BOOLEAN         | Is also an SAO Leader  |
| `STU_IS_BRD`       | BOOLEAN         | Is also a Board Member |

### `Club`

| Column               | Type          | Notes                                |
| -------------------- | ------------- | ------------------------------------ |
| `CLUB_ID`            | SERIAL **PK** | Surrogate key                        |
| `ADV_ID`             | INT **FK**    | → `Professor(P_ID)`; faculty advisor |
| `CLUB_NAME`          | TEXT          | Club name                            |
| `CLUB_TYPE`          | TEXT          | Category (CS, EMS, BA, …)            |
| `CLUB_FORMATION_SEM` | TEXT          | Semester founded                     |
| `CLUB_DESC`          | TEXT          | Description                          |

### `Board_Member` — students serving on a club board

| Column             | Type            | Notes                                           |
| ------------------ | --------------- | ----------------------------------------------- |
| `P_ID`             | INT **PK / FK** | → `Person(P_ID)`                                |
| `CLUB_ID`          | INT **FK**      | → `Club(CLUB_ID)`; the club served              |
| `BRD_POSITION`     | VARCHAR(2)      | Role code: `PR` president, `VP`, `TR` treasurer |
| `BRD_NB_SEMESTERS` | INT             | Semesters on the board                          |
| `BRD_PASSWORD`     | VARCHAR(16)     | Login password                                  |

### `Event`

| Column             | Type          | Notes                              |
| ------------------ | ------------- | ---------------------------------- |
| `EVENT_ID`         | SERIAL **PK** | Surrogate key                      |
| `CLUB_ID`          | INT **FK**    | → `Club(CLUB_ID)`; hosting club    |
| `LDR_ID`           | INT **FK**    | → `SAO_Leader(P_ID)`; event leader |
| `EVENT_NAME`       | TEXT          | Title                              |
| `EVENT_DESC`       | TEXT          | Description                        |
| `EVENT_VENUE`      | TEXT          | Location                           |
| `EVENT_DATE`       | DATE          | Date                               |
| `EVENT_START_TIME` | TIME          | Start time                         |
| `EVENT_END_TIME`   | TIME          | End time                           |

### `Membership` — junction: which students belong to which clubs

| Column          | Type       | Notes                         |
| --------------- | ---------- | ----------------------------- |
| `STD_ID`        | INT **FK** | → `Student(P_ID)`             |
| `CLUB_ID`       | INT **FK** | → `Club(CLUB_ID)`             |
| `MBR_STATUS`    | BOOLEAN    | `true` = active member        |
| `MBR_JOIN_DATE` | DATE       | When they joined              |
| —               | **PK**     | Composite `(STD_ID, CLUB_ID)` |

### `Attendance` — junction: which students attended which events

| Column     | Type       | Notes                          |
| ---------- | ---------- | ------------------------------ |
| `STD_ID`   | INT **FK** | → `Student(P_ID)`              |
| `EVENT_ID` | INT **FK** | → `Event(EVENT_ID)`            |
| —          | **PK**     | Composite `(STD_ID, EVENT_ID)` |

### View and trigger function

- **`ActiveMembers`** — a view selecting every `Membership` row where `MBR_STATUS = true`; used by the board member's member list.
- **`update_member_status()`** — a PL/pgSQL function meant to flip a student's membership to active once they have attended ≥ 2 distinct events. _Note: it is defined but not bound to a `CREATE TRIGGER`, and it references a `Member` table that does not exist — so it does not currently run._

## Running it

Requires Python 3.12 and a local PostgreSQL server.

```bash
# 1. dependencies (uv)
uv python pin 3.12
uv sync

# 2. database
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'serghiniz';"
sudo -u postgres createdb ClubManagementSystem
sudo -u postgres psql -d ClubManagementSystem -f init_db.sql
sudo -u postgres psql -d ClubManagementSystem -f add_values.sql

# 3. run
uv run app.py          # http://localhost:5000
```
