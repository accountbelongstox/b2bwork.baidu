git config --global user.email "accountbelongstox@163.com"
git config --global user.name "accountbelongstox"
git add .
git branch -M 'master'
git commit -m "new amend"
git remote add gitee git@gitee.com:accountbelongstox/b2bwork.baidu.git
git push -u gitee master
git remote add github git@github.com:accountbelongstox/b2bwork.baidu.git
git branch -M 'main'
git commit -m "new amend"
git push -u github main
cmd