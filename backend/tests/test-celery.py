#!/bin/env python3

import celery_tasks as ct
import time

with open('./1.pdb') as f:
    pdbtxt = f.read()

r1 = ct.request_process_tpprenum.delay(pdbtxt)
r2 = ct.request_process_tpprenum.delay(pdbtxt)
r3 = ct.request_process_tpprenum.delay(pdbtxt)

for i in range(15):
    time.sleep(0.5)
    print(r1.status, r2.status, r3.status)

print(r1.info)
# print(pdbtxt)


