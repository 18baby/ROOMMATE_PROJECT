import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


# 변수별 가중치들 저장된 사전 리턴 함수
def get_info(words, default_w):
    new_ws = {}        # 새로운 가중치들을 저장할 사전
    for word in words:
        if word == 'default':
            new_ws[word] = default_w
            continue
        new_w = default_w.copy()
        new_w[word] += 15    # 개인 맞춤 가중치 제공
        new_ws[word] = new_w
    return new_ws


# 최빈값 보정 함수
def pick_max(o_df, df, col, mask, thres=0.5):
    feature_len = len(df[col].unique())
    max_feature = o_df[col].value_counts().idxmax()  #원본 df의 대푯값
    if mask == 1:
        print(f"{col}의 값 개수: {feature_len}, 전체 데이터 최빈값: {max_feature}")
    if feature_len <= 2:
        max_idx = df[col].value_counts().idxmax()
    else:
        if mask == 1:
            print(df[col].value_counts().iloc[0:3].to_frame('count').reset_index(), col)
        max_three_df = df[col].value_counts().iloc[0:3].to_frame('count').reset_index()
        if max_three_df.iloc[0, 0] == max_feature:
            if max_three_df.iloc[1, 1] > max_three_df.iloc[2, 1]:
                if (abs(max_three_df.iloc[1, 1]-max_three_df.iloc[0, 1])/max_three_df.iloc[0, 1])>thres:  #얼마만큼 차이 허용할지
                    max_idx=max_three_df.iloc[0, 0]
                else:
                    max_idx=max_three_df.iloc[1, 0]
            else:
                if (abs(max_three_df.iloc[2, 1]-max_three_df.iloc[0, 1])/max_three_df.iloc[0, 1])>thres:
                    
                    max_idx=max_three_df.iloc[0, 0]
                else:
                    max_idx=max_three_df.iloc[2, 0]
        else:
            max_idx=max_three_df.iloc[0, 0]
    if mask == 1:
        print(f"확정값 {max_idx}")
    return max_idx


# 그룹의 대표 나이 String 값 추출 함수
def age_generate_string(df):
    count_dict = df['age'].value_counts().to_dict()
    sorted_counts = sorted(count_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)  
    temp_age_encode=[0]*4
    
    for key, value in sorted_counts:   # 인코딩된 나이를 빈도 순서로 나타낸 다음 -> 순서를 정함
        if key<=2:
            temp_age_encode[0]+=value
        elif key>=3 and key<=4:
            temp_age_encode[1]+=value
        elif key>=5 and key<=6:
            temp_age_encode[2]+=value
        elif key>=7:
            temp_age_encode[3]+=value
    
    temp_age_encode=np.argsort(temp_age_encode)[::-1]
    result = '-'.join([str(sub+1) for sub in temp_age_encode])
    return result


# 그룹의 대표 인덱스 위치 찾아내기
def age_get_index_based_on_string(option, generated_string, alp=1):
    string_part = generated_string.split('-')
    idx=0

    if(option!=5):
        idx=string_part.index(str(option))   # 인덱스의 위치가 거리이다.

    return (abs(idx*alp))/3


