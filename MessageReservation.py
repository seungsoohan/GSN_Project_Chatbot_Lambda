import json
import time
import datetime
class MessageReservation:
    def __init__(self, ):
      self.mymy = "123"

      self.reservationData = {
                "type": "template",
                "altText": "this is a buttons template",
                "template": {
                  "type": "buttons",
                  "title": "회의실 예약",
                  "text": "일리오스 회의실 ",
                  "actions": [
                    {
                      "type": "datetimepicker",
                      "label": "예약 시작시간 선택",
                      "data": "reservationStart",
                      "mode": "datetime",
                      "initial": "2020-12-08T15:23",
                      "max": "2021-12-08T15:23",
                      "min": "2019-12-08T15:23"
                    },
                    {
                      "type": "postback",
                      "label": "취소",
                      "text": "예약취소",
                      "data": "Data 2"
                    }
                  ]
                }
              }

      self.reservationShowData = {
                  "type": "text",
                  "text": "일리오스 회의실 예약정보\n================\n2020년 12월 18일\n\n13시00분 ~ 14시30분 한승수\n\n예약된 시간을 제외하고 선택해주세요."
                }
      self.reservationSelectEndTime = {
                  "type": "template",
                  "altText": "this is a confirm template",
                  "template": {
                    "type": "confirm",
                    "actions": [
                      {
                        "type": "datetimepicker",
                        "label": "시간선택",
                        "data": "reservationEnd",
                        "mode": "datetime",
                        "initial": "2020-12-18T13:19",
                        "max": "2021-12-18T13:19",
                        "min": "2019-12-18T13:19"
                      },
                      {
                        "type": "postback",
                        "label": "취소",
                        "text": "예약취소",
                        "data": "reservationCancel"
                      }
                    ],
                    "text": "회의 종료시간을 선택해주세요"
                  }
                }
      self.reservationGetUsername = {
                  "type": "text",
                  "text": "예약자 성함을 입력해주세요."
                }
      self.reservationConfirmInfo = {
                  "type": "text",
                  "text": "12월 18일 14시30분 ~ 12월 18일 16시50분 \n예약자 한승수 \n"
                }
      self.reservationConfirmMsg = {
                  "type": "template",
                  "altText": "this is a confirm template",
                  "template": {
                    "type": "confirm",
                    "actions": [
                      {
                        "type": "postback",
                        "label": "확인",
                        "data": "Data 1"
                      },
                      {
                        "type": "postback",
                        "label": "취소하기",
                        "text": "예약 취소하기",
                        "data": "Data 2"
                      }
                    ],
                    "text": "예약하시겠습니까?"
                  }
                }
    def changeOfficeName(self, name):
        self.reservationData["template"]["text"] = name + " 회의실"

    def getReservationJson(self):
        return self.reservationData

    def setReservationShowData(self, data):
      print("set Reservation #############3")
      print(data)
      textMsg = ""
      textMsg += "일리오스 " + "회의실 예약정보\n"
      textMsg += "==================\n"
      for i in data:
        startT = datetime.datetime.strftime(i['startTime'], '%Y년%m월 %d일')
        # %Y-%m-%dT%H:%M')
        startMeetingTime = datetime.datetime.strftime(i['startTime'], '%H시%M분')
        endMeetingTime = datetime.datetime.strftime(i['endTime'], '%H시%M분')
        textMsg += startT + "\n"
        textMsg += startMeetingTime + " ~ " + endMeetingTime + "\n\n"
      textMsg += "예약된 시간을 제외하고 선택해주세요."
      self.reservationShowData['text'] = textMsg
        # self.reservationShowData['text'] = "hihi"

    def getReservationShowJson(self):
        return self.reservationShowData

    def setReservationStarttimeCode(self, timestamp):
        self.reservationSelectEndTime['template']['actions'][0]['data'] = "reservationEnd-" + str(timestamp)
        # a = 1
    def getReservationShowEndtimeJson(self):
        return self.reservationSelectEndTime

    def getReservationInputUsernameJson(self):
        return self.reservationGetUsername

    def getReservationComfirmInfoJson(self):
        return self.reservationConfirmInfo

    def getReservationComfirmJson(self):
        return self.reservationConfirmMsg

    def setReservationConfirmData(self, data):
      code = data['reservationTime']
      self.reservationConfirmMsg['template']['actions'][0]['data'] = "reservationConfirm-" + str(code)

    def setReservationConfirmInfoData(self, data):

      # startT = time.strftime('%Y-%m-%d %H:%M:%S', data['startTime'])
      # endT = time.strftime('%Y-%m-%d %H:%M:%S', data['endTime'])
      startT = data['startTime']
      # startT = startT[5:15]
      startT = startT.strftime("%d일 %H시 %M분")
      endT = data['endTime']
      endT = endT.strftime("%H시 %M분")
      # endT = endT[5:15]
      username = data['username']
      if startT == None:
        startT = "예약시작시간 미확인"
      if endT == None:
        endT = "예약종료시간 미확인"
      if username == None:
        username = "예약자 정보 확인불가"
      content = "회의실 예약을 진행하겠습니다.\n 시간과 예약자 성함을 확인해 주세요.\n" + str(startT) + " ~ " + str(endT) + "\n" + "예약자: " + username
      self.reservationConfirmInfo['text'] = content
