This API can only query Chinese servers！！！

# ysinfo
原神个人信息查询hoshino集成U优化版

写这玩意的原因的方便直接拆穿网图装x的sb

希望米哈游官方人员看到了也别和谐(

# 用法

1. 在genshinuid.py文件头部添加自己的Cookie
2. 把文件夹放到hoshino的modules目录下
3. hoshino的配置文件添加'ysInfo'
4. 重启hoshino

##  获取Cookie方法


1. 浏览器**无痕模式**打开 [https://bbs.mihoyo.com/ys/](https://bbs.mihoyo.com/ys/) ，登录账号
2. 打开[https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie](https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie)，（这个在这里获取Cookie并不会触发`Debugger`，当然也可以忽略这个步骤）
3. 按`F12`，打开`开发者工具`，找到并点击`Network`
4. 按`F5`刷新页面，按下图复制 Cookie：

![How to get mys cookie](https://i.loli.net/2020/10/28/TMKC6lsnk4w5A8i.png)

当触发`Debugger`时，可尝试按`Ctrl + F8`关闭，然后再次刷新页面，最后复制 Cookie。也可以使用另一种方法：

1. 复制代码 `var cookie=document.cookie;var ask=confirm('Cookie:'+cookie+'\n\nDo you want to copy the cookie to the clipboard?');if(ask==true){copy(cookie);msg=cookie}else{msg='Cancel'}`
2. 浏览器**无痕模式**打开 [https://bbs.mihoyo.com/ys/](https://bbs.mihoyo.com/ys/) ，登录账号
3. 按`F12`，打开`开发者工具`，找到并点击`Console`
4. 控制台粘贴代码并运行，获得类似`Cookie:xxxxxx`的输出信息
5. `xxxxxx`部分即为所需复制的 Cookie，点击确定复制

