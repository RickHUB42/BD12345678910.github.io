import sqlite3
from sqlite3 import Error
from datetime import datetime

conn = sqlite3.connect("school.db")

def create_sqlite_tables(db_file):
    """创建SQLite数据库并初始化表结构（复用之前的函数）"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

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

        # 咨询信息表
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

        conn.commit()
        print("表初始化成功！")
    except Error as e:
        print(f"建表出错: {e}")
    return conn

def add_student(stu_name, stu_gnum=None, stu_age=None, stu_nationality=None,
                stu_email=None, stu_phone=None, stu_gender=None, stu_grade=None,
                stu_class=None, graduation_year=None, stu_course=None):
    """
    录入学生信息
    :param conn: 数据库连接对象
    :param stu_name: 学生姓名（必填）
    :param stu_gnum: 学生G号（唯一）
    :param stu_age: 学生年龄（需>0）
    :param stu_nationality: 国籍
    :param stu_email: 邮箱
    :param stu_phone: 电话
    :param stu_gender: 性别
    :param stu_grade: 年级
    :param stu_class: 班级
    :param graduation_year: 毕业年份
    :param stu_course: 修读课程
    :return: 新增学生的stuId（成功）/None（失败）
    """
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

def add_teacher(teacher_name, teacher_room=None, teacher_nationality=None, teacher_email=None, teacher_subject=None, teacher_homeroom=None):
    """
    录入教师信息
    :param conn: 数据库连接对象
    :param teacher_name: 教师姓名（必填）
    :param teacher_room: 教师办公室
    :param teacher_nationality: 教师国籍
    :param teacher_email: 教师邮箱
    :param teacher_subject: 主讲科目
    :param teacher_homeroom: 班主任负责班级
    :return: 新增教师的teacherId（成功）/None（失败）
    """
    try:
        if not teacher_name:
            print("错误：教师姓名不能为空！")
            return None

        cursor = conn.cursor()
        sql = """INSERT INTO teacher_info 
                 (teacherName, teacherRoom, teacherNationality, teacherEmail, teacherSubject, teacherHomeroom)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (teacher_name, teacher_room, teacher_nationality, teacher_email, teacher_subject, teacher_homeroom))
        conn.commit()
        teacher_id = cursor.lastrowid
        print(f"教师【{teacher_name}】录入成功，teacherId: {teacher_id}")
        return teacher_id
    except Error as e:
        print(f"录入教师失败: {e}")
        return None

def add_class(teacher_id, subject=None, room=None, grade=None, type_=None):
    """
    录入班级/课程信息
    :param conn: 数据库连接对象
    :param teacher_id: 授课教师ID（关联teacher_info）
    :param subject: 科目
    :param room: 教室
    :param grade: 年级
    :param type_: 班级类型（如必修/选修，避免和关键字type冲突）
    :return: 新增班级的classId（成功）/None（失败）
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
        if not cursor.fetchone():
            print(f"错误：教师ID【{teacher_id}】不存在！")
            return None

        sql = """INSERT INTO Class_info 
                 (teacherId, subject, room, grade, type)
                 VALUES (?, ?, ?, ?, ?)"""
        cursor.execute(sql, (teacher_id, subject, room, grade, type_))
        conn.commit()
        class_id = cursor.lastrowid
        print(f"班级【{subject}】录入成功，classId: {class_id}")
        return class_id
    except Error as e:
        print(f"录入班级失败: {e}")
        return None

def add_student_to_class(student_id, class_id):
    """
    关联学生和班级（一个学生可关联多个班级，一个班级可包含多个学生）
    :param conn: 数据库连接对象
    :param student_id: 学生ID
    :param class_id: 班级ID
    :return: True（成功）/False（失败）
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Student_info WHERE stuId = ?", (student_id,))
        if not cursor.fetchone():
            print(f"错误：学生ID【{student_id}】不存在！")
            return False
        
        cursor.execute("SELECT 1 FROM Class_info WHERE classId = ?", (class_id,))
        if not cursor.fetchone():
            print(f"错误：班级ID【{class_id}】不存在！")
            return False

        sql = """INSERT INTO student_class_junction (student_id, class_id) VALUES (?, ?)"""
        cursor.execute(sql, (student_id, class_id))
        conn.commit()
        print(f"学生ID【{student_id}】成功关联班级ID【{class_id}】")
        return True
    except Error as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"错误：学生ID【{student_id}】已关联班级ID【{class_id}】！")
        else:
            print(f"关联学生-班级失败: {e}")
        return False

def add_query(stu_id, teacher_id, class_id, question, answer=None, time_=None):
    """
    录入学生的咨询/问题记录
    :param conn: 数据库连接对象
    :param stu_id: 学生ID
    :param teacher_id: 教师ID
    :param class_id: 班级ID
    :param question: 问题内容（必填）
    :param answer: 回答内容（可选）
    :param time_: 提问时间（默认当前时间，格式：YYYY-MM-DD HH:MM:SS）
    :return: 新增查询的queryId（成功）/None（失败）
    """
    try:
        if not question:
            print("错误：问题内容不能为空！")
            return None
        
        if time_ is None:
            time_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.cursor()
        sql = """INSERT INTO query_info 
                 (stuId, teacherId, classId, question, answer, time)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (stu_id, teacher_id, class_id, question, answer, time_))
        conn.commit()
        query_id = cursor.lastrowid
        return query_id
    except Error as e:
        return None
    
# 初始化数据库表
create_sqlite_tables("school.db")