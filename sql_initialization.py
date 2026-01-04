import sqlite3
from sqlite3 import Error

def create_sqlite_tables(db_file):
    """
    创建SQLite数据库并初始化指定的表结构
    :param db_file: 数据库文件路径（如"school.db"）
    :return: 数据库连接对象，失败则返回None
    """
    conn = None
    try:
        # 1. 连接SQLite数据库（不存在则自动创建）
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        print(f"成功连接到SQLite数据库: {db_file}")

        # 2. 创建Student_info表（学生信息表）
        # 修正字段名空格问题（Graduation Year→graduation_year），统一命名规范
        create_student_table = """
        CREATE TABLE IF NOT EXISTS Student_info (
            stuId INTEGER PRIMARY KEY AUTOINCREMENT,  -- 学生ID，自增主键
            stuName TEXT NOT NULL,                   -- 学生姓名，非空
            stuGNum TEXT UNIQUE,                     -- 学生G号，唯一标识
            stuAge INTEGER CHECK(stuAge > 0),        -- 学生年龄，校验大于0
            stuNationality TEXT,                     -- 国籍
            stuEmail TEXT,                           -- 邮箱
            stuPhone TEXT,                           -- 电话（用TEXT避免数字截断）
            stuGender TEXT,                          -- 性别
            stuGrade TEXT,                           -- 年级（TEXT适配"一年级"/"Grade 1"等格式）
            stuClass TEXT,                           -- 班级
            graduation_year INTEGER,                 -- 毕业年份
            stuCourse TEXT                           -- 修读课程
        );
        """
        cursor.execute(create_student_table)

        # 3. 创建Class_info表（班级信息表）
        create_class_table = """
        CREATE TABLE IF NOT EXISTS Class_info (
            classId INTEGER PRIMARY KEY AUTOINCREMENT,  -- 班级ID，自增主键
            teacherId INTEGER,                          -- 关联教师ID
            subject TEXT,                                -- 科目
            room TEXT,                                   -- 教室
            grade TEXT,                                  -- 年级
            type TEXT,                                   -- 班级类型（如必修/选修）
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId)  -- 外键关联教师表
        );
        """
        cursor.execute(create_class_table)

        # 4. 创建teacher_info表（教师信息表）
        create_teacher_table = """
        CREATE TABLE IF NOT EXISTS teacher_info (
            teacherId INTEGER PRIMARY KEY AUTOINCREMENT,  -- 教师ID，自增主键
            teacherName TEXT NOT NULL,                    -- 教师姓名，非空
            teacherRoom TEXT,                             -- 教师办公室
            teacherNationality TEXT,                        -- 国籍
            teacherEmail TEXT,                            -- 教师邮箱
            teacherSubject TEXT,                          -- 主讲科目
            teacherHomeroom TEXT                          -- 班主任负责班级
        );
        """
        cursor.execute(create_teacher_table)

        # 5. 创建学生-班级关联表（多对多关系）
        create_student_class_junction = """
        CREATE TABLE IF NOT EXISTS student_class_junction (
            student_id INTEGER,
            class_id INTEGER,
            PRIMARY KEY (student_id, class_id),  -- 联合主键，避免重复关联
            FOREIGN KEY (student_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_student_class_junction)

        # 6. 创建query_info表（咨询/问题记录表，修正quiry→query）
        create_query_table = """
        CREATE TABLE IF NOT EXISTS query_info (
            queryId INTEGER PRIMARY KEY AUTOINCREMENT,  -- 问题ID，自增主键
            stuId INTEGER,                               -- 关联学生ID
            teacherId INTEGER,                           -- 关联教师ID
            classId INTEGER,                             -- 关联班级ID
            question TEXT NOT NULL,                      -- 问题内容，非空
            answer TEXT,                                 -- 回答内容
            time TIMESTAMP,                              -- 提问时间（SQLite支持TIMESTAMP）
            FOREIGN KEY (stuId) REFERENCES Student_info(stuId),
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId),
            FOREIGN KEY (classId) REFERENCES Class_info(classId)
        );
        """
        cursor.execute(create_query_table)

        # 提交更改
        conn.commit()
        print("所有表初始化成功！")

    except Error as e:
        print(f"创建表时出错: {e}")
    finally:
        if conn:
            # 可选择不关闭连接，返回供后续操作
            # conn.close()
            pass
    return conn

# ------------------- 执行初始化 -------------------
if __name__ == "__main__":
    # 数据库文件路径（当前目录下的school.db，不存在则自动创建）
    database = "school.db"
    # 初始化表
    db_connection = create_sqlite_tables(database)
    
    # 若需关闭连接，执行以下代码
    # if db_connection:
    #     db_connection.close()
    #     print("数据库连接已关闭")