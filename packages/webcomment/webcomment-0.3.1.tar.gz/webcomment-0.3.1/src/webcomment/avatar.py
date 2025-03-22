import re
import hashlib

QQ_MAIL = re.compile(r'^[1-9]\d{4,10}@qq.com$')


class AvatarConvertor:
    def __init__(self, **options):
        self.options = options

    def convert(self, email: str) -> str:
        gravatar_default = self.options.get('gravatar_default', 'robohash')
        if QQ_MAIL.match(email):
            qq_num = email.replace('@qq.com', '')
            return f'https://thirdqq.qlogo.cn/g?b=sdk&nk={qq_num}&s=140'
        else:
            email_md5 = hashlib.md5(email.encode('utf-8')).hexdigest()
            return f'https://www.gravatar.com/avatar/{email_md5}?s=400&d={gravatar_default}'
