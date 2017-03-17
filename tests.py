# -*- coding: utf-8 -*-
import unittest
import requests

class BaseTest(unittest.TestCase):
    base_url = 'http://localhost:3008'

class BalanceTest(BaseTest):
    def test_404(self):
        random_urls = [
            'index',
            'root',
            'admin',
            'wtf',
            '',
        ]
        for x in random_urls:
            r = requests.get(self.base_url + '/' + x)
            self.assertTrue(r.status_code == 404)
            r = requests.post(self.base_url + '/' + x)
            self.assertTrue(r.status_code == 404)
            r = requests.patch(self.base_url + '/' + x)
            self.assertTrue(r.status_code == 404)
            r = requests.put(self.base_url + '/' + x)
            self.assertTrue(r.status_code == 404)
        
    def test_balance(self):
        url = self.base_url + '/balance'
        
        r = requests.get(url)
        self.assertTrue(r.status_code == 400)
        
        r = requests.post(url + '?partner_id=1')
        self.assertTrue(r.status_code == 405)
        
        r = requests.get(url + '?partner_id=0')
        self.assertTrue(r.status_code == 400)
        
        r = requests.get(url + '?partner_id=600')
        self.assertTrue(r.status_code == 400)
        
        r = requests.get(url + '?partner_id=60jjjjjjj0')
        self.assertTrue(r.status_code == 400)
        
        r = requests.get(url + '?partner_id=1&ts=rrrrr')
        self.assertTrue(r.status_code == 400)
        
        r = requests.get(url + '?partner_id=1&ts=01.01.2017')
        self.assertTrue(r.status_code == 400)
        
        r = requests.get(url + '?partner_id=1&ts=2017-03-14T06:12:35.156154')
        self.assertTrue(r.status_code == 200)
        
    def test_post_op(self):
        url = self.base_url + '/operations'
        
        payload = {}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': 74372.04}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': 'sadfbadsh', 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': -234.54, 'partner_id': 'sdfbh'}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': -23400000.54, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        self.assertTrue(r.text == 'parameter «val» value is too small')
        
        payload = {'val': 10, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 200)
        
        payload = {'val': 0, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 200)
        
        payload = {'val': 5.04234123, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': 74372.04, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 200)
        
        payload = {'val': -234.54, 'partner_id': 1}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 200)
        
        payload = {'val': -234.54, 'partner_id': 1, 'curr': 'aaaa'}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': -234.54, 'partner_id': 1, 'curr': 222}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'val': -234.54, 'partner_id': 1, 'curr': 840}
        r = requests.post(url, data=payload)
        self.assertTrue(r.status_code == 200)
        
    def test_get_op(self):
        url = self.base_url + '/operations'
        
        payload = {}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 'f'}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 100000}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 1}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 200)
        self.assertTrue(len(r.json()) == 1)
        self.assertTrue(len(r.json()['operations']) == 50)
        
        payload = {'partner_id': 1, 'size': 0}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 1, 'size': 500}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 400)
        
        payload = {'partner_id': 1, 'size': 27}
        r = requests.get(url, data=payload)
        self.assertTrue(r.status_code == 200)
        self.assertTrue(len(r.json()) == 1)
        self.assertTrue(len(r.json()['operations']) == 27)
        
    def test_transaction(self):
        partner_id = 3
        operation_amount = -133.37
        
        r = requests.get(self.base_url + '/balance?partner_id=' + str(partner_id))
        balance_before = float(r.text)
        
        payload = {'val': operation_amount, 'partner_id': partner_id}
        r = requests.post(self.base_url + '/operations', data=payload)
        self.assertTrue(r.status_code == 200)
        
        payload = {'partner_id': partner_id, 'size': 1, 'offset': 0}
        r = requests.get(self.base_url + '/operations', data=payload)
        self.assertTrue(r.status_code == 200)
        self.assertTrue(len(r.json()) == 1)
        self.assertTrue(len(r.json()['operations']) == 1)
        self.assertTrue(r.json()['operations'][0]['op_val'] == operation_amount)
        
        r = requests.get(self.base_url + '/balance?partner_id=' + str(partner_id))
        balance_after = float(r.text)
        self.assertTrue(balance_after == balance_before + operation_amount)


if __name__ == '__main__':
	unittest.main()