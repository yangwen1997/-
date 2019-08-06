import re
from requests_html import HTMLSession

session = HTMLSession()
r = session.get('http://www.gsxt.gov.cn/index.html')

res = "".join(re.findall("<script>.*?</script>",r.html.html))
resp_js = "function getClearance(){" + res +"};"
resHtml = resp_js.replace("eval", "return").replace("<script>",'').replace("</script>",'')
r.html.render(resHtml)
print(r.html.html)

