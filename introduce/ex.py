import pandas as pd

# label_df = pd.read_csv('label_df.csv')

# #print(label_df.columns)

# #print(label_df.loc[label_df['smoke_cluster']==6, ['smoke', 'alchol', 'clean_period']])
# #print(label_df.loc[label_df['alchol_cluster']==2, ['smoke', 'alchol', 'clean_period']])
# #print(label_df.loc[label_df['clean_period_cluster']==4, ['smoke', 'alchol', 'clean_period']])

# DB_df = pd.read_csv('introduce\main_data.csv', encoding='cp949')
# print(DB_df)



# label_df = pd.read_csv('label_df.csv',encoding='utf-8')
# label_df = label_df.iloc[: , 1:]
# print(label_df)

DB_df = pd.read_csv('introduce\main_data.csv', encoding='utf-8')
DB_df = DB_df.iloc[:, 1:]
print(DB_df)


# # ===== 새로운 사용자 정보 입력 가정 ======
# new_df = {'email': 'lhj5561@naver.com', 'sex': 1, 'age': 7, 'dorm_select': 1, 'college_of': 8, 'personality': 1, 'weekend_stay': 2,
#  'weekday_stay': 1, 'smoke': 1, 'alchol': 1, 'm_how_eat': 3, 'how_eat_in': 2, 'wake_up': 1, 'm_sleep': 3, 'sleep_sensitive': 2,
#  'sleep_habit': 3, 'clean_period': 2, 'shower_timezone': 1, 'w_age_range': 3, 'w_diff_college_of': 1, 'w_personality': 0,
#  'w_weekend_stay': 2, 'w_weekday_stay': 2, 'w_smoke': 1, 'w_alchol': 1, 'w_how_eat': 3, 'w_how_eat_in': 3, 'w_wake_up': 0,
#  'w_sleep': 3, 'w_sleep_sensitive': 1, 'w_sleep_habit': 1, 'w_clean_period': 3, 'w_shower_timezone': 1}
# #add_info = ['alchol', 'smoke', 'clean_period']    # 사전을 통해 나온 결과 단어들 저장 (가정하에)
# add_info = ['alchol'] 
# email = new_df['email']  # 이메일 값 따로 저장
# del new_df['email']      # 이메일 제거

# # 연습용 DF 불러오기
# DB_df = pd.read_csv('introduce\main_data.csv', encoding='utf-8')
# print(DB_df['shower_timezone'])

# # 모델 실행
# print('model 실행 시작')
# email, groups, group_datas = h_model.fit_model(DB_df)
# print('model 실행 완료')
# model_predict(new_df, groups, add_info, group_datas, email, DB_df)
