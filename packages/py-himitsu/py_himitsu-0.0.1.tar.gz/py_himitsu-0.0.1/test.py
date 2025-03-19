from himitsu import query
from himitsu import client

print(str(query.parse_str("a=b c!=d")))

c = client.connect()

results = c.query(client.Operation.QUERY, "", client.Flag.DECRYPT)
for r in results:
    print(str(r))
