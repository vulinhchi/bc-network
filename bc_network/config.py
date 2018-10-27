
def transfer_queue(q1, q2):
    while list(q1.queue):
        q2.put(q1.get())

headers = {'content-type': 'application/json'}