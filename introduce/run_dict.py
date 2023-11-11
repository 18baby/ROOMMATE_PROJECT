import redis
import pandas as pd
import csv

# redis commands

# rd.set("[키]", "[값]")
# rd.get("[키]").decode('utf-8')
# rd.delete("[키]")
# rd.flushdb()


# dictionary 연결
def init_dict():
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    return rd


# dictionary 연결 종료
# dict
def finish_dict(db):
    db.connection_pool.disconnect()


# dictionary에 저장된 모든 key의 list를 출력하는 함수
# dict
def get_list(db):

    # 각 키에 해당하는 값을 가져와서 출력
    result = []
    for key in db.keys('*'):
        values = db.lrange(key.decode('utf-8'), 0, -1)  # 한글 키를 UTF-8로 디코딩
        decoded_values = [value.decode('utf-8') if value is not None else None for value in values]
        result.extend(decoded_values)

    return result


# csv 파일을 읽어서 dictionary에 저장하는 함수
# 파일 경로, dict
def csv_read(file_path, db):
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')

            if len(parts) == 2:
                key, value = parts
                db.set(key, value)
                print(f"Saved Key: {key}, Value: {value} to Redis")
            else:
                print(f"Ignored Line: {line.strip()}")

    print("Data from the file has been saved to Redis.")


# 데이터프레임을 읽어서 dictionary에 저장하는 함수
# 데이터프레임<key, val1, val2, val3>, dict
def df_read(df, db):
    for index, row in df.iterrows():
        key = row['word'].encode('utf-8')
        values = [v for v in [row['val1'], row['val2'], row['val3']] if not pd.isna(v)]
        # print(values)
        if not values:
            continue
        # Redis 리스트에 데이터 저장
        db.rpush(key, *values)


# 백업 csv 파일을 작성하는 함수 (사용x)
# key
def write_log(key):
    with open(csv_file_path, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([key])


# 리스트를 + 기준으로 파싱해서 각각 가중치, 특성 단어 리스트로 리턴하는 함수
# <가중치+특성> 으로 저장된 리스트
def split_list(my_list):
    weight = []
    word = []

    for item in my_list:
        # print(item)
        parts = item.split('+')
        if len(parts) == 2:
            weight.append(parts[0])
            word.append(parts[1])

    return weight, word


# key를 읽어서 해당하는 리스트를 리턴하는 함수
# key, dict
def get_val(key, db):
    values = db.lrange(key.encode('utf-8'), 0, -1)

    result = [value.decode('utf-8') if value is not None else None for value in values]
    return result


# key 리스트를 받아서, dictionary를 먼저 확인해보고, 그 결과를 res 리스트에 저장
# 만약 key가 없으면 단어 유사도 모델에 사용할 리스트(no_keys)에 저장
# res는 1차원 list [특성, 특성, 특성]으로 변환 후 리턴
# key 리스트, dict
def return_words(key_list, db):
    res = []
    no_keys = []

    for i in range(len(key_list)):
        if not get_val(key_list[i], db):
            no_keys.append(key_list[i])
        else:
            res.append(get_val(key_list[i], db))

    res = [item for sublist in res for item in sublist]
    tmp, res = split_list(res)
    return res, no_keys


# 테스트용 main 함수
if __name__ == '__main__':

    csv_file_path = 'backup.csv'
    rd = init_dict()

    load_path = '/Users/ihongju/Documents/ROOMMATE_PROJECT/dictionary/input.csv'
    df = pd.read_csv(load_path, encoding='utf-8')

    df_read(df, rd)
    # word_list = get_list(rd)
    # list1, list2 = split_list(word_list)
    # print(list1)
    # print(list2)
    # bulkload_dict('dict.txt', rd)
    # rd.set(key, value)
    # print_dict(rd)
    # print(str(rd.get('시험').decode('utf-8')))
    temp_list = ['김치']

    res, non_key = return_words(temp_list, rd)
    print(res, non_key)
    # r1, r2 = split_list(res)
    # print(r1, r2)
    # rd.flushdb()
#   종료
    finish_dict(rd)