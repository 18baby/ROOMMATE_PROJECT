from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
import model
import copy

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
    try:
        string_part = generated_string.split('-')
        idx=0

        if(option!=5):
            idx=string_part.index(str(option))   # 인덱스의 위치가 거리이다.
    except:
        print(option, generated_string, alp)
    return (abs(idx*alp))/3

# 기존 group에서 단과대의 수가 많은 순으로 정렬한 결과를 문자열로 바꿔주는 함수 "12-1-3..."
def college_generate_string(df):
    count_dict = df['college_of'].value_counts().to_dict()
    sorted_counts = sorted(count_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)  

    result = '-'.join([str(key) for key, _ in sorted_counts])
    return result

# 사용자로부터 입력받은 단과대와 같은 단과대 희망 여부를 문자열로 바꿔주는 함수 "3-2"
def college_convert_to_string(df):
    strings = []
    college_of = str(df['college_of'])
    w_diff_college_of = str(df['w_diff_college_of'])
    strings.append(f"{college_of}-{w_diff_college_of}")
    result = '-'.join(strings)
    return result

def college_get_index_based_on_string(converted_string, generated_string,alp=1):
    string_part = generated_string.split('-')
    conv_string_part=converted_string.split('-')
    idx=0
    div_by=13
    if(conv_string_part[1]=='3'):
        return (0*alp)/div_by

    try:
        idx=string_part.index(conv_string_part[0])
    except:
        if(conv_string_part[1]=='1'):
            return (13*alp)/div_by
        else:
            return (0*alp)/div_by

    if(conv_string_part[1]=='1'):
        return (idx*alp)/div_by
    else:
        return ((13-idx)*alp)/div_by

# 사용자 정보와 유사한 클러스터들 추출
def cal_dis(word, my_info, want_info, group_datas, groups, unique_data, new_df):
    # 9개의 클러스터와 나의 거리 저장
    distance = [100]*9

    for i, row in group_datas[word].iterrows():
        row = list(row)
        print(i, group_datas[word].columns) 
        # 성별이나 거주 홀이 다른 경우 패스
        if (row[0] != new_df['sex']) or (row[2] != new_df['dorm_select']):
            #print('나이, 거주홀 통과')
            continue

        # 성별, 거주홀이 같은 경우
        distance[i] = 0
        k = 2    # 나이, 단과대는 따로 계산
        d = 0    # 거리 누적값
        for j in range(len(row)):
            print(j, row)
            if j < 4:
                #print(f"{my_info[j]} 생략")    # 추후에 결정
                # <====준모, 태윤 코드 대입!!====>
                # (j == 1(나이)) , (j == 2(단과대)) 일때 코드만 처리하면 됨!!
                if(j==1):
                    age_result_string = age_generate_string(groups[word].get_group(i))  
                    age_distance=age_get_index_based_on_string(new_df['w_age_range'], age_result_string)
                    distance[i] += age_distance 
                elif(j==2):
                    college_result_string = college_generate_string(groups[word].get_group(i))
                    college_convert_string=college_convert_to_string(new_df)
                    college_distance=college_get_index_based_on_string(college_convert_string, college_result_string)
                    distance[i] += college_distance
                continue

            # 원하는 상대방 정보 상관없음 일때
            if new_df[want_info[k]] == 0:
                #print(f"{want_info[k]} 상관 없음")
                k += 1
                continue
            # 거리 계산 (절대값)
            d = abs((row[j] - new_df[want_info[k]])/unique_data[j])
            #print(f"{row[j]} - {new_df[want_info[k]]} 의 제곱: {d}")
            distance[i] += d  # 최종 업데이트
            k += 1

        #print()

    #print()
    print(distance)  
    
    return(np.argmin(distance))    # 자신과 가장 가까운 그룹 리턴

# 인덱싱 거리계산
def get_distnace_df(sub_df, new_info):

    #my_info=sub_df.columns[0:15]   #column name
    want_info=sub_df.columns[15:30]    #column name(w_)
    #new_info=new_info[my_info]    #추가된 코드
    #print(my_info, want_info)
    
    # 인덱싱 진행
    distance=[]
    
    for index, row in sub_df.iterrows():
        sub_distance=0
        
        # 인덱스와 행 데이터 출력
        #print(f"{index}번 학생 ")

        want = row[want_info]  # 원하는 상대방 정보
        coll = row['college_of']  # 현재 확인 데이터의 단과대
        # print(want)

        # 따로 처리할 정보
        w_age = want['w_age_range']
        w_diff_col = want["w_diff_college_of"]
        my_sleep_habit = new_info["sleep_habit"]
        
        # 나이 처리
        sub_distance += filter_age(new_info['age'], row)

        # 단과대 처리
        if w_diff_col == 1:  # 같은 단과대 희망하는 경우
            if coll != new_info['college_of']:
                sub_distance += 1
        elif w_diff_col == 2:  # 다른 단과대 희망하는 경우
            if coll == new_info['college_of']:
                sub_distance += 1

        # 나머지 데이터
        want = want.drop(['w_age_range', "w_diff_college_of"])
        for i, data in enumerate(want): 
            if data == 0:  # 상관없음인 경우 패스
                continue
            elif data != new_info[i]:  # 다른 값이면 거리 추가
                sub_distance += 1
                
        #잠버릇 처리(모름 경우)
        if new_info["sleep_habit"]==2:
            sub_distance -= 1
            
        distance.append(sub_distance)
    return distance 

