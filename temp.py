#!/usr/bin/env python

s1 = so.get_from_http(id1, with_schedules=False)
s2 = so.get_from_http(id2, with_schedules=False)

doc1 = so.get(s1[0]['symbol']['_id'])
doc2 = so.get(s2[0]['symbol']['_id'])

doc2['content']['lotSize'] = doc1['content']['lotSize']
doc2['content']['brokers'] = doc1['content']['brokers']
doc2['content']['instantExecution'] = doc1['content']['instantExecution']
doc2['content']['feeds'] = doc1['content']['feeds']

so.update(doc2)


