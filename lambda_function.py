import sys
import logging
import rds_config
import pymysql
import  requests
import  json
import  os
import boto3
import time
import datetime
import random
from MessageCarousel import MessageCarousel
from MessageReservation import MessageReservation
HEADER = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer zHbvL0w1YLvPsq72QeufxZoATc2K1HuQL1e9sjyrQud82swYNz+9g3mqHuD3dHGBNKkf1qNxYvkBU7d/6W4W8Pz23s/3SL+Mq75ijBD1rHO14Brt4TEqNbqdwRD6DatyBJ9uGIM8mxAWo/gE0s5crgdB04t89/1O/w1cDnyilFU='
}
#rds config
rds_host = "gsoffice.calza1qfpu2i.ap-northeast-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name


greetingCmd = ["안녕", "반가워", "하이", "안녕하세요", "반갑", "반갑습니다", "ㅎㅇ", "hi", "hello", "GS네오텍봇", "GSN", "GS네오텍", "GS 네오텍", "지에스네오텍", "클라우드"]
greetingMsg = ["안녕하세요 ^^ ", "환영합니다 ^^", "반갑습니다 ^^", "Hello :)"]

jokeCmd = ["누구", "누구야", "누구냐", "너", "야", "아", "ㅋ", "ㅋㅋ", "ㅋㅋㅋ"]
jokeMsg = ["안녕하세요 GS네오텍 봇이에요.", "환영합니다 ^^ 예약을 도와드릴게요.", "반갑습니다 ^^ 무엇을 도와드릴까요.", "Hello :) May I help you?"]

showAllCmd = ["예약전체보기", "예약 전체보기", "예약전체", "전체예약", "전체 예약", "예약보여줘",
                "예약내역", "예약 내역",
                "예약 보여줘", "예약알려줘", "예약 알려줘", "예약현황", "예약현황 보여줘", "예약내역 보기"]


