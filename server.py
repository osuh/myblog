import socket
import os
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('server', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

HOST = "192.168.0.104"
PORT = 8080

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST,PORT))
listen_socket.listen(5)

print("Serving HTTP on port {}".format(PORT))


def handle_request(request):
    temp_request = request.decode()
    temp_args = temp_request.split(' ')
    
    response = ""

    http_response = """\
HTTP/1.1 200 OK
Content-type: {}

"""
    if not temp_args:
        return http_response
    
    if temp_args[1] == '/':
        template = env.get_template('index.html')
        
        url = os.path.abspath('articles')      
        list_articles = []
        for x in os.listdir(url):
            x = x.replace('.article', '')
            list_articles.append(x)

        response += template.render(articles = list_articles)

        return http_response.format('text/html') + response
    elif temp_args[1][-3:] == 'css':
        for w in open(temp_args[1][1:]):
            response += w

        return http_response.format('text/css') + response
    else:
        url = os.path.abspath('articles')
        article_name = temp_args[1][1:]
        url = url+'\\'+article_name+'.article'
        if os.path.isfile(url):
            template = env.get_template('article.html')
            content = ""
            with open(url) as fp:
                line = fp.readline()
                while line:
                    content += '<p>{}</p>\n'.format(line)
                    line = fp.readline()
                fp.close()

            response += template.render(content = content, title = article_name)

        return http_response + response


while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    
    http_response = handle_request(request)
    
    print('Got connection by {}'.format(client_address))

    client_connection.sendall(http_response.encode())
    client_connection.close()