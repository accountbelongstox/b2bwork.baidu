git config --global user.email "accountbelongstox@163.com"
git config --global user.name "accountbelongstox"
git add .
git branch -M 'master'
git commit -m "new amend"
rem git remote add gitee git@gitee.com:accountbelongstox/b2bwork.baidu.git
ssh -T git@gitee.com
git push -u gitee master
rem git remote add github git@github.com:accountbelongstox/b2bwork.baidu.git
git branch -M 'main'
git commit -m "new amend"
ssh -T git@github.com
git push -u github main
cmd