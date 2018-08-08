try:
     ...:     npfile = './74849_accs_not_processed'
     ...:     fp2 = open(npfile, 'w')
     ...:     for a in acc_sum_list:
     ...:         aid = list(a.keys())[0]
     ...:         pos =  list(a.values())[0]['positions']
     ...:         try:
     ...:             for p in pos:
     ...:                 tran_data = {'accountId': '', 'amount': '', 'asset': '', 'operationType': 'FUNDING/WITHDRAWAL', 'price': None, 'symbo
     ...: lId': None, 'useAutoCashConversion': 'false'}
     ...:                 tran_data['accountId'] = aid
     ...:                 if p['type'] == 'CURRENCY':
     ...:                     tran_data['amount'] = str(-float(p['value']))
     ...:                     tran_data['asset'] = p['currency']
     ...:                 else:
     ...:                     tran_data['amount'] = str(-float(p['quantity']))
     ...:                     tran_data['asset'] = p['symbolId']
     ...:                     tran_data['symbolId'] = p['symbolId']
     ...:             r1 = bo.transaction_post(tran_data)
     ...:             if r1.status_code > 204:
     ...:                 fp2.write(aid + '\n')
     ...:             r2 = bo.account_archive(aid)
     ...:             if r2.status_code > 204:
     ...:                 fp2.write(aid + '\n')
     ...:             else:
     ...:                 print(aid, 'archived')            
     ...:         except:
     ...:             fp2.write(aid + '\n')
     ...: except KeyboardInterrupt:
     ...:     fp2.write(aid + '\n')
     ...:     fp2.close()
     ...: fp2.close()