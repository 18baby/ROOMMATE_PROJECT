from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import widgets, StringField, SubmitField, IntegerField, RadioField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import InputRequired, StopValidation
from flask_wtf.csrf import CSRFProtect

from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as elemTree
import h_predict, h_model
import pandas as pd
import numpy as np
from run_dict import *
import get_db as gdb


import requests

rd = init_dict()
app = Flask(__name__)      # 서버 생성
csrf = CSRFProtect(app)    # form이 제대로 전송되었는지 확인

COLAB_URL="http://5cb8-34-68-247-235.ngrok.io"    #코랩 재연결 시 바꾸기!!
COLAB_API_URL_NLP=COLAB_URL+"/predict"    #코랩 연결
COLAB_API_URL_OKT=COLAB_URL+"/okt_tokenize" 
 
#연결 정보 가져오기
#tree=elemTree.parse('keys.xml')
#DATABASE_URI=tree.find('string[@name="DATABASE_URI"]').text
#SECRET_KEY=tree.find('string[@name="SECRET_KEY"]').text
DATABASE_URI="mysql+pymysql://root:os2window@localhost/users"
SECRET_KEY="my super secret key"

#데이터 베이스 추가
app.config['SQLALCHEMY_DATABASE_URI']=DATABASE_URI

#폼 비밀키 설정
app.config['SECRET_KEY']=SECRET_KEY


#Initalize DB
db=SQLAlchemy(app)

#모델 생성 -> table 생성
class Usertbl(db.Model):
    __table_name__ = 'usertbl'
    
    email=db.Column(db.String(50), primary_key=True)
    sex=db.Column(db.Integer, nullable=False)
    age=db.Column(db.Integer, nullable=False)
    dorm_select=db.Column(db.Integer, nullable=False)
    
    college_of=db.Column(db.Integer, nullable=False)
    personality=db.Column(db.Integer, nullable=False)
    weekend_stay=db.Column(db.Integer, nullable=False)
    weekday_stay=db.Column(db.Integer, nullable=False)
    smoke=db.Column(db.Integer, nullable=False)
    alchol=db.Column(db.Integer, nullable=False)
    m_how_eat=db.Column(db.Integer, nullable=False)
    how_eat_in=db.Column(db.Integer, nullable=False)
    wake_up=db.Column(db.Integer, nullable=False)
    m_sleep=db.Column(db.Integer, nullable=False)
    sleep_sensitive=db.Column(db.Integer, nullable=False)
    sleep_habit=db.Column(db.Integer, nullable=False)
    clean_period=db.Column(db.Integer, nullable=False)
    shower_timezone=db.Column(db.Integer, nullable=False)

    w_age_range=db.Column(db.Integer, nullable=False)
    w_diff_college_of=db.Column(db.Integer, nullable=False)
    w_personality=db.Column(db.Integer, nullable=False)
    w_weekend_stay=db.Column(db.Integer, nullable=False)
    w_weekday_stay=db.Column(db.Integer, nullable=False)
    w_smoke=db.Column(db.Integer, nullable=False)
    w_alchol=db.Column(db.Integer, nullable=False)
    w_how_eat=db.Column(db.Integer, nullable=False)
    w_how_eat_in=db.Column(db.Integer, nullable=False)
    w_wake_up=db.Column(db.Integer, nullable=False)
    w_sleep=db.Column(db.Integer, nullable=False)
    w_sleep_sensitive=db.Column(db.Integer, nullable=False)
    w_sleep_habit=db.Column(db.Integer, nullable=False)
    w_clean_period=db.Column(db.Integer, nullable=False)
    w_shower_timezone=db.Column(db.Integer, nullable=False)
    
    

#멀티 체크박스 필드 생성
class MultiCheckBoxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

#멀티 체크박스 적어도 하나 입력 (이거 안 먹힘..?)
class MultiCheckboxAtLeastOne():
    def __init__(self, message=None):
        if not message:
            message = '적어도 하나 선택해 주세요.'
        self.message = message

    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation(self.message)

