# msModelSlim
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)   ![License](https://img.shields.io/badge/license-Apache%202.0-blue)
## 介绍
&emsp;&emsp;MindStudio msModelSlim，昇腾模型压缩工具。 【Powered by MindStudio】

&emsp;&emsp;昇腾压缩加速工具，是一个以加速为目标、压缩为技术、昇腾为根本的亲和压缩工具。支持训练加速和推理加速，提供模型低秩分解、大模型量化和稀疏量化、权重压缩、异常值抑制等多种功能。昇腾AI模型开发用户可以灵活调用Python API接口以实现对模型性能调优，并支持导出多种模型格式，在昇腾AI处理器上运行。

## 特性清单
特性接口文档：[API入口](./docs/Python-API接口说明)

| 版本信息                                                               | 新增特性                                                                                                                                                                                                                                                                                                                                                                                                             |
|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [MindStudio_8.0](https://gitee.com/ascend/msit/tree/MindSudio_8.0) | [大模型量化](./msmodelslim/pytorch/llm_ptq)<br/>[大模型稀疏量化和权重压缩](./msmodelslim/pytorch/llm_sparsequant)<br/>[多模态模型量化](./msmodelslim/pytorch/multi_modal)<br/>[长序列压缩](./msmodelslim/pytorch/ra_compression)<br/>|

## 安装方式
### 环境及依赖
- 硬件环境请参见[《昇腾产品形态说明》](https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/quickstart/quickstart/quickstart_18_0002.html)<br>
- 昇腾NPU驱动、固件和CANN软件的安装方案参见[《安装方案》](https://www.hiascend.com/document/detail/zh/canncommercial/800/softwareinst/instg/instg_0002.html?Mode=PmIns&OS=Ubuntu&Software=cannToolKit)<br>
- 硬件配套的软件，包括PyTorch框架、torch_npu插件（使用本工具在NPU上做大模型量化时需要安装，在CPU上不需要），下载资源参见[《配套资源下载》](https://www.hiascend.com/developer/download/commercial/result?module=cann)



### 安装方式一：pip安装
&emsp;&emsp;该安装方式不依赖CANN包，python>=3.7版本，仅针对MindStudio_8.0及以后版本可用，可选pip源安装方式或whl包安装方式。具体步骤如下：
1. pip源安装方式：
    
2. whl包安装方式：
   - 下载对应版本whl包。版本与配套whl包关联如下：

       | MindStudio版本 | whl包链接                                      |
       |---------------|---------------------------------------------|
       | MindStudio_8.0 | [msmodelslim-8.0.1-py3-none-any.whl](./whl) |
   - 安装到Python环境
       ```
        pip install {whl包}
       ```

### 安装方式二：源码安装
#### 针对CANN 8.0.RC3及之前的版本安装方式
&emsp;&emsp;下载安装CANN，配置环境变量``PYTHONPATH``后即可使用msModelSlim。参考[安装CANN软件包](https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/softwareinst/instg/instg_0007.html?Mode=PmIns&OS=Ubuntu&Software=cannToolKit)<br><br>
&emsp;&emsp;**注意** ：8.0.RC2版本存在已知问题，使用modelslim调用接口时，部分功能存在异常。请使用msmodelslim调用。

#### 针对CANN 8.0.0及之后的版本安装方式：
1. 下载安装CANN8.0.0及之后的版本，可以参考[安装CANN软件包](https://www.hiascend.com/document/detail/zh/canncommercial/800/softwareinst/instg/instg_0008.html?Mode=PmIns&OS=Ubuntu&Software=cannToolKit)
2. 下载msModelSlim源码
    ```
    git clone https://gitee.com/ascend/msit.git
    ```

3. 进入到msit/msmodelslim的目录，运行安装脚本
    ```
    cd msit/msmodelslim
    bash install.sh
    ```
   
4. （可选）如需使用稀疏量化特性，还需要以下步骤
   - 进入python环境下的site_packages包管理路径
     ```
     cd {python环境路径}/site-packages/msmodelslim/pytorch/weight_compression/compress_graph/
     ```
   - 编译weight_compression组件
     ```
     bash build.sh {CANN包安装路径}/ascend-toolkit/latest
     ```
   - 上一步编译操作会得到bulid文件夹，给build文件夹相关权限
     ```
     chmod -R 550 build
     ```
     
#### CANN版本配套表
| tag          | 可支持的CANN版本（向前兼容） |
|--------------|------------------|
| [MindStudio_8.0](https://gitee.com/ascend/msit/tree/MindSudio_8.0) | 8.0.0            |
| 无需安装，CANN软件包自带msModelSlim源码| 8.0.RC3及以前版本     |

## Quick Start
&emsp;&emsp;快速开始请参考[量化及稀疏量化场景代码样例](./msmodelslim/pytorch/llm_ptq/量化及稀疏量化场景导入代码样例.md)。<br>
### 使用案例
&emsp;&emsp;提供了多种已验证的模型量化脚本，开发者可根据脚本说明，通过命令行直接生成，请参考[example](./example)。<br>
### 使用指南
&emsp;&emsp;提供了FA量化使用说明、低显存量化使用说明、W8A8/W8A16量化的精度调优、稀疏量化精度调优等，请参考[docs](./docs)。

## 分支维护策略
MindStudio msModelSlim 分支版本号命名规则如下：
- msModelSlim仓每年发布4个商发版本，分别对应一个release版本。（待补充例子）