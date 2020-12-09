from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.conf import settings

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import pya3rt

# LINE Messaging APIは、CHANNEL_ACCESS_TOKENとCHANNEL_SECRETが必要
line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN) # 各API通信を行うときに使用
handler = WebhookHandler(settings.CHANNEL_SECRET) # 署名の検証で使用
talk_api = settings.TALK_API # 雑談BotAPI

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')

    def post(self, request, *args, **kwargs):
        # リクエストヘッダーから署名検証のための値を取得
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        # リクエストボディを取得
        body = request.body.decode('utf-8')

        try:
            # 署名を検証して、問題なければhandleに定義されている関数を呼び出す
            handler.handle(body, signature)
        except InvalidSignatureError:
            # 署名検証で失敗した場合は、例外をあげる
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            # APIのエラーが発生した場合は、例外をあげる
            print(e)
            return HttpResponseServerError()

        # 処理が成功したらOKを表示
        return HttpResponse('OK')

    # 外部からのアクセスを可能にする
    # csrf_tokenを渡していないpostメソッドは403エラーになるため
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    # staticmethod関数は、インスタンス化せずに呼び出せる関数のこと
    # handlerのaddメソッドで、リクエストのイベント毎に実行する関数を記述
    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    def message_event(event):
        # オウムが返しする
        # reply = event.message.text

        # 雑談Bot
        client = pya3rt.TalkClient(talk_api)
        response = client.talk(event.message.text)
        reply = response['results'][0]['reply']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
