# SmartPush_AutoTest



## Getting started

## 打包/上传的依赖
```
pip install wheel
pip install twine
```


## 打包-打包前记得修改版本号
```
python setup.py sdist bdist_wheel
```


## 上传到pipy的命令
```
twine upload dist/*
```

# 平台调用demo
```
import json # import 请置于行首
from smartpush.export.basic import ExcelExportChecker
from smartpush.export.basic import GetOssUrl
oss=GetOssUrl.get_oss_address_with_retry(vars['queryOssId'], "${em_host}", json.loads(requestHeaders))
result = ExcelExportChecker.check_excel_all(expected_oss=oss,actual_oss=vars['exportedOss'],ignore_sort =True)
assert result
```
## check_excel_all() 支持拓展参数
    1、check_type = "including"   如果需要预期结果包含可传  eg.联系人导出场景可用，flow导出场景配合使用
    2、ignore_sort = 0   如果需要忽略内部的行排序问题可传，eg.email热点点击数据导出无排序可用，传指定第几列，0是第一列
    3、ignore_sort_sheet_name = "url点击"   搭配ignore_sort使用，指定哪个sheet忽略排序，不传默认所有都排序，参数大小写不敏感(url点击-URL点击)
    4、skiprows = 1   传1可忽略第一行，   eg.如flow的导出可用，动态表头不固定时可以跳过读取第一行

## get_oss_address_with_retry(target_id, url, requestHeader, requestParam=None, is_import=False, **kwargs)
    1、is_import 导入校验是否成功传True,否则默认都是导出
    2、**kwargs 参数支持重试次数     
        tries = 30 # 重试次数
        delay = 2  # 延迟时间，单位s