import unittest
from bot import Bot, BIO, DESCRIPTION, calculate, PROMPTS

class FakeBot(Bot):
    def __init__(self):
        super().__init__('fake'); self.calls=[]
    def api(self, method, **params):
        self.calls.append((method, params))
        return {'username':'Lotto_8888_BOT'} if method == 'getMe' else True

class Tests(unittest.TestCase):
    def test_percent(self):
        self.assertIn('= 30', calculate('percent','15 200'))
        self.assertIn('= 0.05', calculate('percent','0,5 10'))
        self.assertIn('= -30', calculate('percent','15 -200'))
    def test_fraction(self):
        self.assertIn('= 3/4', calculate('fraction','18 24'))
        self.assertIn('= -3/4', calculate('fraction','18 -24'))
        self.assertIn('= 0/1', calculate('fraction','0 -24'))
    def test_table(self):
        self.assertIn('8 × 12 = 96',calculate('table','8'))
    def test_bad_inputs(self):
        for tool, text in [('fraction','1 0'),('table','10001'),('percent','NaN 2'),('percent','1e9 2'),('fraction','1.2 2'),('percent','1')]:
            with self.assertRaises(ValueError): calculate(tool,text)
    def test_profile_and_flows(self):
        self.assertLessEqual(len(BIO),120); self.assertLessEqual(len(DESCRIPTION),512)
        bot=FakeBot(); bot.configure()
        for text in ['/start','/help','/privacy','/percent 15 200','/fraction 18 24','/table 8','/table','unknown']:
            bot.handle({'message':{'chat':{'id':1,'type':'private'},'text':text}})
        for tool,prompt in PROMPTS.items():
            bot.handle({'callback_query':{'id':'q','data':tool,'message':{'chat':{'id':1,'type':'private'}}}})
            bot.handle({'message':{'chat':{'id':1,'type':'private'},'text':'8' if tool=='table' else '18 24','reply_to_message':{'text':prompt}}})
        self.assertIn('8 × 12 = 96',bot.calls[-1][1]['text'])

if __name__=='__main__': unittest.main()
