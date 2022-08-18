import xmlrpc.client

url = 'http://127.0.0.1:8000/'
proxy = xmlrpc.client.ServerProxy(url)


if __name__ == '__main__':
    print(proxy.multifunction(1, 11, 'name', 'Bread'))
