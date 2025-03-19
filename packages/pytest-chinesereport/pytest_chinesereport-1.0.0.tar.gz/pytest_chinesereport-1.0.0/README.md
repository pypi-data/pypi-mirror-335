# pytest-chinesereport

### 1、pytest-chinesereport介绍

pytest-chinesereport 是一个针对 pytest 生成中文版 html 报告的插件，基于 pytest-testreport 进行了优化及 bug 修复，安装好pytest-chinesereport之后，运行用例时加上参数即可生成报告

###### 注意点：如果安装了 pytest-html 这个插件，请先卸载，不然会有冲突
###### 注意点：如果安装了 pytest-testreport 这个插件，请先卸载，不然会有冲突

##### 使用案例：

- ###### 命令行执行： pytest 运行测试时加上参数--report 指定报告文件名

    ```shell
    # 指定报告文件名
    pytest --report=report.html
    
    #其他配置参数
    --title=指定报告标题
    --tester=指定报告中的测试者
    --desc = 指定报告中的项目描述
    
    # 同时使用多个参数
    pytest --report=report.html --title=测试报告 --tester=测试人员 --desc=项目描述
    ```
    
- ###### pytest.main执行

    ```shell
    import pytest
    
    pytest.main(['--report=report.html',
                 '--title=测试报告标题',
                 '--tester=测试人员',
                 '--desc=报告描述信息'])
    ```

    

### 2、安装pytest-chinesereport

pytest-chinesereport是基于python3.6开发的，安装前请确认你的python版本>3.6

安装命令

```pip install pytest-chinesereport```

### 3、使用文档：
https://unittestreport.readthedocs.io/en/latest/doc9_pytest/
### 备注：

- ##### 基于 pytest-testreport 进行 bug 修复及优化

