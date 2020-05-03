# Termius Patches

用于Termius的一些补丁脚本。

## 介绍

* `font_patch.py`：用于设定终端中文字体
* `fix_bugs_*.py`：用于修复一些bug
* `add_features.py`：用于添加一些实用功能
* `set_sftp_local_home.py`：用于设置SFTP的本地主目录

## 使用方法
需要Python 3.6及以上环境，直接执行即可使用。目前仅支持在Windows下执行。

* `font_patch.py`使用交互式文本UI，可以重复执行；
* `fix_bugs_*.py`和`add_features.py`不需要交互，直接执行即可，不能重复执行；
* `set_sftp_local_home.py`接受一个参数，为要设置的主目录路径，支持中文，用法如：
  ```
  .\set_sftp_local_home.py D:\SomeFolder
  ```
  如果不给参数，则只打印当前的主目录值。

## 大致原理
Termius使用Electron框架，App的相关代码和资源大部分包含在`(安装目录)/resources/app.asar`中。`app.asar`是一个Electron ASAR格式的档案包，补丁脚本会在`app.asar`中读取要修改的文件，然后查找修改目标；修改完成后，脚本会将做出的改动更新到`app.asar`中。

## 注意事项
* 补丁操作开始执行之前，`app.asar`会被备份到当前的工作目录中，备份文件名为`app.asar.bak.(UNIX时间戳)`。如果补丁打完后需要撤销，可以用备份文件将`app.asar`重新覆盖回去。

* Termius更新后字体设置仍会有效，只要不需要更改设置就无需重打补丁。

## 备注

此系列补丁（包括`fix_bugs_*.py`中最新的）当前已测试过适用于Termius 5.9.2。

`add_features.py`加入的功能：

* 用`Termius.exe dev`启动时会打开开发人员工具；
* 在Hosts页输入label直接连接（不支持重复的label或空label的情况）；
* 在Hosts页输入框中按方向键下`↓`会自动定位至候选的第一项；
* 按Tab定位时会高亮显示选中的元素。

`fix_bugs_5.6.1.py`修复的bug：

* 重复处理的按键事件的bug（例如启用了^H退格时按一下退格发送两个^H）

`fix_bugs_5.1.1.py`修复的bug：

* 重复处理的按键事件的bug（例如启用了^H退格时按一下退格发送两个^H）
* 终端窗口Overflow的bug

`fix_bugs_5.0.6.py`修复的bug：

* 重复处理的按键事件的bug（例如启用了^H退格时按一下退格发送两个^H）
* Snippets相关快捷键不能设置的bug