#폼 클래스 만들기    
class UserForm(FlaskForm):
    
    #기본 속성
    personality=RadioField("성격 유형", choices=[(1,'외향적'),(2,'내향적')], coerce=int, validators=[InputRequired()])
    weekend_stay=RadioField("주말 거주 유형", choices=[(1,'주로 기숙사내'),(2,'주로 기숙사 밖')], coerce=int, validators=[InputRequired()])
    weekday_stay=RadioField("평일 거주 유형", choices=[(1,'주로 기숙사내'),(2,'주로 기숙사 밖')], coerce=int, validators=[InputRequired()])
    smoke=RadioField("흡연 유무", choices=[(1,'아니다'),(2,'그렇다')], coerce=int, validators=[InputRequired()])
    alcohol=RadioField("음주 정도", choices=[(1, '드물게'), (2, '보통'), (3, '자주')], coerce=int, validators=[InputRequired()])
    m_how_eat=RadioField("식사 해결 장소", choices=[(1, '기숙사 내'), (2, '기숙사 밖'), (3, '기숙사 식당')], coerce=int, validators=[InputRequired()])
    how_eat_in=RadioField("배달음식 같이 먹기 희망 여부", choices=[(1,'비희망'),(2,'희망')], coerce=int, validators=[InputRequired()])
    wake_up=RadioField("평균 기상 시간", choices=[(1,'6시~8시'),(2,'8시~10시'),(3,'10시~12시'), (4,'12시 이후')], coerce=int, validators=[InputRequired()])
    m_sleep=RadioField("평균 취침 시간", choices=[(1,'10시~12시'),(2,'12시~2시'),(3,'2시 이후')], coerce=int, validators=[InputRequired()])
    sleep_sensitive=RadioField("취침시 예민도", choices=[(1,'둔감'),(2,'예민')], coerce=int, validators=[InputRequired()])
    sleep_habit=RadioField("잠버릇 유무", choices=[(1,'없다'), (2, '있다'), (3,'잘 모르겠다')], coerce=int, validators=[InputRequired()])
    clean_period=RadioField("일주일동안 청소 빈도", choices=[(1,'드물게(1회~0회)'),(2,'보통(2회~4회)'),(3,'자주(5회~7회)')], coerce=int, validators=[InputRequired()])
    shower_timezone=RadioField("샤워 시간대", choices=[(1,'아침'),(2,'저녁')], coerce=int, validators=[InputRequired()])

    #유저 정보
    email=StringField("이메일", validators=[InputRequired()])
    age=IntegerField("나이", validators=[InputRequired()])
    sex=RadioField("성별", choices=[(1,'남자'),(2,'여자')], coerce=int, validators=[InputRequired()])
    dorm_select=RadioField("거주 홀 정보", choices=[(1, '레이크홀'), (2, '비레이크홀')], coerce=int, validators=[InputRequired()])
    college_of=SelectField("단과대", choices=[(1, '문과대'), (2, '이과대'), (3, '건축대'), (4, '공과대'), (5, '사과대'), 
                                              (6, '경영대'), (7, '부동산대'), (8, '융기원'), (9, '생명과학대'), (10, '수의대'),
                                              (11, '예디대'), (12, '사범대'), (13, '그외')], coerce=int, validators=[InputRequired()])
    #1: 문과대	2: 이과대	3. 건축대	4. 공과대	5. 사과대	6. 경영대	7. 부동산	8. 융기원	9. 생명과학대 10. 수의대 11. 예디대 12. 사범대 13. 그외
    
    submit=SubmitField("다음 페이지로")
    
