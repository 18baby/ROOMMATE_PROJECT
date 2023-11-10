import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


# 최빈값 보정 함수
def pick_max(o_df, df, col, thres=0.5):
    feature_len = len(df[col].unique())
    max_feature = o_df[col].value_counts().idxmax()  #원본 df의 대푯값
    ## print(f"{col}의 값 개수: {feature_len}, 전체 데이터 최빈값: {max_feature}")
    if feature_len <= 2:
        max_idx = df[col].value_counts().idxmax()
    else:
        ## print(df[col].value_counts().iloc[0:3].to_frame('count').reset_index(), col)
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
    ## print(f"확정값 {max_idx}")
    return max_idx


# 그룹의 대표 나이 String 값 추출 함수
def age_generate_string(df):
    count_dict = df['age'].value_counts().to_dict()
    sorted_counts = sorted(count_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)
    temp_age_encode = [0] * 4

    for key, value in sorted_counts:  # 인코딩된 나이를 빈도 순서로 나타낸 다음 -> 순서를 정함
        if key <= 2:
            temp_age_encode[0] += value
        elif key >= 3 and key <= 4:
            temp_age_encode[1] += value
        elif key >= 5 and key <= 6:
            temp_age_encode[2] += value
        elif key >= 7:
            temp_age_encode[3] += value

    temp_age_encode = np.argsort(temp_age_encode)[::-1]
    result = '-'.join([str(sub + 1) for sub in temp_age_encode])
    return result


# 그룹의 대표 인덱스 위치 찾아내기
def age_get_index_based_on_string(option, generated_string, alp=1):
    string_part = generated_string.split('-')
    idx = 0

    if (option != 5):
        idx = string_part.index(str(option))  # 인덱스의 위치가 거리이다.

    return (abs(idx * alp)) / 3


# DB_df = pd.read_excel("df.xlsx", engine='openpyxl')
# # print(f" 읽은 데이터 프레임 확인")
# # print(DB_df)


# 단어별 가중치들 저장하는 함수
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


def fit_model(DB_df):
    
    col_list = list(DB_df.columns)
    ## print(col_list)

    label_df = DB_df[col_list]
    label_df = label_df.astype(object)


    # 디폴트 가중치 설정
    default_w = {'sex':50.0, 'age':5.21, 'dorm_select':50.0, 'college_of':1.27, 'personality':4.53, 'weekend_stay':5.76, 
           'weekday_stay':6.76, 'smoke':28.47, 'alchol':5.95, 'm_how_eat':0.79, 'how_eat_in':13.54, 'wake_up':17.98, 'm_sleep':26.32, 
           'sleep_sensitive':12.56, 'sleep_habit':5.03, 'clean_period':29.02, 'shower_timezone':6.15, 'w_age_range':1.0,
           'w_diff_college_of':1.0, 'w_personality':1.0, 'w_weekend_stay':1.0, 'w_weekday_stay':1.0, 'w_smoke':1.0, 'w_alchol':1.0,
           'w_how_eat':1.0, 'w_how_eat_in':1.0, 'w_wake_up':1.0, 'w_sleep':1.0, 'w_sleep_sensitive':1.0, 'w_sleep_habit':1.0, 
           'w_clean_period':1.0, 'w_shower_timezone':1.0}
    keys = list(default_w.keys())
    
    
    # 성별, 거주홀은 제외한 모든 변수들에 대해 가중치 + 15 진행
    words = ['default', 'age', 'college_of', 'personality', 'weekend_stay', 'weekday_stay', 'smoke', 
             'alchol', 'm_how_eat', 'how_eat_in', 'wake_up', 'm_sleep', 'sleep_sensitive', 'sleep_habit',
             'clean_period', 'shower_timezone']

    # 각 중요 변수별 조정된 가중치 값들 저장(사전)
    new_ws = get_info(words, default_w)
    
    # print(label_df)
    # 원핫 인코딩
    dummy_df = pd.get_dummies(label_df)
    # print("원-핫 인코딩 결과")
    # print(dummy_df)

    
   # 가중치 계산 코드
    dummy_dfs = {}    # 단어별 가중치 곱해진 DF

    for word in words:
        weights = new_ws[word]
        copy_df = dummy_df.copy()
        for i in range(len(keys)):
            copy_df.loc[:, copy_df.columns.str.startswith(keys[i])] = copy_df.loc[:, copy_df.columns.str.startswith(keys[i])]*weights[keys[i]]
        dummy_dfs[word] = copy_df

    ## print(len(dummy_dfs))
    
    # 9개의 클러스터로 분류
    clusters = {}

    for word in words:
        km = KMeans(n_clusters=9, n_init=10, random_state=1)
        cluster = km.fit_predict(dummy_dfs[word])
        clusters[word] = cluster

        
    # 라벨링 데이터에 각 변수별 클러스터 결과 열 추가
    for word in words:
        label_df[f'{word}_cluster'] = clusters[word]
    
    
    label_df.to_csv('label_df.csv')   # 클러스터링 결과 저장
    
    
    cols = list(label_df.columns[0:17])
    
    # 그룹별 내정보 저장하기(최대값으로 저장)
    groups = {}        # 단어별로 클러스터링 그룹핑 결과

    for word in words:
        group = label_df.groupby(f'{word}_cluster')
        groups[word] = group
    
    ## print(groups)
    
    group_datas = {}   # 단어별 그룹 결과 저장
    # 그룹별 대표값 계산
    for word, word_group in groups.items():
        # print("시#################작")
        # # print(f'Key: {word}, Value: {word_group}')

        cluster_group = []   # word별로 클러스터별 대표값 저장
        for name, group in word_group:
            ## print(name)       # 클러스터 번호
            group_data = []   # 그룹별 변수의 최빈값 저장

            for col in cols:
                group_data.append(pick_max(label_df, group, col))

            cluster_group.append(group_data)

        # print(cluster_group)   # 단어별 그룹핑 확인용
        groups_df = pd.DataFrame(cluster_group, columns=cols)   # 데이터 프레임 형태 변환

        group_datas[word] = groups_df    # 단어 사전에 그룹별 대표값 저장
        
        
        # 클러스터 대푯값 저장
        for word, df in group_datas.items():
            ## print(word)
            ## print(df)
            copy_df.to_csv(f'introduce\cluster_rep\{word}_cluster_representative.csv')  # 클러스터별 대푯값 저장

    return groups, group_datas

# df_email=origin_df.iloc[:, 1]
# DB_df=origin_df.iloc[:, 2:]
# DB_df = DB_df.iloc[:191, :]
# label_df = pd.read_csv('label_df.csv')
# label_df = label_df.iloc[:191, :]



DB_df = pd.read_csv('main_data.csv',encoding='utf-8')
DB_df = DB_df.iloc[:, 1:]
# print(DB_df)
# print("done..")
group, group_datas=fit_model(DB_df)   # 동작 확인
