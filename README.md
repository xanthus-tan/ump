#UMP自动化部署工具
##简介
  Unified management platform 简称UMP，是一款简单，模块化，低侵入的部署管理工具。
目前UMP具备节点管理，节点监控，应用发布，应用部署功能，用户可以通过开发模块拓展UMP。

UMP由三部分组成，客户端(ump-cli.py)，服务端(ump.py)，指标采集器(collector)。
UMP客户端，UMP服务端支持windows, unix-like环境部署。
被管节点目前支持开通SSH服务的Linux系统。
##支持的被管节点操作系统
Centos 6+

RHEL 6+

Ubuntu 14+

Debain 8+
##快速开始
###服务端部署
1. 安装Python3.7+
2. 安装依赖环境
   ```
   pip install flask
   pip install SQLAlchemy
   pip install paramiko
   ```
###客户端部署
1. 安装Python3.7+
2. 安装依赖环境
   ```
   pip install prettytable

   ```
##目录说明
##内置模块介绍
##模块扩展说明