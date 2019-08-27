# -*- coding: UTF-8 -*-
from Crypto.Cipher import AES
import sys
import hashlib
import hmac
import string
import time
import urllib2
import base64
import json

AUTHORIZATION = "authorization"
DEFAULT_ENCODING = 'UTF-8'
AUTH_STRING_PREFIX = "yff-openapi-sign"

# 保存AK/SK的类
class BceCredentials(object):
    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key


# 根据RFC 3986，除了：
#   1.大小写英文字符
#   2.阿拉伯数字
#   3.点'.'、波浪线'~'、减号'-'以及下划线'_'
# 以外都要编码
RESERVED_CHAR_SET = set(string.ascii_letters + string.digits + '.~-_')
def get_normalized_char(i):
    char = chr(i)
    if char in RESERVED_CHAR_SET:
        return char
    else:
        return '%%%02X' % i
NORMALIZED_CHAR_LIST = [get_normalized_char(i) for i in range(256)]


# 正规化字符串
def normalize_string(in_str, encoding_slash=True):
    if in_str is None:
        return ''

    # 如果输入是unicode，则先使用UTF8编码之后再编码
    in_str = in_str.encode(DEFAULT_ENCODING) if isinstance(in_str, unicode) else str(in_str)

    # 在生成规范URI时。不需要对斜杠'/'进行编码，其他情况下都需要
    if encoding_slash:
        encode_f = lambda c: NORMALIZED_CHAR_LIST[ord(c)]
    else:
        # 仅仅在生成规范URI时。不需要对斜杠'/'进行编码
        encode_f = lambda c: NORMALIZED_CHAR_LIST[ord(c)] if c != '/' else c

    # 按照RFC 3986进行编码
    return ''.join([encode_f(ch) for ch in in_str])


# 生成规范URI
def get_canonical_uri(path):
    # 规范化URI的格式为：/{bucket}/{object}，并且要对除了斜杠"/"之外的所有字符编码
    return normalize_string(path, False)


# 生成规范query string
def get_canonical_querystring(params):
    if params is None:
        return ''

    # 除了authorization之外，所有的query string全部加入编码
    result = ['%s=%s' % (k, normalize_string(v)) for k, v in params.items() if k.lower != AUTHORIZATION]

    # 按字典序排序
    result.sort()

    # 使用&符号连接所有字符串并返回
    return '&'.join(result)


# 生成规范header
def get_canonical_headers(headers, headers_to_sign=None):
    headers = headers or {}

    # 没有指定header_to_sign的情况下，默认使用：
    #   1.host
    #   2.content-md5
    #   3.content-length
    #   4.content-type
    #   5.所有以x-bce-开头的header项
    # 生成规范header
    if headers_to_sign is None or len(headers_to_sign) == 0:
        headers_to_sign = {"host", "content-md5", "content-length", "content-type"}
    else:
        headers_to_sign = {d.strip().lower() for d in headers_to_sign}

    # 对于header中的key，去掉前后的空白之后需要转化为小写
    # 对于header中的value，转化为str之后去掉前后的空白
    f = lambda (key, value): (key.strip().lower(), str(value).strip())

    result = []
    for k, v in map(f, headers.iteritems()):
        # 无论何种情况，以x-bce-开头的header项都需要被添加到规范header中
        if k in headers_to_sign and AUTHORIZATION != k:
            result.append("%s:%s" % (normalize_string(k), normalize_string(v)))

    # 按照字典序排序
    result.sort()

    # 使用\n符号连接所有字符串并返回
    return '\n'.join(result)


