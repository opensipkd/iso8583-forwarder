from datetime import datetime
from common.bphtb.structure import (
    PAYMENT_CODE,
    TRANSACTION_BITS,
    )
from test_inquiry import (
    DbTransaction,
    TestInquiry,
    area_module,
    )


def payment_request(iso, inq_resp_iso):
    REQUEST_BITS = TRANSACTION_BITS.keys()
    for bit in (39, 70):
        i = REQUEST_BITS.index(bit)
        del REQUEST_BITS[i]
    iso.copy(REQUEST_BITS, inq_resp_iso)
    iso.set_transaction_code(PAYMENT_CODE)
    ntb = datetime.now().strftime('%Y%m%d%H%M%S')
    iso.set_ntb(ntb)


class TestPayment(TestInquiry):
    def run(self):
        resp_iso = TestInquiry.run(self)
        if not resp_iso.is_ok_response():
            return resp_iso, None
        print('Bank kirim payment request')
        req_iso = DbTransaction()
        req_iso.set_transaction_request()
        payment_request(req_iso, resp_iso)
        raw = self.get_raw(req_iso)
        print('Pemda terima payment request')
        from_iso = DbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim payment response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso, req_iso  # Untuk test_reversal.py


def main(argv):
    test = TestPayment(argv)
    test.run()
