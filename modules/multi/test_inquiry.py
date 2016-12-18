from datetime import datetime
from pprint import pprint
from time import sleep
from optparse import OptionParser
from structure import (
    PBB_INQUIRY_CODE,
    BPHTB_INQUIRY_CODE,
    PADL_INQUIRY_CODE,
    )
import conf


INQUIRY_CODES = dict(
    pbb=PBB_INQUIRY_CODE,
    bphtb=BPHTB_INQUIRY_CODE,
    padl=PADL_INQUIRY_CODE)

name = '.'.join(['multi', conf.module_name])
module = __import__(name)
area_module = getattr(module, conf.module_name)
DbTransaction = area_module.DbTransaction


class Inquiry(DbTransaction):
    def inquiry_request(self, module_name, invoice_id, bank_id):
        inquiry_code = INQUIRY_CODES[module_name]
        self.set_transaction_request()
        kini = datetime.now()
        self.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
        self.set_transaction_code(inquiry_code) 
        self.setBit(12, kini.strftime('%H%M%S')) 
        self.setBit(13, kini.strftime('%m%d')) 
        self.setBit(15, kini.strftime('%m%d')) 
        self.setBit(18, '6010') 
        self.setBit(22, '021')
        self.setBit(32, bank_id)
        self.setBit(33, '00110')
        self.setBit(35, '')
        self.setBit(37, kini.strftime('%H%M%S')) 
        self.setBit(41, '000')
        self.setBit(42, '000000000000000')
        self.setBit(43, 'Nama Bank')
        self.setBit(49, '390')
        self.setBit(59, 'PAY')
        self.setBit(60, '142')
        self.setBit(61, invoice_id)
        self.setBit(63, '')
        self.setBit(102, '')
        self.setBit(107, '')


class Test(object):
    def get_raw(self, iso):
        msg = 'MTI {mti}'.format(mti=iso.getMTI())
        print(msg)
        pprint(iso.getBitsAndValues())
        raw = iso.getRawIso()
        sleep(1)
        print([raw])
        return raw


class TestInquiry(Test):
    def __init__(self, argv):
        self.option = get_option(argv)
        if not self.option:
            return
        self.module_name = self.option.module
        self.invoice_id = self.option.invoice_id
        streamer_name, bank_id = split_bank(self.option.bank)
        self.conf = dict(name=streamer_name, ip='127.0.0.1', bank_id=bank_id)

    def run(self):
        if not self.option:
            return
        print('Bank kirim inquiry request')
        req_iso = Inquiry()
        req_iso.inquiry_request(self.module_name, self.invoice_id,
            self.conf['bank_id'])
        raw = self.get_raw(req_iso)
        print('Pemda terima inquiry request')
        from_iso = DbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim inquiry response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso # Untuk test_payment.py


def get_option(argv):
    module_name = 'pbb'
    bank = 'btn'
    pars = OptionParser()
    help_module = 'default {m}'.format(m=module_name)
    help_bank = 'default {b}. Contoh lain: mitracomm,14 dimana 14 adalah BCA'.\
            format(b=bank)
    pars.add_option('-m', '--module', default=module_name, help=help_module)
    pars.add_option('-i', '--invoice-id')
    pars.add_option('-b', '--bank', default=bank, help=help_bank)
    option, remain = pars.parse_args(argv)
    if not option.invoice_id:
        print('--invoice-id harus diisi.')
        return
    return option

def split_bank(s):
    t = s.split(',')
    if t[1:]:
        streamer_name = t[0]
        bank_id = int(t[1])
    else:
        streamer_name = s 
        bank_id = 0 
    return streamer_name, bank_id

class MainProcess(object):
    def __init__(self, argv):
        self.option = get_option(argv)
        if not self.option:
            return
        streamer_name, bank_id = split_bank(self.option.bank)
        self.conf = dict(name=streamer_name, ip='127.0.0.1', bank_id=bank_id)

def main(argv):
    test = TestInquiry(argv)
    test.run()
