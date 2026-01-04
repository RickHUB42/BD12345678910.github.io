import sqlite3
from sqlite3 import Error
from datetime import datetime

conn = sqlite3.connect("school.db")

def create_sqlite_tables(db_file):
    """创建SQLite数据库并初始化表结构（包含新增表）"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 已有的表结构保持不变...
        # 学生信息表
        create_student_table = """
        CREATE TABLE IF NOT EXISTS Student_info (
            stuId INTEGER PRIMARY KEY AUTOINCREMENT,
            stuName TEXT NOT NULL,
            stuGNum TEXT UNIQUE,
            stuAge INTEGER CHECK(stuAge > 0),
            stuNationality TEXT,
            stuEmail TEXT,
            stuPhone TEXT,
            stuGender TEXT,
            stuGrade TEXT,
            stuClass TEXT,
            graduation_year INTEGER,
            stuCourse TEXT
        );
        """
        cursor.execute(create_student_table)

        # 班级信息表
        create_class_table = """
        CREATE TABLE IF NOT EXISTS Class_info (
            classId INTEGER PRIMARY KEY AUTOINCREMENT,
            teacherId INTEGER,
            subject TEXT,
            room TEXT,
            grade TEXT,
            type TEXT,
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId)
        );
        """
        cursor.execute(create_class_table)

        # 教师信息表
        create_teacher_table = """
        CREATE TABLE IF NOT EXISTS teacher_info (
            teacherId INTEGER PRIMARY KEY AUTOINCREMENT,
            teacherName TEXT NOT NULL,
            teacherRoom TEXT,
            teacherSubject TEXT,
            teacherHomeroom TEXT
        );
        """
        cursor.execute(create_teacher_table)

        # 学生-班级关联表
        create_student_class_junction = """
        CREATE TABLE IF NOT EXISTS student_class_junction (
            student_id INTEGER,
            class_id INTEGER,
            PRIMARY KEY (student_id, class_id),
            FOREIGN KEY (student_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_student_class_junction)

        # 咨询信息表（已存在，对应Query类）
        create_query_table = """
        CREATE TABLE IF NOT EXISTS query_info (
            queryId INTEGER PRIMARY KEY AUTOINCREMENT,
            stuId INTEGER,
            teacherId INTEGER,
            classId INTEGER,
            question TEXT NOT NULL,
            answer TEXT,
            time TIMESTAMP,
            FOREIGN KEY (stuId) REFERENCES Student_info(stuId),
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId),
            FOREIGN KEY (classId) REFERENCES Class_info(classId)
        );
        """
        cursor.execute(create_query_table)

        # 新增表结构
        # 1. 日历表（Calendar）
        create_calendar_table = """
        CREATE TABLE IF NOT EXISTS Calendar (
            calendarId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            class_id INTEGER,
            created_by INTEGER NOT NULL,
            created_by_type TEXT NOT NULL CHECK(created_by_type IN ('student', 'teacher')),
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_calendar_table)

        # 2. 作业表（Assignment）
        create_assignment_table = """
        CREATE TABLE IF NOT EXISTS Assignment (
            assignmentId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_time TIMESTAMP NOT NULL,
            class_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            total_points REAL CHECK(total_points >= 0),
            type TEXT,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_assignment_table)

        # 3. 公告表（Announcement）
        create_announcement_table = """
        CREATE TABLE IF NOT EXISTS Announcement (
            announcementId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL
        );
        """
        cursor.execute(create_announcement_table)

        # 4. 讨论表（Discussion）
        create_discussion_table = """
        CREATE TABLE IF NOT EXISTS Discussion (
            discussionId INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            initiator_id INTEGER NOT NULL,
            initiator_type TEXT NOT NULL CHECK(initiator_type IN ('student', 'teacher')),
            class_id INTEGER,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parent_id INTEGER,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (parent_id) REFERENCES Discussion(discussionId) ON DELETE CASCADE,
            FOREIGN KEY (initiator_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (initiator_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_discussion_table)

        # 5. 小组表（GroupClass）
        create_group_class_table = """
        CREATE TABLE IF NOT EXISTS GroupClass (
            groupClassId INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            leader_stu_id INTEGER,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE,
            FOREIGN KEY (leader_stu_id) REFERENCES Student_info(stuId) ON DELETE SET NULL
        );
        """
        cursor.execute(create_group_class_table)

        # 6. 仪表盘表（Dashboard）
        create_dashboard_table = """
        CREATE TABLE IF NOT EXISTS Dashboard (
            dashboardId INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('student', 'teacher')),
            layout_settings TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, user_type),
            FOREIGN KEY (user_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_dashboard_table)

        # 7. 成绩表（MyGrades）
        create_my_grades_table = """
        CREATE TABLE IF NOT EXISTS MyGrades (
            gradeId INTEGER PRIMARY KEY AUTOINCREMENT,
            stu_id INTEGER NOT NULL,
            assignment_id INTEGER NOT NULL,
            score REAL,
            comment TEXT,
            graded_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stu_id, assignment_id),
            FOREIGN KEY (stu_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (assignment_id) REFERENCES Assignment(assignmentId) ON DELETE CASCADE,
            CHECK(score IS NULL OR (score >= 0 AND score <= (SELECT total_points FROM Assignment WHERE assignmentId = assignment_id)))
        );
        """
        cursor.execute(create_my_grades_table)

        # 8. 教学材料表（Material）
        create_material_table = """
        CREATE TABLE IF NOT EXISTS Material (
            materialId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            class_id INTEGER,
            teacher_id INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_material_table)

        conn.commit()
        print("表初始化成功！")
    except Error as e:
        print(f"建表出错: {e}")
    return conn

# 原有函数保持不变...
def add_student(stu_name, stu_gnum=None, stu_age=None, stu_nationality=None,
                stu_email=None, stu_phone=None, stu_gender=None, stu_grade=None,
                stu_class=None, graduation_year=None, stu_course=None):
    # 函数实现不变...
    try:
        if not stu_name:
            print("错误：学生姓名不能为空！")
            return None
        if stu_age is not None and stu_age <= 0:
            print("错误：学生年龄必须大于0！")
            return None

        cursor = conn.cursor()
        sql = """INSERT INTO Student_info 
                 (stuName, stuGNum, stuAge, stuNationality, stuEmail, stuPhone, 
                  stuGender, stuGrade, stuClass, graduation_year, stuCourse)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (stu_name, stu_gnum, stu_age, stu_nationality,
                            stu_email, stu_phone, stu_gender, stu_grade,
                            stu_class, graduation_year, stu_course))
        conn.commit()
        stu_id = cursor.lastrowid
        print(f"学生【{stu_name}】录入成功，stuId: {stu_id}")
        return stu_id
    except Error as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"错误：学生G号【{stu_gnum}】已存在！")
        else:
            print(f"录入学生失败: {e}")
        return None

