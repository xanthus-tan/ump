# UMP自动化部署工具
## 简介
  Unified management platform 简称UMP，是一款简单，模块化，低侵入的部署管理工具。
目前UMP具备节点管理，节点监控，应用发布，应用部署功能，用户可以通过开发模块拓展UMP。

UMP由三部分组成，客户端(ump-cli.py)，服务端(ump.py)，指标采集器(collector)。
UMP客户端，UMP服务端支持windows, unix-like环境部署。
被管节点目前支持开通SSH服务的Linux系统。
## 支持的被管节点操作系统
Centos 6+

RHEL 6+

Ubuntu 14+

Debain 8+
## 快速开始

### 服务端部署
1. 安装Python3.7+
2. 安装依赖环境
   ```
   pip install flask
   pip install SQLAlchemy
   pip install paramiko
   ```
### 客户端部署
1. 安装Python3.7+
2. 安装依赖环境
   ```
   pip install prettytable

   ```
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
控制已经部署的服务
## 命令
### hosts模块
```
  ump-cli.py --module hosts --action get --group g1
  获取g1组的主机信息
  
  ump-cli.py --module hosts --action set --group g1 --address 192.168.72.130,192.168.72.132 --user xanthus --password 1
  创建组g1,同时注册节点192.168.72.130,192.168.72.132，用户名xanthus 密码1
  
  ump-cli.py --module hosts --action delete --group g1
  删除组g1以及该组的所有节点
  
  ump-cli.py --module hosts --action delete --group g1 --address 192.168.72.130
  删除组g1的192.168.72.130节点
```
### monitor模块
```
  ump-cli.py --module monitor --action set --group g1 --collector true --cpath /home/xanthus/ump/collector
  向组g1部署监控脚本，路径为/home/xanthus/ump/collector(第一步)
  
  ump-cli.py --module monitor --action set --group g1 --auto true --freq 5
  每5秒监控一次组g1下的节点
  
  ump-cli.py --module monitor --action set --group g1 --auto true --freq 5 --cpath /home/xanthus/ump/collector
  每5秒监控一次组g1下的节点, 监控脚本的路径是/home/xanthus/ump/collector
  
  ump-cli.py --module monitor --action get --group g1 --type status
  查看ump目前运行的监控任务
  
  ump-cli.py --module monitor --action get --group g1 --type metrics --cpath /home/xanthus/ump/collector
  查看组g1下所有节点的当前性能数据
  
  ump-cli.py --module monitor --action get --group g1 --cpath /home/xanthus/collector --type metrics
  查看组g1当前的性能数据，监控脚本路径是/home/xanthus/collector
  
  ump-cli.py --module monitor --action delete --jobid 5060cdf69b5f11ecb154a6fc7733a40b
  删除定制监控任务，任务id 5060cdf69b5f11ecb154a6fc7733a40b
```
### release模块
```
  ump-cli.py --module release --action set --name demo-app --tag 1.0 --src d:\demo-app.jar
  上传demo-app.jar包，名称为demo-app,标签为1.0
  
  ump-cli.py --module release --action get
  查看已经发布的所有app
  
  ump-cli.py --module release --action get --name demo-app
  查看已经发布的app名称为demp-app
  
  ump-cli.py --module release --action delete --name demo-app --tag 1.0
  删除指定的app
```
### deploy模块
```
  ump-cli.py --module deploy --action set --group g1 --name demo-deploy --app demo-app:1.0 --dest /tmp/
  创建一个部署，名称为demo-deploy。同时向组g1部署称为demo-app标签为1.0的app。节点路径为/tmp
  
  ump-cli.py --module deploy --action set --group g1 --name demo-deploy --app demo-app:1.0 --dest /tmp/ --args "-Xms512m -Xmx512m"
  创建一个部署，名称为demo-deploy。同时向组g1部署称为demo-app标签为1.0的app。节点路径为/tmp，参数为-Xms512m -Xmx512m
  
  ump-cli.py --module deploy --action get --name demo-deploy
  查看部署名称为demo-deploy的部署信息
  
  ump-cli.py --module deploy --action get --name demo-deploy --detail true
  查看部署名称为demo-deploy的细节信息
  
  ump-cli.py --module deploy --action get --name demo-deploy --history true
  查看部署名称为demo-deploy的历史信息
  
  ump-cli.py --module deploy --action delete --name demo-deploy
```
### service模块
```
  ump-cli.py --module instance --action get --deploy-name demo-deploy
  ump-cli.py --module instance --action set --deploy-name demo-deploy --control start
  ump-cli.py --module instance --action set --deploy-name demo-deploy --control stop
  ump-cli.py --module instance --action set --deploy-name demo-deploy --insid 70ff911003e511ed80aba4fc7733a40c --control start
  ump-cli.py --module instance --action set --deploy-name demo-deploy --insid 70ff911003e511ed80aba4fc7733a40c --control stop
```
## 目录说明

## 模块扩展说明