# 签名主算法
def normal_sign(credentials, http_method, path, headers, params,
         timestamp=0, expiration_in_seconds=1800, headers_to_sign=None):
    headers = headers or {}
    params = params or {}

    # 1.生成sign key
    # 1.1.生成auth-string，格式为：yff-openapi-sign/{accessKeyId}/{timestamp}/{expirationPeriodInSeconds}
    sign_key_info = AUTH_STRING_PREFIX + '/%s/%d/%d' % (
        credentials.access_key_id,
        timestamp,
        expiration_in_seconds)

    print 'auth-string = %s,accessKeyId = %s,secret_access_key = %s'%(sign_key_info,credentials.access_key_id,credentials.secret_access_key)

    # 1.2.使用auth-string加上SK，用SHA-256生成sign key
    sign_key = hmac.new(
        credentials.secret_access_key,
        sign_key_info,
        hashlib.sha256).hexdigest()


    print 'sign_key = %s'%(sign_key)

    # 2.生成规范化uri
    canonical_uri = get_canonical_uri(path)

    print 'canonical_uri = %s'%(canonical_uri)

    # 3.生成规范化query string
    canonical_querystring = get_canonical_querystring(params)
    print 'canonical_querystring = %s'%(canonical_querystring)

    # 4.生成规范化header
    canonical_headers = get_canonical_headers(headers, headers_to_sign)
    print 'canonical_headers = %s'%(canonical_headers)

    # 5.使用'\n'将HTTP METHOD和2、3、4中的结果连接起来，成为一个大字符串
    string_to_sign = '\n'.join(
        [http_method, canonical_uri, canonical_querystring, canonical_headers])

    print 'string_to_sign = %s'%(string_to_sign)

    # 6.使用5中生成的签名串和1中生成的sign key，用SHA-256算法生成签名结果
    sign_result = hmac.new(sign_key, string_to_sign, hashlib.sha256).hexdigest()

    # 7.拼接最终签名结果串
    if headers_to_sign:
        # 指定header to sign
        result = '%s/%s/%s' % (sign_key_info, ';'.join(headers_to_sign), sign_result)
    else:
        # 不指定header to sign情况下的默认签名结果串
        result = '%s//%s' % (sign_key_info, sign_result)

    return result

#简化的签名算法
def simplify_sign(credentials, http_method, path, headers,timestamp=0,
                   expiration_in_seconds=1800, headers_to_sign=None):
    headers = headers or {}

    # 1.生成sign key
    # 1.1.生成auth-string，格式为：yff-openapi-sign/{accessKeyId}/{timestamp}/{expirationPeriodInSeconds}
    sign_key_info = AUTH_STRING_PREFIX + '/%s/%d/%d' % (
        credentials.access_key_id,
        timestamp,
        expiration_in_seconds)

    print 'auth-string = %s,accessKeyId = %s,secret_access_key = %s'%(sign_key_info,credentials.access_key_id,credentials.secret_access_key)

    # 1.2.使用auth-string加上SK，用SHA-256生成sign key
    sign_key = hmac.new(
        credentials.secret_access_key,
        sign_key_info,
        hashlib.sha256).hexdigest()


    print 'sign_key = %s'%(sign_key)

    # 2.生成规范化uri
    canonical_uri = get_canonical_uri(path)

    print 'canonical_uri = %s'%(canonical_uri)

    # 3.生成规范化header
    canonical_headers = get_canonical_headers(headers, headers_to_sign)
    print 'canonical_headers = %s'%(canonical_headers)

    # 5.使用'\n'将HTTP METHOD和2、3、4中的结果连接起来，成为一个大字符串
    string_to_sign = '\n'.join(
        [http_method, canonical_uri,canonical_headers])

    print 'string_to_sign = %s'%(string_to_sign)

    # 6.使用5中生成的签名串和1中生成的sign key，用SHA-256算法生成签名结果
    sign_result = hmac.new(sign_key, string_to_sign, hashlib.sha256).hexdigest()

    # 7.拼接最终签名结果串
    if headers_to_sign:
        # 指定header to sign
        result = '%s/%s/%s' % (sign_key_info, ';'.join(headers_to_sign), sign_result)
    else:
        # 不指定header to sign情况下的默认签名结果串
        result = '%s//%s' % (sign_key_info, sign_result)

    return result

def pkcs7padding(data):
    bs = AES.block_size
    padding = bs - len(data) % bs
    padding_text = chr(padding) * padding
    return data + padding_text

def pkcs7unpadding(data):
    lengt = len(data)
    unpadding = ord(data[lengt - 1])
    return data[0:lengt-unpadding]

def convert_hex_to_string(hex_string):
    string = ''
    for pos in range(0, len(hex_string), 2) :
        string += str(chr(int(hex_string[pos:pos+2], 16)))
    return string

