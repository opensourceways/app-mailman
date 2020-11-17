## Mailman - list - set template

##### 获取Client对象 
```python
from mailmanclient import Client

client = Client('http://localhost:8001/3.1', 'restadmin', 'restpass')
```

##### 获取list对象
`list = client.get_list(fqdn_listname)`  --`fqdn_listname: 邮件列表的全称`

##### 设置list的模板
`list.set_template(template_name, template_url, username, password)`
