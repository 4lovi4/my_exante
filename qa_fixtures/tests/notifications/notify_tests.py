#!/usr/bin/env python3

from utils import utils 

GW_URL = 'http://web-platform2.test.zorg.sh:4080/{}'

TEST_USER1 = 'notifyX@me.me'
TEST_USER2 = 'notifyY@me.me'
TEST_ACC = 'NOT9000.TST'

INSTRUMENT = 'NOTIFY-STOCK.AUT'

class TestGW:
    

    def test_app_subscribe(self):
        
        assert True
    
    def test_app_data(self):

        assert True

class TestOrders:
    
    def test_order_cancel(self):
        
        assert True

    def test_order_fill(self):
        
        assert True


class TestPriceAlerts:

    def test_bid_excess_alert(self):
        
        assert True

    def test_bid_lessening_alert(self):

        assert True

    def test_ask_excess_alert(self):
        
        assert True

    def test_ask_lessening_alert(self):

        assert True

    def test_mid_excess_alert(self):
        
        assert True

    def test_mid_lessening_alert(self):

        assert True
