`交易中，每个新高一点的低点，相对于起始低点，但不替换`
`效果结束，替换新低点`
# GoogleDriver Download url is:
    - https://chromedriver.storage.googleapis.com/index.html
    - https://registry.npmmirror.com/binary.html?path=chromedriver/
# 支持命令
    - 
# 依赖包
    - 已移到下面python包安装命令
## 安装openssl
    - mkdir -p /usr/tmp && cd /usr/tmp
    - wget https://www.openssl.org/source/openssl-1.1.1n.tar.gz
    - tar -zxvf openssl-1.1.1n.tar.gz
    - cd openssl-1.1.1n
    - make
    - make install
    - mv /usr/bin/openssl /usr/bin/openssl.bak
    - ln -sf /usr/local/openssl/bin/openssl /usr/bin/openssl
    - echo "/usr/local/openssl/lib" >> /etc/ld.so.conf
    - ldconfig -v
    - openssl version
# linux安装python
    - mkdir -p /usr/tmp && cd /usr/tmp
    - wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
    - tar -zxvf Python-3.10.4.tgz
    - cd Python-3.10.4
    - yum -y install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel zlib-devel
    - vim Modules/Setup
    - 修改行 line:210  # socket line above, and edit the OPENSSL variable:
    - 修改行 line:211  OPENSSL=/usr/local/openssl
    - 修改行 line:212  _ssl _ssl.c \
    - 修改行 line:213      -I$(OPENSSL)/include -L$(OPENSSL)/lib \
    - 修改行 line:214      -lssl -lcrypto
    - ./configure --enable-optimizations
    - make
    - make install
    - touch ~/.pip/pip.conf
    - vim ~/.pip/pip.conf
    - 添加行 [global]
    - 添加行 index-url=http://mirrors.aliyun.com/pypi/simple/
    - 添加行 [install]
    - 添加行 trusted-host=mirrors.aliyun.com
    - cd /www/项目名
    - python3.10 venv -m venv
    - . venv/bin/activate
# 依赖包
    - python3.10 -m  pip3.10 install --upgrade  pip3.10
    - pip3.10 install selenium
    - pip3.10 install redis
    - pip3.10 install requests
    - pip3.10 install pymongo
    - pip3.10 install beautifulsoup4
    - pip3.10 install cssselect
    - pip3.10 install lxml
    - pip3.10 install mimerender
    - pip3.10 install flask    
    - pip3.10 install twisted
    - tar -zxvf Python-3.10.4.tgz
# linux部署chrome，selenium
    - yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    - yum install mesa-libOSMesa-devel gnu-free-sans-fonts wqy-zenhei-fonts
    - google-chrome --version
    - cd /www/项目名
    - wget https://registry.npmmirror.com/-/binary/chromedriver/103.0.5060.134/chromedriver_linux64.zip
    - unzip chromedriver_linux64.zip
    - mv chromedriver chromedriver_linux64_v103.0.5060.134
    - chmod +x chromedriver_linux64_v103.0.5060.134
# 添加开机启动
    - cd /www/项目名
    - vim start.sh
    - 添加命令： nohup /www/项目名/venv/bin/python3.10 -u /www/项目名/main.py > /www/项目名/out.log 2>&1 &
# 添加开机启动
    - chmod +x start.sh
    - vim /etc/rc.local
    - 添加 /www/项目名/start.sh
    - ps -ef | grep bmgctl
    - bt后台设置nginx 域名端口映射(反向代理)