def filter_age(my_age, row):
    if my_age<=1:
        my_age_encode=1
    elif my_age>=2 and my_age<=3:
        my_age_encode=2
    elif my_age>=4 and my_age<=5:
        my_age_encode=3
    elif my_age>=6:
        my_age_encode=4

    distance=0
    if ((row['w_age_range']==my_age_encode) | (row['w_age_range']==5)) == False:
        distance=1
    else:
        distance=0
        
    return distance

# 특성별로 선택된 클러스터들을 list로 전달받고, 최종 후보 4인을 리스트 형태로 반환
def select_candidate(df_list, new_info, penalty=0.2):
    
    for sub_df in df_list:
        sub_df['idx'] = sub_df.index
        #print(sub_df.index)
        sub_df['distance']=get_distnace_df(sub_df, new_info)
            
    res = pd.concat(df_list, ignore_index=True)

    # idx 열을 기준으로 그룹화하고 count 열을 추가하여 등장 횟수를 계산
    res['count'] = res.groupby('idx')['idx'].transform('count')
    res = res.drop_duplicates(subset=['idx'])

    # penalty로 보정된 거리 계산, 후보 4인을 리스트로 생성
    res['distance_fixed'] = res['distance'] + (res['count'] * penalty)
    res = res.sort_values(by='distance_fixed', ascending=False)

    #display(res)
    candidates = res.iloc[0:4, -4].tolist()
    return candidates


# 클러스터 예측
def model_predict(merge_dict, groups, add_info, group_datas, df_email, label_df, DB_df):

    new_df = copy.deepcopy(merge_dict)       # 입력받은 사용자 정보
    email = new_df['email']  # 이메일 값 따로 저장
    del new_df['email']      # 이메일 제거
    
    col_list = ['sex', 'age', 'dorm_select', 'college_of', 'personality', 'weekend_stay', 'weekday_stay', 'smoke', 'alchol',
            'm_how_eat', 'how_eat_in', 'wake_up', 'm_sleep', 'sleep_sensitive', 'sleep_habit', 'clean_period', 'shower_timezone',
            'w_age_range', 'w_diff_college_of', 'w_personality', 'w_weekend_stay', 'w_weekday_stay', 'w_smoke', 'w_alchol',
            'w_how_eat', 'w_how_eat_in', 'w_wake_up', 'w_sleep', 'w_sleep_sensitive', 'w_sleep_habit', 'w_clean_period', 'w_shower_timezone']
    
    want_info = col_list[17:]  # 원하는 상대방 정보 열 이름들
    my_info = col_list[:17]    # 내정보 열 이름들 -> [sex, dorm_select]
    print(want_info)
    print(my_info)

    # 내정보 변수별 가능한 값들
    unique_data = []
    for name in my_info:
        unique_data.append(len(label_df[name].value_counts()))
    print("의심점1", unique_data)
    
    t_distance = {}   # 선택된 단어별 클러스터 저장
    # 추가 정보 없는 경우 -> 디폴트 가중치 적용
    if not add_info:
        t_distance['default'] = cal_dis('default', my_info, want_info, group_datas, groups, unique_data, new_df)

    else:    # 추가 정보 있는 경우
        for i, word in enumerate(add_info):
            # 확인용
            #print(i, word)
            #display(group_datas[word])
            t_distance[word] = cal_dis(word, my_info, want_info, group_datas, groups, unique_data, new_df)
    
    print(t_distance)
    
    # 선택된 그룹의 데이터 프레임 저장
    s_groups = [] 

    # 선택된 그룹들 저장
    for key, value in t_distance.items():
        s_groups.append(groups[key].get_group(value))

    #print(s_groups)    # 여기서 교집합 메소드 넣어서 해결하면 될듯
    

    # 새로운 사용자 정보 변환(성별, 거주홀은 걸러냈으므로 제거)
    new_info = pd.Series(new_df)
    new_info = new_info[my_info]
    new_info = new_info.drop(['sex', 'dorm_select'])
    
    final = select_candidate(s_groups, new_info)
    print(final)
    
    result = DB_df.iloc[final, :17]
    result['email'] = df_email[final]    # 이메일 결합
    
    # 최종 결과 (4인)
    list_user_data=convert_kor(result)
