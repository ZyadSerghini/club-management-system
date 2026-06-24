
-- INSERTS --

-- PERSON
INSERT INTO Person (P_ID, P_FNAME, P_LASTNAME, P_TYPE) VALUES
(1, 'Sara', 'El Amrani', 'S'),
(2, 'Omar', 'Benjelloun', 'S'),
(3, 'Rania', 'Toumi', 'S'),
(4, 'Youssef', 'Kadiri', 'S'),
(5, 'Salma', 'Zerhouni', 'S'),
(6, 'Aya', 'Mouline', 'S'),
(7, 'Khalid', 'Jebari', 'S'),
(100, 'Nadia', 'Ouazzani', 'A'),
(101, 'Anas', 'Fassi', 'A'),
(102, 'Imane', 'Lakhloufi', 'A'),
(10, 'Driss', 'El Idrissi', 'E'),
(11, 'Meryem', 'Kabbaj', 'E'),
(12, 'Karim', 'Bennis', 'E'),
(13, 'Sami', 'Naciri', 'E');

-- EMPLOYEE
INSERT INTO Employee (P_ID, EMP_HIRE_DATE, EMP_IS_ADM, EMP_IS_ADV) VALUES
(10, '2020-01-01', false, true),
(11, '2021-01-01', false, true),
(12, '2019-01-01', false, true),
(13, '2022-09-01', false, true);

-- PROFESSOR
INSERT INTO Professor (P_ID, P_OFFICE, P_PHONE_EXT) VALUES
(10, 'F101', '1001'),
(11, 'F102', '1002'),
(12, 'F103', '1003'),
(13, 'F104', '1004');

-- SAO_Admin
INSERT INTO SAO_Admin (P_ID, ADM_PASSWORD) VALUES
(100, 'nadia123'),
(101, 'anas321'),
(102, 'imane321');

-- SAO_Leader
INSERT INTO SAO_Leader (P_ID, LDR_PASSWORD, ADMIN_ID) VALUES
(1, 'sarapass', 100),
(2, 'omarpass', 101),
(6, 'ayapass', 102);

-- STUDENT
INSERT INTO Student (P_ID, STU_MAJOR, STU_NB_SEMESTERS, STU_IS_LDR, STU_IS_BRD) VALUES
(1, 'CS', 4, true, true),
(2, 'EMS', 5, true, false),
(3, 'BA', 3, false, true),
(4, 'CS', 2, false, false),
(5, 'EMS', 3, false, false),
(6, 'BA', 6, false, true),
(7, 'EMS', 2, false, false);

-- CLUB
INSERT INTO Club (CLUB_ID, ADV_ID, CLUB_NAME, CLUB_TYPE, CLUB_FORMATION_SEM, CLUB_DESC) VALUES
(200, 11, 'Tech Club', 'CS', 'Fall 2023', 'Promotes technical skills and innovation'),
(201, 10, 'Green Energy Society', 'EMS', 'Spring 2023', 'Focuses on sustainability and green energy'),
(202, 12, 'Business Leaders', 'BA', 'Fall 2022', 'Encourages entrepreneurship and leadership in business'),
(203, 13, 'Public Speaking Club', 'BA', 'Spring 2024', 'Improves communication and public speaking skills');

-- BOARD_MEMBER
INSERT INTO Board_Member (P_ID, CLUB_ID, BRD_POSITION, BRD_NB_SEMESTERS, BRD_PASSWORD) VALUES
(1, 200, 'PR', 2, 'pres123'),
(3, 202, 'TR', 1, 'treas123'),
(6, 203, 'VP', 1, 'vp321');

-- MEMBERSHIP
INSERT INTO Membership (STD_ID, CLUB_ID, MBR_STATUS, MBR_JOIN_DATE) VALUES
(1, 200, true, '2023-09-01'),
(2, 200, true, '2023-09-01'),
(3, 202, false, '2022-09-01'),
(4, 201, true, '2023-02-01'),
(5, 201, true, '2023-09-01'),
(6, 203, true, '2024-02-01'),
(7, 203, false, '2024-02-01');

-- EVENT (Only using LDR_ID values: 1, 2, 6)
INSERT INTO Event (EVENT_ID, CLUB_ID, LDR_ID, EVENT_NAME, EVENT_DESC, EVENT_VENUE, EVENT_DATE, EVENT_START_TIME, EVENT_END_TIME) VALUES
(300, 200, 1, 'Hackathon 2025', 'Tech innovation competition', 'Auditorium A', '2025-03-15', '09:00:00', '17:00:00'),
(301, 201, 2, 'Green Talk', 'Seminar on sustainability', 'Green Hall', '2025-04-10', '10:00:00', '12:00:00'),
(302, 202, 1, 'Business Pitch Day', 'Startup pitch event', 'Main Hall', '2025-05-01', '14:00:00', '17:00:00'),
(303, 203, 6, 'Speech Battle', 'Student debate and speech contest', 'Auditorium B', '2025-06-10', '13:00:00', '15:00:00');

-- ATTENDANCE
INSERT INTO Attendance (STD_ID, EVENT_ID) VALUES
(1, 300),
(2, 300),
(3, 302),
(4, 301),
(5, 301),
(6, 303),
(7, 303);
