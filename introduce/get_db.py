import pymysql
import pandas as pd


def get_db():
    my_db = pymysql.connect(host='localhost', user='root', passwd='root',
                            db='users', charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)

# userDB 이용
    cursor = my_db.cursor()
    cursor.execute('USE users;')

# 전체 데이터 받아옴
    sql = """
        SELECT * FROM usertbl
        """
    cursor.execute(sql)

    result = cursor.fetchall()
    my_db.close()

# 데이터프레임으로 변환
    df = pd.DataFrame(result)
    return (df)


# def convert_kor(df):
#     sex_map = {
#         1: "남자",
#         2: "여자"
#     }
#     dorm_select_map = {
#         1: "레이크홀",
#         2: "비레이크홀"
#     }
#     college_of_map = {
#         1: "문과대",
#         2: "이과대",
#         3: "건축대",
#         4: "공과대",
#         5: "사회과학대",
#         6: "경영대",
#         7: "부동산대",
#         8: "융합과학기술원",
#         9: "생명과학대",
#         10: "수의대",
#         11: "예술디자인대",
#         12: "사범대",
#         13: "기타"
#     }
#     personality_map = {
#         1: "E(외향)",
#         2: "I(내향)"
#     }
#     weekend_stay_map = {
#         1: "주로 기숙사 내",
#         2: "주로 기숙사 밖"
#     }
#     weekday_stay_map = {
#         1: "주로 기숙사 내",
#         2: "주로 기숙사 밖"
#     }
#     smoke_map = {
#         1: "흡연자",
#         2: "비흡연자"
#     }
#     alchol_map = {
#         1: "자주",
#         2: "보통",
#         3: "드물게"
#     }
#     how_eat_map = {
#         1: "기숙사 내",
#         2: "기숙사 밖",
#         3: "기숙사 식당"
#     }
#     how_eat_in_map = {
#         1: "희망",
#         2: "비희망"
#     }
#     wake_up_map = {
#         1: "6시~8시",
#         2: "8시~10시",
#         3: "10시~12시",
#         4: "12시 이후",
#         0: "상관 없음"
#     }
#     sleep_map = {
#         1: "10시~12시",
#         2: "12시~2시",
#         3: "2시 이후",
#         0: "상관 없음"
#     }
#     sleep_sensitive_map = {
#         1: "예민",
#         2: "둔감",
#         0: "상관 없음"
#     }
#     sleep_habit_map = {
#         1: "있다",
#         2: "없다",
#         0: "상관 없음"
#     }
#     clean_period_map = {
#         1: "5회~7회",
#         2: "2회~4회",
#         3: "0회~1회",
#         0: "상관 없음"
#     }
#     shower_timezone_map = {
#         1: "아침",
#         2: "저녁",
#         0: "상관 없음"
#     }
#     df['sex'] = df['sex'].map(sex_map)
#     df['age'] = df['age'].astype(int) + 20
#     df['dorm_select'] = df['dorm_select'].map(dorm_select_map)
#     df['college_of'] = df['college_of'].map(college_of_map)
#     df['personality'] = df['personality'].map(personality_map)
#     df['weekend_stay'] = df['weekend_stay'].map(weekend_stay_map)
#     df['weekday_stay'] = df['weekday_stay'].map(weekday_stay_map)
#     df['smoke'] = df['smoke'].map(smoke_map)
#     df['alchol'] = df['alchol'].map(alchol_map)
#     df['how_eat'] = df['how_eat'].map(how_eat_map)
#     df['how_eat_in'] = df['how_eat_in'].map(how_eat_in_map)
#     df['wake_up'] = df['wake_up'].map(wake_up_map)
#     df['sleep'] = df['sleep'].map(sleep_map)
#     df['sleep_sensitive'] = df['sleep_sensitive'].map(sleep_sensitive_map)
#     df['sleep_habit'] = df['sleep_habit'].map(sleep_habit_map)
#     df['clean_period'] = df['clean_period'].map(clean_period_map)
#     df['shower_timezone'] = df['shower_timezone'].map(shower_timezone_map)
#     result_dict = df.to_dict(orient='records')

#     return(result_dict)


# if __name__ == "__main__":
#     df = get_db()
#     res_dict = convert_kor(df)
#     print(res_dict)
