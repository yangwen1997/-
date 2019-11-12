import cpca

location_str = ["  高阳县庞口农机市场南100米"]
df = cpca.transform(location_str)
pro = list(df['省'])
city = list(df['市'])
addr = list(df['地址'])
a = pro[0]
b = city[0]
c = addr[0]
print(a, b, c)
