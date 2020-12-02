# README
**NOTE**: Please read the guidance below before you starting changing any content inside of this folder.

## Introduce
This files inside of this folder are used for replacing the default mailman core email templates when the mailman suite
services starts up, therefore these files are strictly arranged by the design of mailman templates mechanism.

There are many different template substitutions provided by mailman core service, please refer [here](https://mailman.readthedocs.io/en/latest/src/mailman/rest/docs/templates.html#templated-texts)
to have a better understanding on this. In short, mailman templates are classified with different keys, here below are some of
these template keys:
1. `domain:admin:notice:new-list`: Sent to the administrators of any newly created mailing list.
2. `list:user:action:subscribe`: The message sent to subscribers when a subscription confirmation is required.
3. `list:user:notice:welcome`: The notice sent to a member when they are subscribed to the mailing list.

For instance, if we require to update the `welcome` templates of `developing` list (on domain `example.com`), we need to update the list uris via
mailman core API:
```python
import requests
requests.patch('http://{host}:{port}/3.1/lists/developing.example.com/uris',
              {'list:user:notice:welcome': 'http://{http_path_which_store_template_file}'},
               auth=({username}, {password}))
```
## Customize templates for a list
1. Fork the repository https://github.com/opensourceways/app-mailman first.
2. By default, the mailing list will use the public template set in common directory. If you want to customize templates for a list, first find the domain of the maillist list under the templates directory, then find the list under the domain directory that you want to customize.
3. Put the template file under the list. You can write the file according to the common files. But the filename should follow the standard so that can resolve to a standard template name. e.g. if you want to customize the `list:user:notice:welcome` template, the file name must be `list-user-notice-welcome.txt`. See more about the template name, you can visit https://docs.mailman3.org/projects/mailman/en/latest/src/mailman/rest/docs/templates.html.
4. Create a pull request.Once the pull request be merged, the customised template will cover the common template. 

## Folder Structure
Mailman's `core-utils` will help us to setting up the http server and invoke mailman's core API to patch the template, in order to
achieve this automatically, the structure of folder `templates` are arranged below:

```$xslt
mail
├───────templates
│       ├───────domain1
│       │       ├───────common  
│       │       │       ├───────list-admin-action-post.txt
│       │       │       ├───────list-user-action-subscribe.txt
│       │       │       └───────list-user-notice-welcome.txt
│       │       ├───────list1
│       │       └───────list2
│       │               └───────list-user-notice-welcome.txt  
│       └───────domain2 

```
Once the content in templates folder have been updated, we can update the mailman templates through recreating the `core-utils` pods in cluster.

