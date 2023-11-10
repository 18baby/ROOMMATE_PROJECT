import pandas as pd
from sqlalchemy import create_engine

# CSV 파일을 데이터프레임으로 읽기
csv_file = "main_data.csv"
dataframe = pd.read_csv(csv_file, encoding='utf-8')

# MySQL 데이터베이스 연결 설정
db_username = "root"
db_password = "os2window"
db_host = "localhost"  # MySQL 서버 호스트
db_name = "users"

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}")
# engine = create_engine(f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}?schema=None")


# 데이터프레임을 MySQL 테이블로 저장
table_name = "usertbl"
dataframe.to_sql(table_name, con=engine, if_exists="replace", index=False)

# 연결 종료
engine.dispose()
