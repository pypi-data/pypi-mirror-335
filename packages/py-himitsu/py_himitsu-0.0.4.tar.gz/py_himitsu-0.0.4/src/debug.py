from himitsu import client
from himitsu import query

c = client.connect()

c.delete("proto=secretservice", strict=False)

c.add("proto=secretservice collection=asdf4")
c.add("proto=secretservice collection=asdf4 attrxxx=lol")

results = c.query("proto=secretservice")
for r in results:
    print(str(r))

c.delete("proto=secretservice", strict=False)
print(c.status())
