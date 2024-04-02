import hashlib

def generate_url_id(url):
    """
    生成给定URL的哈希映射字符串。
    使用MD5哈希函数生成URL的哈希值。
    """
    # 将URL编码为UTF-8，MD5需要二进制数据作为输入
    url_encoded = url.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(url_encoded)
    # 返回MD5哈希值的十六进制表示形式
    return md5.hexdigest()