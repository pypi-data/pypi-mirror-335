安装打包工具
```shell
py -m pip install --upgrade build
```

打包
```shell
py -m build
```

安装上传工具
```shell
py -m pip install --upgrade twine
```

上传
```shell
twine upload dist/*
# 查看详细过程
twine upload dist/* --verbose  
```