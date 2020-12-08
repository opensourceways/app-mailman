import os
import sys
from mailmanclient import Client

# This file used to create the default domain, list and welcome templates for mail list
# the configuration are listed below:
MAILMAN_CORE_ENDPOINT = os.environ.get("MAILMAN_CORE_ENDPOINT", 'https://api.osinfra.cn/mailman/3.1')

MAILMAN_CORE_USER = os.environ.get("MAILMAN_CORE_USER", "restadmin")

MAILMAN_CORE_PASSWORD = os.environ.get("MAILMAN_CORE_PASSWORD", "")

# configure used for http server for mailman core service
TEMPLATE_FOLDER_PATH = os.environ.get("TEMPLATE_FOLDER_PATH", "templates")


def prepare_code():
    ret = os.system('which git')
    if ret == 0:
        if os.path.exists(os.path.join(os.getcwd(), 'app-mailman')):
            os.system('cd app-mailman;'
                      'git remote set-url origin https://github.com/opensourceways/app-mailman.git;'
                      'git pull')
        else:
            os.system('git clone https://github.com/opensourceways/app-mailman.git;')
    else:
        print('Git is not installed on this machine. Please install git first.')
        sys.exit(1)


def prepare_list():
    # pre-check before handling mailman core service
    templates_path = os.path.join(os.getcwd(), 'app-mailman/mail', TEMPLATE_FOLDER_PATH)
    if not os.path.exists(templates_path):
        print("The template file folder 'TEMPLATE_FOLDER_PATH' must exits on local.")
        sys.exit(1)
    if not MAILMAN_CORE_PASSWORD:
        print("MAILMAN_CORE_PASSWORD required to login.")
        sys.exit(1)
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
                    print('set common template'
                          'domain:{} \r\n'
                          'template name:{} \r\n'
                          'uri:{}'.format(template_name, os.path.abspath(txt_file), uri))
                except Exception as e:
                    print(e)
                    sys.exit(1)

        existing_lists = domain.lists
        list_dirs = os.listdir(os.path.join(templates_path, domain.mail_host))
        list_dirs.remove('common')
        for list_dir in list_dirs:
            if list_dir not in existing_lists:
                domain.create_list(list_dir)
                print('create list \r\n'
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
                    print('set list template \r\n'
                          'list: {} \r\n'
                          'template name: {} \r\n '
                          'uri: {}'.format(maillist, os.path.abspath(file), uri))
                except Exception as e:
                    print(e)
                    sys.exit(1)
            templates = maillist.templates
            for template in templates:
                if (template.name.replace(':', '-') + '.txt') not in list_text_dirs:
                    maillist.set_template(template.name, '')
                    print('remove list template \r\n'
                          'list: {} \r\n'
                          'template name: {}'.format(maillist.list_name, template.name))


if __name__ == "__main__":
    prepare_code()
    prepare_list()

