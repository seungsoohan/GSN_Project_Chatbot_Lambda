import json class MessageCarousel: def __init__(self, ):
        # self.data = Object()
        self.errorMsgData = { "type": "text", "text": "잘못된 
                      접근입니다. 다시 선택해주세요."
                    }
        self.data = { "type": "template", "altText": "회의실 사용현황", 
                      "template": {
                        "type": "carousel", "imageSize": "cover", 
                        "imageAspectRatio": "rectangle", "columns": [
                          { "thumbnailImageUrl": 
                            "https://seungsoo-images-bucket.s3.ap-northeast-2.amazonaws.com/ilios.jpg", 
                            "title": "Ilios 회의실", "text": "사용가능", 
                            "actions": [
                              { "type": "postback", "label": "예약하기", 
                                "text": "일리오스 예약", "data": "Data 
                                1"
                              },
                              
                              { "type": "uri", "label": "자세히보기", 
                                "uri": 
                                "http://3.34.171.104/iot/office/log/?n=90"
                              },
                            ]
                          },
                          { "thumbnailImageUrl": 
                            "https://seungsoo-images-bucket.s3.ap-northeast-2.amazonaws.com/dorado.jpg", 
                            "title": "Dorado 회의실", "text": 
                            "사용불가", "actions": [
                              { "type": "message", "label": "예약하기", 
                                "text": "예약하기"
                              },
                              { "type": "message", "label": 
                                "자세히보기", "text": "도라도 세부사항"
                              }
                            ]
                          },
                          { "thumbnailImageUrl": 
                            "https://seungsoo-images-bucket.s3.ap-northeast-2.amazonaws.com/GSN.jpg", 
                            "title": "**** 회의실", "text": "확인불가", 
                            "actions": [
                              { "type": "message", "label": "예약하기", 
                                "text": "예약하기"
                              },
                              { "type": "message", "label": 
                                "자세히보기", "text": "자세히보기"
                              }
                            ]
                          }
                        ]
                      }
                    }
        
    def makeCarousel(self): temp = 1 def changeOfficeState(self, OId, 
    state):
        # val = json.dumps(self.data)
        stateCmdStr = "" if state == 0: stateCmdStr = "사용 가능" elif 
        state == 1:
            stateCmdStr = "사용 중" elif state == 2: stateCmdStr = "예약 
            중"
        else: stateCmdStr = "확인 불가" 
        self.data["template"]["columns"][OId-1]["text"] = stateCmdStr
        # val.type = "zzz" temp = 2
        
    def getJson(self):
        # return json.dumps(self.data)
        return self.data def getErrorMsgJson(self, data): 
        self.errorMsgData['text'] = data return self.errorMsgData
        
