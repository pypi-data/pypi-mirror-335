# sdk打包

[将自己的包上传到PyPi并可通过pip安装]<https://blog.csdn.net/yifengchaoran/article/details/113447773>

[pypi的2FA验证码]<https://blog.csdn.net/qq_39517117/article/details/138549900>

***不要用这个仓库里的sdk文件，使用最新的piper_sdk**

安装

```shell
pip install setuptools wheel twine
```

创建分发包

在项目根目录下，运行以下命令来创建源分发包和已构建分发包：

注意，如果需要对某个版本重复多次创建测试，将路径下的`piper_sdk.egg-info`、`dist`、`build`删掉后重新创建

版本在`setup.py`中的`version`参数修改

```shell
python3 setup.py sdist bdist_wheel
```

创建分发包后，可以从本地安装，版本自己看一下，我示例是`0.2.16`

```shell
pip3 install dist/piper_sdk-0.2.16-py3-none-any.whl
```

上传到 PyPI

首先，您需要在 PyPI 上创建一个帐户。如果没有帐户，请先注册并登录。

然后，使用 twine 工具上传包：

```shell
twine upload dist/*
```

上传需要输入pypi账号以及token，需要管理员将人员拉进来，然后生成一个上传token

上传的时候假设已经上传了0.0.6版本，但是发现0.0.6版本有问题在线上仓库删掉了，本地修改后重新提交的时候，还是会上传不上去，最好把版本号改一下

每次上传的时候，最好把创建分发包的那些`piper_sdk.egg-info`、`dist`、`build`文件删掉，重新创建一遍，有时候版本号不改而且也没删掉那些文件的话，上传的代码还是旧的

ps：pypi账号也需要验证器，只是需要输入代码如下：

XXX部分是创建账号后的一个验证的一串码，需要通过这个码来生成验证码，生成的验证码是4位的

```shell
import pyotp
totp = pyotp.TOTP('XXXXXXXXXXXXXXXXXXXXX')
print(totp.now())
```

安装在线包

上传后，可以使用 pip 安装您的包来测试：

```shell
pip install piper_sdk
```