def aes_encrypt(data):
    skf = file(R'D:\project\auto_interface\antoInterfacePlatform\main\common\svrkey.json', 'r')
    skj = json.load(skf)
    svr_key_str = skj['key']
    svr_iv_str = convert_hex_to_string(skj['iv'])

    svr_aes_256_cbc = AES.new(svr_key_str, AES.MODE_CBC, svr_iv_str)
    data = pkcs7padding(data)
    data = svr_aes_256_cbc.encrypt(data)
    data = base64.b64encode(data)
    return data

def aes_decrypt(data):
    skf = file(r'D:\project\auto_interface\antoInterfacePlatform\main\common\svrkey.json', 'r')
    skj = json.load(skf)
    svr_key_str = skj['key']
    svr_iv_str = convert_hex_to_string(skj['iv'])

    svr_aes_256_cbc = AES.new(svr_key_str, AES.MODE_CBC, svr_iv_str)
    data = base64.decodestring(data)
    data = svr_aes_256_cbc.decrypt(data)
    data = pkcs7unpadding(data)
    return data

def process(jsonFile):

    # dev
    #url = 'http://10.9.19.192:16888'

    # qa
    #url = 'http://139.196.177.217:16888'
    url = 'http://openapi-qa.youyu.cn'

    requestFile = jsonFile
    requestFile = file(requestFile, 'r')
    requestFile = json.load(requestFile)
    key_id = requestFile['key_id']
    secret_key = requestFile['secret_key'].encode("utf-8")
    inputUri = requestFile['inputUri']
    http_method = requestFile['http_method'].upper()
    body = requestFile.get('body')
    queryUrl = url + inputUri

    params = {}
    if inputUri.find('?') != -1:
        path, paramString = inputUri.split('?')
        paramsList = paramString.split('&')
        for item in paramsList:
            k,v = item.split('=')
            params[k]=v
    else:
        path = inputUri

    headers = {
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
            }
    headersOpt = {'X-Requested-With','User-Agent','Accept'}

    timestamp = int(time.time())
    credentials = BceCredentials(key_id, secret_key)
    #result = normal_sign(credentials, http_method, path, headers, params, timestamp, 300, headersOpt)
    result = simplify_sign(credentials, http_method, path, headers, timestamp, 300, headersOpt)

    # enable/disable auth
    headers['Authorization'] = result

    # enable/disable en/decrypt
    headers['X-encryptflag'] = '1'

    if headers.get('X-encryptflag') == '1' and body:
        print 'body before encrypted: '
        print body
        body = aes_encrypt(body)

    print
    print 'queryUrl: '
    print queryUrl
    print 'body: '
    print body
    print 'headers: '
    print headers

    req = urllib2.Request(queryUrl, body, headers)
    response = urllib2.urlopen(req)
    resp = response.read()

    if headers.get('X-encryptflag') != '1':
        print 'response: '
    else:
        print 'response before decrypt: '
        print resp
        resp = aes_decrypt(resp)
        print('response: ')

    try:
        respDict = json.loads(resp)
        print(json.dumps(respDict, ensure_ascii=False, sort_keys=True, indent=4))
    except:
        print(resp)

if __name__ == "__main__":
    '''
    if 2 > len(sys.argv):
        print "usage: python authService.py query_trade_funddetail.json query_trade_historyorderdetail.json query_trade_historyorder.json query_trade_spotrate.json query_trade_stockposition.json query_trade_todaydeliver.json query_trade_todayorderdetail.json query_trade_todayorder.json"
        sys.exit()

    inputJsonFiles = sys.argv[1:]
    for jsonFile in inputJsonFiles :
        print "------------------"
        process(jsonFile)
    '''

    process(r"C:\Users\nan.wei\Desktop\OpenApi\QA_BUSINESS_TDY\query_trade_funddetail.json")
    #process(r"C:\Users\nan.wei\Desktop\OpenApi\QA_BUSINESS_TDY\query_trade_todaydeliver.json")
    #process(r"C:\Users\nan.wei\Desktop\OpenApi\QA_BUSINESS_TDY\query_trade_spotrate.json")
    #process(r"C:\Users\nan.wei\Desktop\OpenApi\QA_BUSINESS_TDY\query_trade_neworder.json")
