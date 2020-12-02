import os
import signal
import logging
from mailmanclient import Client
from http.server import SimpleHTTPRequestHandler, HTTPServer

# This file used to create the default domain, list and welcome templates
# for mail list
# the configuration are listed below:
MAILMAN_CORE_ENDPOINT = os.environ.get("MAILMAN_CORE_ENDPOINT", 'https://api.osinfra.cn/mailman/3.1')

MAILMAN_CORE_USER = os.environ.get("MAILMAN_CORE_USER", "restadmin")

MAILMAN_CORE_PASSWORD = os.environ.get("MAILMAN_CORE_PASSWORD", "restpass@osinfra")

DEFAULT_DOMAIN_NAME = os.environ.get("DEFAULT_DOMAIN_NAME", "openeuler.org")

DEFAULT_MAIL_LISTS = os.environ.get("DEFAULT_MAIL_LISTS", "dev,community,user")

# configure used for http server for mailman core service
TEMPLATE_FOLDER_PATH = os.environ.get("TEMPLATE_FOLDER_PATH", "templates")
TEMPLATE_SERVER_ADDRESS = os.environ.get("TEMPLATE_SERVER_ADDRESS",
                                         "127.0.0.1")
TEMPLATE_SERVER_PORT = os.environ.get("TEMPLATE_SERVER_PORT", 8000)

TEMPLATE_FOLDER_CONVERSION_EXCEPTION = {
    "domain-admin-notice-new-list": "domain:admin:notice:new-list",
    "list-user-notice-no-more-today": "list:user:notice:no-more-today",
}

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='./templates.log', level=logging.INFO, format=LOG_FORMAT)
page = 1


class TemplateHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        # Allow access for templates folder.
        if not str.lstrip(self.path, "/").startswith("templates"):
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(
                bytes("Only resource under templates folder are accessible!",
                      'UTF-8'))
        else:
            super(TemplateHandler, self).do_GET()


class SignalException(Exception):
    pass


def download_code():
    if os.path.exists(os.path.join(os.getcwd(), 'app-mailman')):
        os.system('cd app-mailman; git pull')
    else:
        os.system('git clone https://gitee.com/liuqi469227928/app-mailman.git;')


def prepare_list():
    # pre-check before handling mailman core service
    templates_path = os.path.join(os.getcwd(), 'app-mailman/mail', TEMPLATE_FOLDER_PATH)
    if not os.path.exists(templates_path):
        print("The template file folder 'TEMPLATE_FOLDER_PATH' must exits on local.")
        exit(1)
    client = Client(MAILMAN_CORE_ENDPOINT,
                    MAILMAN_CORE_USER,
                    MAILMAN_CORE_PASSWORD)
    domains = client.domains
    for domain in domains:
        common_path = os.path.join(templates_path, domain.mail_host, 'common')
        common_templates = list(filter(lambda x: x.endswith('.txt'), os.listdir(common_path)))
        if common_templates:
            for txt_file in common_templates:
                template_name = txt_file.rsplit('.txt')[0].replace('-', ':')
                uri = MAILMAN_CORE_ENDPOINT + os.path.abspath(txt_file)
                try:
                    domain.set_template(template_name, uri)
                    logging.info('set common template'
                                 'domain:{} \r\n'
                                 'template name:{} \r\n'
                                 'uri:{}'.format(template_name, os.path.abspath(txt_file), uri))
                    print('set common template'
                          'domain:{} \r\n'
                          'template name:{} \r\n'
                          'uri:{}'.format(template_name, os.path.abspath(txt_file), uri))
                except Exception as e:
                    logging.error(e)
                    exit(1)

        existing_lists = domain.lists
        list_dirs = os.listdir(os.path.join(templates_path, domain.mail_host))
        list_dirs.remove('common')
        for list_dir in list_dirs:
            if list_dir not in existing_lists:
                domain.create_list(list_dir)
                logging.info('create list \r\n'
                             'domain: {} \r\n'
                             'list: {}'.format(domain.mail_host, list_dir))

        for maillist in domain.lists:
            try:
                list_text_dirs = os.listdir(os.path.join(templates_path, domain.mail_host, maillist.list_name))
            except FileNotFoundError:
                continue
            list_text_dirs = list(filter(lambda x: x.endswith('.txt'), list_text_dirs))
            for file in list_text_dirs:
                template_name = file.rsplit('.txt')[0].replace('-', ':')
                uri = MAILMAN_CORE_ENDPOINT + os.path.abspath(file)
                try:
                    maillist.set_template(template_name, uri)
                    logging.info('set list template \r\n'
                                 'list: {} \r\n'
                                 'template name: {} \r\n '
                                 'uri: {}'.format(maillist, os.path.abspath(file), uri))
                    print('set list template \r\n'
                          'list: {} \r\n'
                          'template name: {} \r\n '
                          'uri: {}'.format(maillist, os.path.abspath(file), uri))
                except Exception as e:
                    logging.error(e)
                    exit(1)
            templates = maillist.templates
            for template in templates:
                if (template.name.replace(':', '-') + '.txt') not in list_text_dirs:
                    maillist.set_template(template.name, '')
                    logging.info('remove list template \r\n'
                                 'list: {} \r\n'
                                 'template name: {}'.format(maillist.list_name, template.name))
                    print('remove list template \r\n'
                          'list: {} \r\n'
                          'template name: {}'.format(maillist.list_name, template.name))


def httpd_signal_handler(signum, frame):
    print("signal received {0}, exiting".format(signum))
    raise SignalException()


def running_templates_server():
    httpd = HTTPServer((TEMPLATE_SERVER_ADDRESS, int(TEMPLATE_SERVER_PORT)),
                       TemplateHandler)
    # Force encoding to UTF-8
    m = SimpleHTTPRequestHandler.extensions_map
    m[''] = 'text/plain'
    m.update(dict([(k, v + ';charset=utf-8') for k, v in m.items()]))
    print("template server starts at {0}:{1}".format(TEMPLATE_SERVER_ADDRESS,
                                                     TEMPLATE_SERVER_PORT))
    try:
        # exit with 0 when sigterm signal received.
        signal.signal(signal.SIGTERM, httpd_signal_handler)
        httpd.serve_forever()
    except (InterruptedError, SignalException):
        pass
    print("template server ends")
    httpd.server_close()


if __name__ == "__main__":
    download_code()
    prepare_list()
    running_templates_server()

