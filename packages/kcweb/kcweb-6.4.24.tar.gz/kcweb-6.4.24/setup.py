
# 打包上传 python setup.py sdist upload
# 打包并安装 python setup.py sdist install
# twine upload --repository-url https://test.pypi.org/legacy/ dist/* #上传到测试
# pip install --index-url https://pypi.org/simple/ kcweb   #安装测试服务上的kcweb pip3 install kcweb==4.12.4 -i https://pypi.org/simple/
# 安装 python setup.py install
#############################################  pip3.8 install kcweb==6.4.15 -i https://pypi.org/simple
import os,sys
from setuptools import setup, find_packages,Extension
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)
from kcweb import kcwebinfo
confkcw={}
confkcw['name']=kcwebinfo['name']                             #项目的名称 
confkcw['version']=kcwebinfo['version']							#项目版本
confkcw['description']=kcwebinfo['description']       #项目的简单描述
confkcw['long_description']=kcwebinfo['long_description']     #项目详细描述
confkcw['license']=kcwebinfo['license']                    #开源协议   mit开源
confkcw['url']=kcwebinfo['url']
confkcw['author']=kcwebinfo['author']  					 #名字
confkcw['author_email']=kcwebinfo['author_email'] 	     #邮件地址
confkcw['maintainer']=kcwebinfo['maintainer'] 						 #维护人员的名字
confkcw['maintainer_email']=kcwebinfo['maintainer_email']    #维护人员的邮件地址
def get_file(folder='./',lists=[]):
    lis=os.listdir(folder)
    for files in lis:
        if not os.path.isfile(folder+"/"+files):
            if files=='__pycache__' or files=='.git':
                pass
            else:
                lists.append(folder+"/"+files)
                get_file(folder+"/"+files,lists)
        else:
            pass
    return lists
b=get_file("kcweb",['kcweb'])
setup(
    name = confkcw["name"],
    version = confkcw["version"],
    keywords = "kcweb"+confkcw['version'],
    description = confkcw["description"],
    long_description = confkcw["long_description"],
    license = confkcw["license"],
    author = confkcw["author"],
    author_email = confkcw["author_email"],
    maintainer = confkcw["maintainer"],
    maintainer_email = confkcw["maintainer_email"],
    url=confkcw['url'],
    packages =  b,
    install_requires = ['kcw==2.6.6','PyMySQL==0.9.3','redis==3.3.8','python-dateutil==2.9.0','pymongo==3.10.0','Mako==1.3.6','six>=1.12.0','websockets==8.1'], #第三方包
    package_data = {
        '': ['*.html', '*.js','*.css','*.jpg','*.png','*.gif'],
    },
    entry_points = {
        'console_scripts':[
            'kcweb = kcweb.kcweb:cill_start'
        ]
    }
)