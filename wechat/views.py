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
WECHAT_AES_KEY = ''
WECHAT_APPID = ''

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
		if encrypt_type == 'raw':
            msg = parse_message(request.body)
            if msg.type == 'text':
                reply = create_reply('这是条文字消息', msg)
            elif msg.type == 'image':
                reply = create_reply('这是条图片消息', msg)
            elif msg.type == 'voice':
                reply = create_reply('这是条语音消息', msg)
            else:
                reply = create_reply('这是条其他类型消息', msg)
            return HttpResponse(reply.render(), content_type="application/xml")
        else:
            from wechatpy.crypto import WeChatCrypto

            crypto = WeChatCrypto(WECHAT_TOKEN, WECHAT_AES_KEY, WECHAT_APPID)
            try:
                msg = crypto.decrypt_message(
                    request.body,
                    msg_signature,
                    timestamp,
                    nonce
                )
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