# 최종 결과 출력
    print(list_user_data)
    session['user_data_dict'] =list_user_data
    #return redirect(url_for('result'), code=307)

######################################################################################### 

def convert_kor(df):
    sex_map = {
        1: "남자",
        2: "여자"
    }
    dorm_select_map = {
        1: "레이크홀",
        2: "비레이크홀"
    }
    college_of_map = {
        1: "문과대",
        2: "이과대",
        3: "건축대",
        4: "공과대",
        5: "사회과학대",
        6: "경영대",
        7: "부동산대",
        8: "융합과학기술원",
        9: "생명과학대",
        10: "수의대",
        11: "예술디자인대",
        12: "사범대",
        13: "기타"
    }
    personality_map = {
        1: "E(외향)",
        2: "I(내향)"
    }
    weekend_stay_map = {
        1: "주로 기숙사 내",
        2: "주로 기숙사 밖"
    }
    weekday_stay_map = {
        1: "주로 기숙사 내",
        2: "주로 기숙사 밖"
    }
    smoke_map = {
        1: "비흡연자",
        2: "흡연자"
    }
    alchol_map = {
        1: "드물게",
        2: "보통",
        3: "자주"
    }
    how_eat_map = {
        1: "기숙사 내",
        2: "기숙사 밖",
        3: "기숙사 식당"
    }
    how_eat_in_map = {
        1: "비희망",
        2: "희망"
    }
    wake_up_map = {
        1: "6시~8시",
        2: "8시~10시",
        3: "10시~12시",
        4: "12시 이후"
    }
    sleep_map = {
        1: "10시~12시",
        2: "12시~2시",
        3: "2시 이후"
    }
    sleep_sensitive_map = {
        1: "둔감",
        2: "예민"
    }
    sleep_habit_map = {
        1: "없다",
        2: "있다",
        3: "잘 모르겠다"
    }
    clean_period_map = {
        1: "0회~1회",
        2: "2회~4회",
        3: "5회~7회"
    }
    shower_timezone_map = {
        1: "아침",
        2: "저녁"
    }
    df['sex'] = df['sex'].map(sex_map)
    df['age'] = df['age'].astype(int) + 20
    df['dorm_select'] = df['dorm_select'].map(dorm_select_map)
    df['college_of'] = df['college_of'].map(college_of_map)
    df['personality'] = df['personality'].map(personality_map)
    df['weekend_stay'] = df['weekend_stay'].map(weekend_stay_map)
    df['weekday_stay'] = df['weekday_stay'].map(weekday_stay_map)
    df['smoke'] = df['smoke'].map(smoke_map)
    df['alchol'] = df['alchol'].map(alchol_map)
    df['m_how_eat'] = df['m_how_eat'].map(how_eat_map)
    df['how_eat_in'] = df['how_eat_in'].map(how_eat_in_map)
    df['wake_up'] = df['wake_up'].map(wake_up_map)
    df['m_sleep'] = df['m_sleep'].map(sleep_map)
    df['sleep_sensitive'] = df['sleep_sensitive'].map(sleep_sensitive_map)
    df['sleep_habit'] = df['sleep_habit'].map(sleep_habit_map)
    df['clean_period'] = df['clean_period'].map(clean_period_map)
    df['shower_timezone'] = df['shower_timezone'].map(shower_timezone_map)
    result_dict = df.to_dict(orient='records')

    return(result_dict)

# DB_df = pd.read_csv('/workspace/secondContainer/main_data.csv')
#Db_df
#print(DB_df.columns)
# df_email = DB_df.iloc[:, 1]
# DB_df = DB_df.iloc[:, 2:]
#print(DB_df.columns)

# groups, group_datas = model.fit_model(DB_df)   # 동작 확인

# 새로운 사용자 정보 입력
# new_df = {'email': 'lhj5561@naver.com', 'sex': 1, 'age': 7, 'dorm_select': 1, 'college_of': 8, 'personality': 1, 'weekend_stay': 2,
#  'weekday_stay': 1, 'smoke': 2, 'alchol': 3, 'm_how_eat': 3, 'how_eat_in': 1, 'wake_up': 2, 'm_sleep': 3, 'sleep_sensitive': 2,
#  'sleep_habit': 3, 'clean_period': 2, 'shower_timezone': 1, 'w_age_range': 3, 'w_diff_college_of': 1, 'w_personality': 0,
#  'w_weekend_stay': 2, 'w_weekday_stay': 2, 'w_smoke': 2, 'w_alchol': 3, 'w_how_eat': 3, 'w_how_eat_in': 1, 'w_wake_up': 0,
#  'w_sleep': 3, 'w_sleep_sensitive': 2, 'w_sleep_habit': 3, 'w_clean_period': 3, 'w_shower_timezone': 1}

#add_info = ['m_how_eat', 'how_eat_in', 'clean_period']    # 사전을 통해 나온 결과 단어들 저장 (가정하에)