# ===모델 메인 함수===
# 클러스터링 진행 -> 그룹별 클러스터 결과 리턴
def fit_model(DB_df):
    label_df = DB_df
    print("DB 확인")

    label_df = label_df.astype(object)   # 더미 변수화를 위한 형 변환

    # 이메일 따로 저장
    email = label_df['email']
    label_df = label_df.iloc[:, 1:]

    #print(label_df.columns)

    # 더미변수 생성
    dummy_df = pd.get_dummies(label_df)
    #print(dummy_df.columns)

    # 디폴트 가중치 설정
    default_w = {'sex':50.0, 'age':5.21, 'dorm_select':50.0, 'college_of':1.27, 'personality':4.53, 'weekend_stay':5.76, 
               'weekday_stay':6.76, 'smoke':28.47, 'alchol':5.95, 'm_how_eat':0.79, 'how_eat_in':13.54, 'wake_up':17.98, 'm_sleep':26.32, 
               'sleep_sensitive':12.56, 'sleep_habit':5.03, 'clean_period':29.02, 'shower_timezone':6.15, 'w_age_range':1.0,
               'w_diff_college_of':1.0, 'w_personality':1.0, 'w_weekend_stay':1.0, 'w_weekday_stay':1.0, 'w_smoke':1.0, 'w_alchol':1.0,
               'w_how_eat':1.0, 'w_how_eat_in':1.0, 'w_wake_up':1.0, 'w_sleep':1.0, 'w_sleep_sensitive':1.0, 'w_sleep_habit':1.0, 
               'w_clean_period':1.0, 'w_shower_timezone':1.0}
    keys = list(default_w.keys())

    # 변수 이름들 저장
    col_list = ['email', 'sex', 'age', 'dorm_select', 'college_of', 'personality', 'weekend_stay', 
            'weekday_stay', 'smoke', 'alchol', 'm_how_eat', 'how_eat_in', 'wake_up', 'm_sleep', 
            'sleep_sensitive', 'sleep_habit', 'clean_period', 'shower_timezone', 'w_age_range', 
            'w_diff_college_of', 'w_personality', 'w_weekend_stay', 'w_weekday_stay', 'w_smoke', 
            'w_alchol', 'w_how_eat', 'w_how_eat_in', 'w_wake_up', 'w_sleep', 'w_sleep_sensitive', 
            'w_sleep_habit', 'w_clean_period', 'w_shower_timezone']

    # 모델을 만들 변수들 저장
    words = ['default', 'age', 'college_of', 'personality', 'weekend_stay', 'weekday_stay', 'smoke', 
             'alchol', 'm_how_eat', 'how_eat_in', 'wake_up', 'm_sleep', 'sleep_sensitive', 'sleep_habit',
             'clean_period', 'shower_timezone']

    new_ws = get_info(words, default_w)     # 변수별 가중치 저장 사전

    # 가중치 계산 코드
    dummy_dfs = {}  # 변수별 가중치 적용 데이터프레임들

    for word in words:
        weights = new_ws[word]
        copy_df = dummy_df.copy()
        for i in range(len(keys)):
            copy_df.loc[:, copy_df.columns.str.startswith(keys[i])] = copy_df.loc[:, copy_df.columns.str.startswith(keys[i])]*weights[keys[i]]
        dummy_dfs[word] = copy_df

    clusters = {}   # 변수별 클러스터 결과 저장

    # 변수별로 9개의 클러스터로 클러스터링 진행
    for word in words:
        km = KMeans(n_clusters=9, n_init=10, random_state=1)
        cluster = km.fit_predict(dummy_dfs[word])
        clusters[word] = cluster

    #print(clusters['default'])

    # 라벨링 데이터에 각 변수별 클러스터 결과 열 추가
    for word in words:
        label_df[f'{word}_cluster'] = clusters[word]

    #print(label_df.loc[label_df['default_cluster'] == 6].index)   # 클러스터 결과 확인

    label_df.to_csv('cluster별_라벨링.csv')   # 변수별 클러스터링 결과 저장

    # ==== 클러스터별 대푯값 확인 ====
    cols = list(label_df.columns[0:17])     # 내정보 열 이름들
    print(cols)

    # 변수별 그룹핑
    groups = {}        # 변수별로 그룹핑 결과 객체 저장
    for word in words:
        group = label_df.groupby(f'{word}_cluster')
        groups[word] = group

    group_datas = {}   # 변수별 그룹 대푯값 결과 저장
    # 그룹별 대표값 계산
    for word, word_group in groups.items():
        #print(f'Key: {word}, Value: {word_group}')

        cluster_group = []   # word별로 클러스터별 대표값 저장
        for name, group in word_group:
            if word == 'smoke':
                print("smoke 클러스터")
                print(f"클러스터 번호{name}")       # 클러스터 번호
                mask = 1
            else:
               mask = 0
            group_data = []   # 그룹별 변수의 최빈값 저장

            for col in cols:
                # if word == 'smoke':
                #     print(f"{col} 확인")
                group_data.append(pick_max(label_df, group, col, mask))

            cluster_group.append(group_data)

        groups_df = pd.DataFrame(cluster_group, columns=cols)   # 데이터 프레임 형태 변환
        group_datas[word] = groups_df    # 단어 사전에 그룹별 대표값 저장

    #print(groups['default'].get_group(1))   # default 변수의 1번 그룹 확인
    # for word, dfs in group_datas.items():
    #     print(f"{word} 저장")
    #     print(dfs)
    #     dfs.to_csv(f'cluster_rep/{word}_cluster_representative.csv')   # 대푯값 저장

    return email, groups, group_datas
    # ======= 리턴값 정리 =========
    # groups: 사전 -> key: 변수명, value: 그룹핑된 객체
    # group_datas: 사전 -> key: 변수명, value: 그룹별 대푯값 데이터프레임


# ====== 연습용 DF 불러오기 ========
# DB_df = pd.read_csv('introduce\main_data.csv', encoding='utf-8')
# DB_df = DB_df.iloc[:, 1:]
# print(DB_df.columns)
# print(DB_df.shape)
# fit_model(DB_df)