def get_room_state(id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('GSOffice')

    try:
        response = table.get_item(Key={'Room': id})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        # print(response)
        return response['Item']

def addWordToDB(db, cursor, word):
    sql = "select * from WordsLog where word=%s"
    cursor.execute(sql, word)
    rows = cursor.fetchall()

    if len(rows) == 0:
        sql = "insert into WordsLog (word, createdAt, count) values (%s, DATE_ADD(now(), interval 9 hour), 1)"
        cursor.execute(sql, (word))
        db.commit()
    else:
        cnt = int(rows[0]['count'])
        uid = int(rows[0]['id'])
        sql = "update WordsLog set count=%s where id=%s"
        cursor.execute(sql, (cnt+1, uid))
        db.commit()

def getReservedData(db, cursor, officeId):
    if officeId == 0:
        sql = "select * from Reservation where confirmation=1 and endTime > DATE_ADD(now(), interval 9 hour) order by startTime ASC"
        cursor.execute(sql)
    else:
        sql = "select * from Reservation where confirmation=1 and endTime > DATE_ADD(now(), interval 9 hour) and officeId=%s order by startTime ASC"
        cursor.execute(sql, officeId)
    rows = cursor.fetchall()


    return rows

def setAndGetReservationUsername(db, cursor, userId, name):
    sql = "select * from Reservation where userId=%s order by reservationTime DESC limit 1 "
    cursor.execute(sql, (userId))
    rows = cursor.fetchall()
    reservationTimeCode = rows[0]['reservationTime']
    sql = "update Reservation set username=%s where reservationTime=%s and userId=%s"
    cursor.execute(sql, (name, reservationTimeCode, userId))
    db.commit()

    rows[0]['username'] = name

    return rows[0]

def reservateConfirmation(db, cursor, userId, code):
    sql = "update Reservation set confirmation=%s where reservationTime=%s and userId=%s"
    cursor.execute(sql, (1, code, userId))

    db.commit()

def setReservationState(db, cursor, userId, timetype, curTime, dt, officeId):
    os.environ['TZ'] = "Asia/Seoul"
    time.tzset()
    cvt_dt = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M')
    time_now = int(time.time())
    cvt2_dt = int(time.mktime(cvt_dt.timetuple()))
    officeId = int(officeId)
    # check valid time
    if(cvt2_dt - time_now < 0):
        print("input time after current time")
        return 2

    # check reserved
    sql = "select * from Reservation where confirmation=1 and startTime > DATE_ADD(now(), interval 0 hour) and officeId=%s"
    cursor.execute(sql, (officeId))
    rows = cursor.fetchall()
    for i in rows:
        reservedStartT = int(time.mktime(i['startTime'].timetuple()))
        reservedEndT = int(time.mktime(i['endTime'].timetuple()))
        print("search db", reservedStartT, reservedEndT)
        if reservedStartT < cvt2_dt and cvt2_dt < reservedEndT:
            return 5
        if timetype == "end":
            if reservedStartT < cvt2_dt or reservedEndT < cvt2_dt:
                return 5
    if timetype == "start":
        sql = "insert into Reservation (userId, startTime, reservationTime, officeId, officeName) values (%s, %s, %s, %s, %s)"
        if officeId == 1:
            officeName = "일리오스"
        elif officeId == 2:
            officeName = "도라도"
        else:
            officeName = "회의실3"
        cursor.execute(sql, (userId, dt, curTime, officeId, officeName))
    elif timetype == "end":

        sql = "select * from Reservation where reservationTime=%s and userId=%s"
        cursor.execute(sql, (curTime, userId))

        rows2 = cursor.fetchall()

        # 종료시간이 시작시간보다 작을 경우
        if int(time.mktime(rows2[0]['startTime'].timetuple()) ) > cvt2_dt :
            return 3

        if cvt2_dt - int(time.mktime(rows2[0]['startTime'].timetuple()) ) > 60*60*6 :
            return 4
        # sql = "update User set processStep=%s where userId=%s"
        #good
        sql = "update Reservation set endTime=%s where reservationTime=%s and userId=%s"
        cursor.execute(sql, (dt, curTime, userId))

        # sql = "insert into Reservation (userId, endTime) values (%s, %s)"



    db.commit()
    return 1
    # return 0

def getUserState(db, cursor, userId):
    sql = "select * from User where userId=%s"
    cursor.execute(sql, (userId))
    rows = cursor.fetchall()

    # print(rows)
    return rows[0]['processStep']
    # return 123

def get_office_state(cursor, id):
    # 0 for all
    # cursor = db.cursor()
    sql = "select * from Office order by id asc"
    cursor.execute(sql)
    rows = cursor.fetchall()

    print(rows)
    if id == 0:
        return rows
    else:
        return rows[id]["state"]

def setUserState(db, cursor, userId, state):
    sql = "update User set processStep=%s where userId=%s"
    cursor.execute(sql, (state, userId))
    db.commit()

def setUserIdToDB(db, cursor, id):
    sql = "select * from User where userId=%s"
    cursor.execute(sql, id)
    rows = cursor.fetchall()
    if len(rows) == 0:
        sql = "insert into User (userId, processStep) values (%s, %s)"
        cursor.execute(sql, (id, 0))
        db.commit()
    else:
        sql = "update User set processStep=%s where userId=%s"
        cursor.execute(sql, (0, id))
        db.commit()


def lambda_handler(event, context):

    try:
        db = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
        # db = pymysql.connect(rds_host, user=name, passwd=password, connect_timeout=5)
    except pymysql.MySQLError as e:
        print("MySQL connect error", e)
        sys.exit()


    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        Offices = MessageCarousel()
        ReserveMsg = MessageReservation()

        # print(Offices.getJson())
        print(event)

        for ee in event['events']:
            userId = ee['source']['userId']
            payload = {
                'replyToken': ee['replyToken'],
                'messages': []
            }
            if ee['type'] == "message":

                if ee['message']['type'] == 'text':
                    msgCmd = ee['message']['text']
                    msgCmdSplit = msgCmd.split(" ")
                    if msgCmd == "사용현황" or msgCmd == "취소":
                        officesState = get_office_state(cursor, 0)
                        setUserIdToDB(db, cursor, userId)
                        for i in officesState:
                            print(i)
                            timeAddDelta = datetime.timedelta(minutes= 3)
                            if i['updateAt'] < datetime.datetime.now() - timeAddDelta:
                                Offices.changeOfficeState(i["id"], 3) # 3 for can not find data from log
                            else:
                                Offices.changeOfficeState(i["id"], i["state"])
                        payload['messages'].append(Offices.getJson())
                    # elif msgCmd == "예약전체보기":
                    elif msgCmd in showAllCmd:
                        reservedData = getReservedData(db, cursor, 0)
                        ReserveMsg.setReservationShowData(reservedData, 0, 0) # first 0 for all office, second 0 for without end msg
                        payload['messages'].append(ReserveMsg.getReservationShowJson())

                    elif len(msgCmdSplit) == 2 and msgCmdSplit[1] == "예약":
                        if(msgCmdSplit[0] == "일리오스"):
                            reservedData = getReservedData(db, cursor, 1) # 1 for ilios
                            ReserveMsg.changeOfficeName(msgCmdSplit[0], 1)
                            ReserveMsg.setReservationShowData(reservedData, 1, 1) # first 1 for ilios office, and second 1 for with end Msg
                            payload['messages'].append(ReserveMsg.getReservationShowJson())
                        elif(msgCmdSplit[0] == "도라도"):
                            reservedData = getReservedData(db, cursor, 2) # 2 for dorado
                            ReserveMsg.changeOfficeName(msgCmdSplit[0], 2)
                            ReserveMsg.setReservationShowData(reservedData, 2, 1) #first 2 for dorado office, and second 1 for with end Msg
                            payload['messages'].append(ReserveMsg.getReservationShowJson())
                        elif(msgCmdSplit[0] == "회의실3"):
                            reservedData = getReservedData(db, cursor, 3) # 3 for office3
                            ReserveMsg.changeOfficeName(msgCmdSplit[0], 3)
                            ReserveMsg.setReservationShowData(reservedData, 3, 1) #first 3 for office3, and second 1 for with end Msg
                            payload['messages'].append(ReserveMsg.getReservationShowJson())
                        payload['messages'].append(ReserveMsg.getReservationJson())
                        setUserState(db, cursor, userId, 1) # set for completed

                    elif getUserState(db, cursor, userId) == 3:
                        reservationData = setAndGetReservationUsername(db, cursor, userId, ee['message']['text'])
                        ReserveMsg.setReservationConfirmData(reservationData)
                        ReserveMsg.setReservationConfirmInfoData(reservationData)
                        print("~~~~~~~~~~~~~~~~~``!")
                        print(reservationData)
                        payload['messages'].append(ReserveMsg.getReservationComfirmInfoJson())
                        payload['messages'].append(ReserveMsg.getReservationComfirmJson())
                        setUserState(db, cursor, userId, 4)
                    elif msgCmd in greetingCmd:
                        randNum = random.randrange(0,len(greetingMsg))
                        payload['messages'].append(Offices.getErrorMsgJson(greetingMsg[randNum]))
                    elif msgCmd in jokeCmd:
                        randNum = random.randrange(0,len(jokeMsg))
                        payload['messages'].append(Offices.getErrorMsgJson(jokeMsg[randNum]))
                    else:
                        if msgCmd != "예약관리":
                            addWordToDB(db, cursor, msgCmd)
                        payload['messages'].append(
                        {
                          "type": "template",
                          "altText": "회의실 예약",
                          "template": {
                            "type": "buttons",
                            "title": "GS네오텍 회의실",
                            "text": "편리하게 사용해보세요",
                            "actions": [
                              {
                                "type": "message",
                                "label": "예약전체보기",
                                "text": "예약전체보기"
                              },
                              {
                                "type": "message",
                                "label": "예약하기",
                                "text": "사용현황"
                              },
                              {
                                "type": "uri",
                                "label": "예약취소",
                                "uri": "http://3.34.171.104/office/select.php"
                              }
                            ]
                          }
                        }
                    )


                else:
                  print("Something Error")
            elif ee['type'] == "postback":
                # if ee['postback']['data'] == "reservationStart" or ee['postback']['data'].split("-")[0] == "reservationEnd":
                curTime = int(time.time())
                # msgCmd.split(" ")
                if ee['postback']['data'].split("-")[0] == "reservationStart":
                    checkState = getUserState(db, cursor, userId)
                    officeId = ee['postback']['data'].split("-")[1]
                    if checkState == 1:

                        ret = setReservationState(db, cursor, userId, "start", curTime, ee['postback']['params']['datetime'], officeId)
                        if ret == 1:
                            setUserState(db, cursor, userId, 2)
                            ReserveMsg.setReservationStarttimeCode(curTime)
                            payload['messages'].append(ReserveMsg.getReservationShowEndtimeJson())
                        elif ret == 2:
                            payload['messages'].append(Offices.getErrorMsgJson("현재시간보다 이전시간은 선택할 수 없습니다"))
                        elif ret == 3:
                            payload['messages'].append(Offices.getErrorMsgJson("예약 종료시간은 시작시간보다 작을 수 없습니다."))
                        elif ret == 5:
                            payload['messages'].append(Offices.getErrorMsgJson("이미 예약된 시간입니다."))
                        else:
                            payload['messages'].append(Offices.getErrorMsgJson("알 수 없는 에러가 발생했습니다."))
                    else:
                        setUserState(db, cursor, userId, 0)
                        payload['messages'].append(Offices.getErrorMsgJson("something wrong"))
                        payload['messages'].append(Offices.getJson())
                elif ee['postback']['data'].split("-")[0] == "reservationEnd":
                    officeId = ee['postback']['data'].split("-")[1]
                    checkState = getUserState(db, cursor, userId)
                    if checkState == 2:
                        ret = setReservationState(db, cursor, userId, "end", ee['postback']['data'].split("-")[1], ee['postback']['params']['datetime'], officeId)
                        if ret == 1:
                            setUserState(db, cursor, userId, 3)
                            payload['messages'].append(ReserveMsg.getReservationInputUsernameJson())
                        elif ret == 2:
                            payload['messages'].append(Offices.getErrorMsgJson("현재시간보다 이전시간은 선택할 수 없습니다"))
                        elif ret == 3:
                            payload['messages'].append(Offices.getErrorMsgJson("예약 종료시간은 시작시간보다 작을 수 없습니다."))
                        elif ret == 4:
                            payload['messages'].append(Offices.getErrorMsgJson("최대 예약시간은 6시간입니다."))
                        else:
                            payload['messages'].append(Offices.getErrorMsgJson("예약된 시간입니다"))


                    else:
                        setUserState(db, cursor, userId, 0)
                        payload['messages'].append(Offices.getErrorMsgJson("잘못된 접근입니다. 다시 선택해주세요."))
                        payload['messages'].append(Offices.getJson())
                elif ee['postback']['data'].split("-")[0] == "reservationConfirm":
                    setUserState(db, cursor, userId, 0)
                    reservateConfirmation(db, cursor, userId, ee['postback']['data'].split("-")[1])
                    reservedData = getReservedData(db, cursor, 0)
                    ReserveMsg.setReservationShowData(reservedData, 0, 0) # first 0 for all office, second 0 for without end msg
                    payload['messages'].append(Offices.getErrorMsgJson("예약이 완료되었습니다!"))
                    payload['messages'].append(ReserveMsg.getReservationShowJson())
                    payload['messages'].append(Offices.getJson())
                elif ee['postback']['data'] == "reservationCancel":
                    setUserState(db, cursor, userId, 0)


            if len(payload['messages']) > 0:
                temp = 0
                # print(json.dumps(payload))
                response = requests.post('https://api.line.me/v2/bot/message/reply',
                    headers=HEADER,
                    data=json.dumps(payload))
    cursor.close()
    db.close()
