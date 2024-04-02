# VAgent

## 测试代码
- To test react:

```bash
python test/test_react.py
```

- To test pipeline(workflow):
```bash
python test/test_pipeline.py
```
注意：现在pipeline的检索还没实现，需手动在`VAgent/engine/pipeline.py`里写workflow message来测试case

- To test web env,

```bash
python test/test_web.py
```

## 准备cookie以登录某网站页面
如需拿到登录账号后的网站的前端信息，可以:

- 在chrome浏览器页面登录后，右击 -> EditThisCookie -> 第一排第五个按钮（将cookie复制到剪切板）-> 贴在`assets/cookies/${website_name}.json`（能解决较多网站登录）
- 如果1不行，根据`test/test_login_web.py`，把cookie传到env的context里

## 环境依赖
- 如果遇到tesseract is not installed or it's not in your path, mac系统可以：
```bash
brew install tesseract
brew list tesseract
```
把安装后的tesseract路径(一般为`/opt/homebrew/bin/tesseract`)在代码中指定：
```python
tesseract_cmd = '/opt/homebrew/bin/tesseract'
```
具体可参考:(https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i)[https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i]

windows可参考:(https://blog.csdn.net/deletewo/article/details/127332027)[https://blog.csdn.net/deletewo/article/details/127332027]

## 全局config设置
assets/config.yml里有些需配置的文件和信息

## 更新日志
- **[2024/3/4]** 原子action space除去mouse scroll，取代为提前对页面scroll获取信息

