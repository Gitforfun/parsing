import requests
# from pprint import pprint  # для диагностики
import json

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Authorization': 'Basic cG9zdG1hbjpwYXNzd29yZA=='}
addr = 'https://api.github.com/users/Gitforfun/repos'
json_data = 'data.json'


def scrap_rep(addrs, headrs):
    """
    не совсем ясно, зачем список записывать в формате json
    Пришлось генерировать ключ-имя для каждого имени репозитория
    """
    data_saving = {}
    req = requests.get(addrs, headers=headrs)
    data_loading = json.loads(req.text)
    i = 0
    for item in data_loading:
        i += 1
        data_saving |= {f'repos_name_{i}': f'{item["name"]}'}
    # pprint(data_saving)  # для диагностики
    with open(json_data, 'w') as outfile:
        json.dump(data_saving, outfile)


if __name__ == '__main__':
    scrap_rep(addr, headers)
