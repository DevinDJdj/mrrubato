#Ubuntu
import plyvel
#import leveldb

d = plyvel.DB('mydb/', create_if_missing=True)
#d = leveldb.DB('mydb', create_if_missing=True)
print(d.get(b'key'))

d.put(b'key', b'value')
#db.delete(b'key')
#'DB' object has no attribute 'iterator' why?


it = d.iterator(prefix=b'ke')
for key, value in it:
    print(key)

sn = d.snapshot()
#further action
#sn.get...
#my_sub_db = db.prefixed_db(b'example-'

d.close()
