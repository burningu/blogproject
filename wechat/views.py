from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)

WECHAT_TOKEN = 'abcd'
WECHAT_AES_KEY = '38ecad2n4UvjND8kzvWscTankK2wonHpyCIZHfk2IVr'
WECHAT_APPID = 'wx0b1b456e3866f75a'
WECHAT_APPSecret = 'a3e866e717c58386ca74a47819a1380d'

@csrf_exempt
def wechat(request):

    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')
    encrypt_type = request.GET.get('encrypt_type', 'raw')
    msg_signature = request.GET.get('msg_signature', '')

    try:
        check_signature(WECHAT_TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        return HttpResponse(status=403)
    if request.method == 'GET':
        echo_str = request.GET.get('echostr', '')
        return HttpResponse(echo_str, content_type="text/plain")
    elif request.method == 'POST':
        from wechatpy import WeChatClient
        client =  WeChatClient(WECHAT_APPID, WECHAT_APPSecret)
        client.menu.create({
            'button':[
                {
                    "type": "scancode_waitmsg",
                    "name": "扫一扫条形码",
                    "key" : 'isbn_sao'
                },
                {
                    "type": "view",
                    "name": "我的网站",
                    "url": "这个网址下文细说，这个字典可以暂时去掉"
                }
            ]
        })
        if encrypt_type == 'raw':
            msg = parse_message(request.body)
            if msg.type == 'text':
                reply = create_reply(msg.content, msg)
            elif msg.type == 'image':
                reply = create_reply(msg.image, msg)
            elif msg.type == 'voice':
                reply = create_reply('这是条语音消息', msg)
            elif msg.type == 'location':
                reply = create_reply(str(msg.location), msg)
            elif msg.type == 'event':
                reply = create_reply(str(msg.event), msg)
                print(msg.event + msg.scene_id + msg.ticket)
            else:
                reply = create_reply('这是条其他类型消息', msg)
            return HttpResponse(reply.render(), content_type="application/xml")
        else:
            from wechatpy.crypto import WeChatCrypto

            crypto = WeChatCrypto(WECHAT_TOKEN, WECHAT_AES_KEY, WECHAT_APPID)
            try:
                msg = crypto.decrypt_message(request.body, msg_signature, timestamp, nonce)
            except (InvalidSignatureException, InvalidAppIdException):
                return HttpResponse(status=403)
            else:
                msg = parse_message(msg)
                if msg.type == 'text':
                    reply = create_reply('这是条文字消息', msg)
                elif msg.type == 'image':
                    reply = create_reply('这是条图片消息', msg)
                elif msg.type == 'voice':
                    reply = create_reply('这是条语音消息', msg)
                else:
                    reply = create_reply('这是条其他类型消息', msg)
                return HttpResponse(crypto.encrypt_message(reply.render(), nonce, timestamp), content_type="application/xml")
    else:  
        logger.info('--------------------------------')  