class MateForm(FlaskForm):
    
    #기본 속성
    w_personality=RadioField("성격 유형", choices=[(1,'외향적'),(2,'내향적'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_weekend_stay=RadioField("주말 거주 유형", choices=[(1,'주로 기숙사내'),(2,'주로 기숙사 밖'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_weekday_stay=RadioField("평일 거주 유형", choices=[(1, '주로 기숙사내'), (2, '주로 기숙사 밖'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_smoke=RadioField("흡연 유무", choices=[(1,'아니다'),(2,'그렇다'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_alcohol=RadioField("음주 정도", choices=[(1, '드물게'), (2, '보통'), (3, '자주'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_how_eat=RadioField("식사 해결 장소", choices=[(1, '기숙사 내'), (2, '기숙사 밖'), (3, '기숙사 식당'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_how_eat_in=RadioField("배달음식 같이 먹기 희망 여부", choices=[(1,'비희망'),(2,'매우 희망'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_wake_up=RadioField("평균 기상 시간", choices=[(1,'6시~8시'),(2,'8시~10시'),(3,'10시~12시'), (4,'12시 이후'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_sleep=RadioField("평균 취침 시간", choices=[(1,'10시~12시'),(2,'12시~2시'),(3,'2시 이후'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_sleep_sensitive=RadioField("취침시 예민도", choices=[(1,'둔감'),(2,'예민'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_sleep_habit=RadioField("잠버릇 유무", choices=[(1,'없다'), (2,'있다'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_clean_period=RadioField("일주일동안 청소 빈도", choices=[(1,'드물게(1회~0회)'),(2,'보통(2회~4회)'),(3,'자주(5회~7회)'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_shower_timezone=RadioField("샤워 시간대", choices=[(1,'아침'),(2,'저녁'), (0, '상관없음')], coerce=int, validators=[InputRequired()])

    #룸메이트 정보
    w_age_range=RadioField("원하는 상대방 나이", choices=[(1, '20~21살'), (2, '22~23살'), (3, '24~25살'), (4, '26살 이상'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    w_diff_college_of=RadioField("같은 단과대 희망 여부", choices=[(1, '비희망'),(2,'희망'), (0, '상관없음')], coerce=int, validators=[InputRequired()])
    
    #추가정보
    w_focus_text=TextAreaField("위 문항들 중 중요하게 여겼으면 좋겠는 정보")   #말을 바꾸기
    
    submit=SubmitField("Submit")
    
@app.route("/")
def hello():
    ######코랩 넘기기 코드
    # print("문장입력####")
    # input_sentence=input()     #문장 입력 부분 (248번째 줄에 존재)
    # tokenized_list=make_okt_token(input_sentence)
    # ret_list, no_keys_list=return_words(tokenized_list, rd)
    # nlp_list=make_nlp_predict(no_keys_list)
    # print("코랩결과물####", tokenized_list, ret_list, no_keys_list, nlp_list)
    return render_template("index.html")


@app.route("/servey", methods=["GET", "POST"])
def servey():
    email, sex, age, dorm_select, college_of, personality, weekend_stay, weekday_stay=None, 0, None, None, None, None, None, None
    smoke, alcohol, m_how_eat, how_eat_in, wake_up, m_sleep, sleep_sensitive, sleep_habit, clean_period=None, None, None, None, None, None, None, None, None
    shower_timezone=None
    error_msg=""
    form=UserForm(request.form) 
    
    kwargs={'email': email, 'sex': sex, 'age': age, 'dorm_select': dorm_select, 'college_of': college_of, 'personality': personality,
            'weekend_stay': weekend_stay, 'weekday_stay': weekday_stay, 'smoke': smoke, 'alchol': alcohol, 'm_how_eat': m_how_eat, 'how_eat_in': how_eat_in, 'wake_up': wake_up,
            'm_sleep': m_sleep, 'sleep_sensitive': sleep_sensitive, 'sleep_habit': sleep_habit, 'clean_period': clean_period, 
            'shower_timezone': shower_timezone}
    
    #Validate Form & 이메일 중복확인 후 입력 완료 후 데이터 세션으로 servey2로 넘김
    if request.method=="POST" and form.validate():
        before_mail=form.email.data
        existingEmail=Usertbl.query.filter_by(email=form.email.data).first()
        
        if existingEmail is not None:
            form=UserForm(formdata=None)
            error_msg="중복되는 이메일"
            return render_template("servey.html", error_msg=error_msg, **kwargs, form=form)
        else: 
            age=form.age.data
            if age<20:
                age=20
            elif age>28:
                age=28
            user_dict={'email': form.email.data, 'sex': form.sex.data, 'age': (age)%10, 'dorm_select': form.dorm_select.data, 'college_of': form.college_of.data, 'personality': form.personality.data,
                       'weekend_stay': form.weekend_stay.data, 'weekday_stay': form.weekday_stay.data, 'smoke': form.smoke.data, 'alchol': form.alcohol.data, 'm_how_eat': form.m_how_eat.data, 'how_eat_in': form.how_eat_in.data, 
                       'wake_up': form.wake_up.data, 'm_sleep': form.m_sleep.data, 'sleep_sensitive': form.sleep_sensitive.data, 'sleep_habit': form.sleep_habit.data, 
                       'clean_period': form.clean_period.data, 'shower_timezone': form.shower_timezone.data}
        
            session['user_dict'] = user_dict
            return redirect(url_for('servey2'), code=307)
            
        form=UserForm(formdata=None)
    
    return render_template("servey.html", error_msg=error_msg, **kwargs, form=form)


@app.route("/servey2", methods=["GET", "POST"])
def servey2():
    # 사용자 정보 가져오기
    user_dict = session.get('user_dict', None)
    print(f'{user_dict} 데이터 수신 성공')  # survey1에서 데이터 전송 확인
    
    w_age_range, w_diff_college_of, w_personality, w_weekend_stay, w_weekday_stay=None, None, None, None, None
    w_smoke, w_alcohol, w_how_eat, w_how_eat_in, w_wake_up, w_sleep, w_sleep_sensitive, w_sleep_habit, w_clean_period=None, None, None, None, None, None, None, None, None
    w_shower_time, w_shower_timezone, w_material_share, w_bug_catch, w_phone_chat_in, w_phone_chat_time, w_age_range=None, None, None, None, None, None, None
    w_dorm_select, w_focus_text=None, None
    error_msg=""
    form=MateForm(request.form)
    
    kwargs={'age_range': w_age_range, 'diff_college_of': w_diff_college_of, 'personality': w_personality, 'weekend_stay': w_weekend_stay, 
            'weekday_stay': w_weekday_stay, 'smoke': w_smoke, 'alchol': w_alcohol, 'm_how_eat': w_how_eat, 'how_eat_in': w_how_eat_in, 'wake_up': w_wake_up,
            'm_sleep': w_sleep, 'sleep_sensitive': w_sleep_sensitive, 'sleep_habit': w_sleep_habit, 'clean_period': w_clean_period, 
            'shower_timezone': w_shower_timezone, 'focus_text': w_focus_text}
    
    #Validate Form
    if request.method=="POST" and form.validate():
        print('POST WORKS')
        # # MateForm에만 있는 항목들, 아무 값도 안들어가있음
        # print("DIFF COLL:",form.diff_college_of.data)
        # print("AGE RANGE:",form.age_range.data)
        # # BaseForm에 있는 항목들, 제대로 값이 들어가 있음
        # print("PERSONALITY:",form.personality.data)
        # print("HOW EAT",form.how_eat.data)
        mate_dict={'w_age_range': form.w_age_range.data, 'w_diff_college_of': form.w_diff_college_of.data, 'w_personality': form.w_personality.data, 
                   'w_weekend_stay': form.w_weekend_stay.data, 'w_weekday_stay': form.w_weekday_stay.data, 'w_smoke': form.w_smoke.data, 
                   'w_alchol': form.w_alcohol.data, 'w_how_eat': form.w_how_eat.data, 'w_how_eat_in': form.w_how_eat_in.data, 
                   'w_wake_up': form.w_wake_up.data, 'w_sleep': form.w_sleep.data, 'w_sleep_sensitive': form.w_sleep_sensitive.data, 
                   'w_sleep_habit': form.w_sleep_habit.data, 'w_clean_period': form.w_clean_period.data, 
                   'w_shower_timezone': form.w_shower_timezone.data }   

        merge_dict={**user_dict, **mate_dict}    # 사용자로 부터 입력받은 내용
        print(merge_dict)
        
        ########################
        print(request.form.get('w_focus_text'))    #추가정보 입력한 값(연결 필요!!!!!!!)
        input_additional_sentence=request.form.get('w_focus_text')
        ########################
        if input_additional_sentence=='':
            add_info=[]
        else:
            tokenized_list=make_okt_token(input_additional_sentence)  # 코랩 형태소 분석기
            ret_list, no_keys_list=return_words(tokenized_list, rd)   
            
            if len(no_keys_list)!=0:
                nlp_res=make_nlp_predict(no_keys_list)
            
            key_list=[]
            for no_key in no_keys_list:
                key_list.extend(nlp_res[no_key])
            print(key_list)
            weight, word=split_list(key_list)
            
            print("코랩결과물####", tokenized_list, ret_list, no_keys_list, word)
            add_info=ret_list+word
        
            # 중복으로 나타난 특성을 제거하는 부분
            add_info = list(set(add_info))
            
            #add_info=['alchol']
        print("추가정보", add_info)
        
        #DB에 저장
        user=Usertbl(**merge_dict)
        db.session.add(user)
        db.session.commit()
        
        
        ########모델 선택 부분############
        h_predict.model_predict(merge_dict, groups, add_info, group_datas, email, DB_df)
        #model_predict(merge_dict, cluster_group_df, group_datas, origin_df)    #predict.py에 넘기기
        
        return redirect(url_for('result'), code=307)

    #Clear Form
    form=MateForm(formdata=None)
    return render_template("servey2.html", error_msg=error_msg, **kwargs, form=form)


@app.route("/result", methods=["GET", "POST"])
def result():   
    user_data_dict=session.get('user_data_dict', None)
    print("result 받음")
    print(user_data_dict)
    return render_template("result.html", show_users=user_data_dict)


@app.route("/qna", methods=["GET", "POST"])
def qna():
    #DB 내용 전부 출력
    show_users=Usertbl.query.all()
    return render_template("qna.html")


# 생성자 확인(우리정보)
@app.route("/creator")
def creator():
    return render_template("creator.html")


# 우리 모델 실행
# def model_predict(merge_dict, groups, add_info, group_datas, df_email, label_df, DB_df):
#     print("예측 실행")
#     return model_predict(merge_dict, groups, add_info, group_datas, df_email, label_df, DB_df)


#코랩에 데이터 넘기기
def make_okt_token(additional_info):
    data={"추가정보": additional_info}
    print(data)
    response=requests.post(COLAB_API_URL_OKT, json=data)
    #print(response.status_code, response.text)# HTTP 상태 코드를 확인합니다. 200이어야 합니다.
    result=response.json()
    #df_res=make_data_frame(result)
    print(result['tokenized_list'])
    return result['tokenized_list']   #이 부분 사전에 연결하면 될 듯


def make_nlp_predict(no_keys_list):
    data={"없는키": no_keys_list}
    print(data)
    response=requests.post(COLAB_API_URL_NLP, json=data)
    print(response.status_code, response.text)# HTTP 상태 코드를 확인합니다. 200이어야 합니다.
    result=response.json()
    #df_res=make_data_frame(result)
    print(result)
    return result


#JSON to 데이터 프레임
# def make_data_frame(similar_dict):
#     df_res=pd.DataFrame([[k] + v for k, v in similar_dict.items()], columns=['원래단어', '분류1', '분류2', '분류3'])
#     return df_res


if __name__ == "__main__":
    
    # origin_df = gdb.get_db()
    # df_email=origin_df.iloc[:, 1]
    # DB_df = pd.read_csv('introduce\main_data.csv', encoding='utf-8')
    # DB_df=origin_df.iloc[:, 2:]
    # DB_df = DB_df.iloc[:191, :]
    DB_df = pd.read_csv('main_data.csv', encoding='utf-8')
    DB_df = DB_df.iloc[:, 1:]
    label_df = pd.read_csv('label_df.csv',encoding='utf-8')
    label_df = label_df.iloc[: , 1:]
    print(label_df)
    email, groups, group_datas = h_model.fit_model(DB_df)
    # cluster_group_df, group_datas, df_label = model.fit_model(origin_df)
    # print(cluster_group_df[0])
    # print(group_datas)
    print("done..")
    app.run(host='127.0.0.1', port=8484, use_reloader=False)

