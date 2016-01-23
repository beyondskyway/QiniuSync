# QiniuSync
七牛同步工具（windows）:多文件夹实时同步到七牛

## Dependencies
* [pywin32](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/)
* [watchdog](http://developer.qiniu.com/docs/v6/tools/qrsync.html)
* [七牛同步工具qrsync](https://github.com/gorakhargosh/watchdog)


## Configuration
* 七牛信息
```
QINIU_ACCESS_KEY = ''
QINIU_SECRET_KEY = ''
QINIU_BUCKET = ''
QINIU_DOMIAN = ''
```

* 监视路径（同步目录）
```
WATCH_PATH = ('E:/SkyDrive', 'E:/SkyWatcher', 'E:/Diagram')
```

* 过滤触发同步
```
FILE_FILTER = [r'(.*)/\.(.*)']
```
避免不需要上传的文件改动触发同步

* 过滤上传文件

可据需通过[gitignore.io](https://www.gitignore.io/)生成.qrsignore.txt，过滤不需要上传的文件。


## Run
`python run.py`

