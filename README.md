# UMP自动化部署工具
## 简介
  Unified management platform 简称UMP，是一款简单，模块化，低侵入的spring boot部署管理工具。
目前UMP具备节点管理，节点监控，应用发布，应用部署功能，用户可以通过开发模块拓展UMP。

UMP由三部分组成，客户端(ump-cli.py)，服务端(ump.py)，指标采集器(collector)。
UMP客户端，UMP服务端支持windows, unix-like环境部署。
被管节点目前支持开通SSH服务的Linux系统。
## 支持的被管节点操作系统
Centos 6+

RHEL 6+

Ubuntu 14+

Debain 8+

### 服务端部署
1. 安装Python3.7+
2. 安装依赖环境
   ```
   pip install flask
   pip install SQLAlchemy
   pip install paramiko
   ```
## 快速开始
ump.py start

## 内置模块介绍
### hosts模块
记录节点主机信息，相同IP地址主机可以重复注册，通过不同group来区分。
### monitor模块
节点监控模块，ump通过ssh协议抓取节点cpu，内存，硬盘指标存储到指定的elasticsarch库中(版本 7.6.2)
### release模块
ump内置的版本库，本地工程包上传到内置仓库中，并且打上标签。
### deploy模块
将已经release的工程包发布到指定的节点服务中
### instnace模块
控制已经部署的实例
