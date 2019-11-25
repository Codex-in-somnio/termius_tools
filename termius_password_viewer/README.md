# Termius Password Viewer

查看Termius保存的密码的工具。

## 使用方法

先在`app`目录中执行`yarn install --prod`安装项目需要的Node模块。因为好像`npm`从Git拉取模块会出错，所以用`yarn`了。

然后将`app`目录复制到`%LocalAppData%\Programs\Termius\resources`下，运行Termius.exe即可看到此工具的画面。

使用完后，将`app`目录删除即可。

## 注意事项

* 不能和Termius同时运行；
* 不能同时启动多个实例。