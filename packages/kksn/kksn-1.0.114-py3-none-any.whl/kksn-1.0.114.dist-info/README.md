## 关于这个项目

**kksn** 是一款软件序列号生成器，它将用于在**windows**系统下打包**exe**时进行序列号管理、判断的一款工具。

通过为你的工具进行序列号管理，可以防止客户在使用过程中进行软件拷贝操作而造成的损失。

## 简洁操作
使用非常简单，仅需要在代码中进行如下操作：
```python
def main():
    # 这里编写你的工具代码
    pass


if __name__ == '__main__':
    Monitor(target=main, pwd='xxxxxx')
```

## 生成授权文件
当你的客户需要进行授权时，将复制工具生成的序列号，例如：**E8877A0ED06EC57CB9CA335EC3337983==A3F3AEF0-51EA-47DC-9EDA-63322EADDF5B**。

你可以通过**kksn_server.exe**程序为你的客户生成授权文件：
```python
kksn_server.exe -s E8877A0ED06EC57CB9CA335EC3337983==A3F3AEF0-51EA-47DC-9EDA-63322EADDF5B -p xxxxxx
```

## 关于作者
微信公众号：Python卡皮巴拉

🌟【Python卡皮巴拉】—— 你的Python修炼秘籍，代码界的“神兽”驾到！🌟
