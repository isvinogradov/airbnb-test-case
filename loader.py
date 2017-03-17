import psycopg2
import random

x = psycopg2.connect(
    host='localhost', 
    user='ivan', 
    password='3WUV497DT7G305AE', 
    dbname='ivan'
)
c = x.cursor()

for i in range(500*1000):
    d = round(random.uniform(-5000, 5000), 2)
    crr = random.choice([643, 978, 826, 840])
    crr_d = {643: 1, 978: 62.49, 826: 71.46, 840: 58.24}
    q = '''
        INSERT INTO operations 
        (op_val, partner_id, curr_code, rur_exc_rate, rur_amount) 
        VALUES (%s, 1, %s, %s, %s)
    '''
    c.execute(q, [d, crr, crr_d[crr], d*crr_d[crr]])
    x.commit()

x.close()

