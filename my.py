import re, requests, urllib.parse

def remove_html_tags(text):
    clean = re.compile('<.*?>', re.S)
    return re.sub(clean, '', text)

def get_url(keys, curPage=1):
    keys = urllib.parse.quote(keys)
    url = 'https://v.qq.com/x/search/?q=%s&cur=%d' % (keys, curPage)
    print(url)
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.68"
    }
    r = requests.get(url=url, headers=head)
    r.encoding='utf-8'
    #print(html)
    pages = re.search(r'pages:\s*?(\d+?);.*?totalNum:', r.text, re.S)[1]
    #print(pages)
    rArr = re.findall(
	r'<h2 class="result_title"[^>]*?>[^<]*?<a href="([^"]+?)"[^>]*?>(.*?)</a>[^<]*?</h2>',
        r.text, re.S)

    return (rArr, pages)

if __name__ == '__main__':
    rArr, pages = get_url('黑土无言')
    for arr in rArr:
        url = arr[0]
        title = remove_html_tags(arr[1]).strip()
        print(url, title)
