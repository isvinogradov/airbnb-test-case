# coding: utf-8
import os
import re
import simplejson as json
from datetime import datetime

from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line
from tornado.web import RequestHandler, Application, StaticFileHandler
import psycopg2
import momoko

from decorators import validate


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db
        
    @coroutine
    def prepare(self):
        self.partner_id = self.get_argument('partner_id', None)
        if not self.partner_id:
            self.set_status(400)
            self.write('please specify partner_id')
            self.finish()
            return
            
        try:
            self.partner_id = int(self.partner_id)
        except ValueError:
            self.set_status(400)
            self.write('please specify an int')
            self.finish()
            return
        
        q = 'SELECT * FROM partners WHERE id = %s'
        cursor = yield self.db.execute(q, [self.partner_id])
        if not cursor.fetchone():
            self.set_status(400)
            self.write('specified partner does not exist')
            self.finish()
        
        
class WebClient(BaseHandler):
    def get(self):
        """ Веб-клиент """
        self.set_cookie('partner_id', str(self.partner_id))
        self.render('web-client.html')
        self.finish()

        
class Balance(BaseHandler):
    @coroutine
    def get(self):
        """ Получение информации об актуальном балансе на определённую дату / время """
        ts = self.get_argument('ts', None)
        if not ts:
            ts = datetime.now()
        else:
            try:
                ts = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                self.set_status(400)
                self.write('please specify a timestamp with ISO format: %Y-%m-%dT%H:%M:%S.%f')
                self.finish()
                return
        
        q = '''
            SELECT SUM(o.rur_amount) AS balance
            FROM operations o
            WHERE o.partner_id = %s AND o.ts <= TIMESTAMP %s
        '''
        cursor = yield self.db.execute(q, [self.partner_id, ts])
        
        res = cursor.fetchone()[0]
        self.write(str(0 if not res else res))
        self.finish()
        
        
class Operations(BaseHandler):
    validator_post = [
        {
            'parameter_name': 'val',
            'type': float,
            'min': -1000000,
            'max': 1000000,
            'required': True,
            'regex': r'^-?[0-9]\d*(\.\d{0,2})?$',
        },
        {
            'parameter_name': 'curr',
            'type': int,
            'min': 100,
            'max': 999,
            'required': False,
            'default': 643,
        },
    ]
    
    validator_get = [
        {
            'parameter_name': 'offset',
            'type': int,
            'required': False,
            'default': 0,
        },
        {
            'parameter_name': 'size',
            'type': int,
            'required': False,
            'default': 50,
            'min': 1,
            'max': 100
        },
    ]
    
    @coroutine
    @validate(validator_post)
    def post(self):
        """ Создание транзакции: пополнение баланса или списание суммы за покупку """
        q_rate = 'SELECT rur_exchange_rate FROM currencies WHERE code = %s'
        cursor = yield self.db.execute(q_rate, [self.curr])
        exchange_rate = cursor.fetchone()
        if exchange_rate:
            exchange_rate = exchange_rate[0]
        else:
            self.set_status(400)
            self.write('please specify a valid currency code')
            self.finish()
            return
        
        q = '''
            INSERT INTO operations
            (op_val, partner_id, curr_code, rur_exc_rate, rur_amount)
            SELECT %s, %s, code, rur_exchange_rate, %s*rur_exchange_rate
            FROM currencies
            WHERE code = %s
            RETURNING id
        ''' 
        # вставляем данные сразу с посчитанным курсом и рублёвым эквивалентом, 
        # чтобы запрос баланса работал максимально быстро
        cursor = yield self.db.execute(q, [self.val, self.partner_id, self.val, self.curr])

        self.write(str(cursor.fetchone()[0]))
        self.finish()
        
    @coroutine
    @validate(validator_get)
    def get(self):
        """ Получение истории транзакций по партнёру """
        q = '''
            SELECT 
                o.op_val, 
                o.curr_code, 
                o.rur_exc_rate * o.op_val AS rur_val, 
                to_char(o.ts, 'DD.MM.YYYY HH24:MI:SS')
            FROM operations o
            WHERE o.partner_id = %s
            ORDER BY o.ts DESC
            LIMIT %s OFFSET %s
        '''
        cursor = yield self.db.execute(q, [self.partner_id, self.size, self.offset])
        ops = cursor.fetchall()
        
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.write(json.dumps({
            'operations': [{'op_val': x[0], 'curr': x[1], 'rur_val': x[2], 'ts': x[3]} for x in ops]
        }, ensure_ascii=False))
        self.finish()



if __name__ == '__main__':
    dsn = 'port=5432;user=ivan;database=ivan;host=localhost;password=3WUV497DT7G305AE'
    
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_PATH = os.path.join(CURRENT_PATH, 'templates')
    STATIC_PATH = os.path.join(CURRENT_PATH, 'static')
    
    parse_command_line()
    application = Application([
        (r'/web', WebClient), # GET
        (r'/balance', Balance), # GET
        (r'/operations', Operations), # GET, POST
        (r"/static/(.*)", StaticFileHandler, dict(path=STATIC_PATH))
    ], debug=True, template_path=TEMPLATE_PATH, static_path=STATIC_PATH)
    
    ioloop = IOLoop.instance()
    application.db = momoko.Pool(dsn=dsn, size=4, ioloop=ioloop)

    future = application.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())
    ioloop.start()
    future.result()

    http_server = HTTPServer(application)
    http_server.listen(3008, 'localhost')
    ioloop.start()