# 新增函数
def add_calendar(title, start_time, end_time, created_by, created_by_type, description=None, class_id=None):
    """添加日历事件"""
    try:
        if not title or not start_time or not end_time:
            print("错误：标题、开始时间和结束时间不能为空！")
            return None
        if created_by_type not in ('student', 'teacher'):
            print("错误：创建者类型必须是'student'或'teacher'")
            return None

        # 验证创建者存在
        cursor = conn.cursor()
        if created_by_type == 'student':
            cursor.execute("SELECT 1 FROM Student_info WHERE stuId = ?", (created_by,))
        else:
            cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (created_by,))
        if not cursor.fetchone():
            print(f"错误：{created_by_type} ID【{created_by}】不存在！")
            return None

        sql = """INSERT INTO Calendar 
                 (title, description, start_time, end_time, class_id, created_by, created_by_type)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (title, description, start_time, end_time, class_id, created_by, created_by_type))
        conn.commit()
        calendar_id = cursor.lastrowid
        print(f"日历事件【{title}】添加成功，calendarId: {calendar_id}")
        return calendar_id
    except Error as e:
        print(f"添加日历失败: {e}")
        return None

def add_assignment(title, due_time, class_id, teacher_id, description=None, total_points=None, type_=None):
    """添加作业"""
    try:
        if not title or not due_time:
            print("错误：作业标题和截止时间不能为空！")
            return None

        # 验证外键存在
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Class_info WHERE classId = ?", (class_id,))
        if not cursor.fetchone():
            print(f"错误：班级ID【{class_id}】不存在！")
            return None
        
        cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
        if not cursor.fetchone():
            print(f"错误：教师ID【{teacher_id}】不存在！")
            return None

        sql = """INSERT INTO Assignment 
                 (title, description, due_time, class_id, teacher_id, total_points, type)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (title, description, due_time, class_id, teacher_id, total_points, type_))
        conn.commit()
        assignment_id = cursor.lastrowid
        print(f"作业【{title}】添加成功，assignmentId: {assignment_id}")
        return assignment_id
    except Error as e:
        print(f"添加作业失败: {e}")
        return None

def add_announcement(title, content, teacher_id, class_id=None):
    """添加公告"""
    try:
        if not title or not content:
            print("错误：公告标题和内容不能为空！")
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
        if not cursor.fetchone():
            print(f"错误：教师ID【{teacher_id}】不存在！")
            return None

        sql = """INSERT INTO Announcement 
                 (title, content, teacher_id, class_id)
                 VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (title, content, teacher_id, class_id))
        conn.commit()
        announcement_id = cursor.lastrowid
        print(f"公告【{title}】发布成功，announcementId: {announcement_id}")
        return announcement_id
    except Error as e:
        print(f"发布公告失败: {e}")
        return None

# 可根据需要继续实现其他类的添加函数（add_discussion、add_group_class等）
#Initialization
create_sqlite_tables('schoolv2.db')