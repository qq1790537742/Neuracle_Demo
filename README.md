# 脑机接口大赛在线系统

该系统分为三个子系统：刺激系统、采集系统、算法系统

该系统使用Kafka消息中间件作为通信平台，Kafka部署可按照相关部署文档进行

## 安装依赖

> 最新Psychopy环境安装（基于Python3.8）

下载网址（Psychopy Github）：

https://github.com/psychopy/psychopy/releases

windows系统选择2022.1.1-win64.exe下载

![image-20220228144442782](C:\Users\Xrl\AppData\Roaming\Typora\typora-user-images\image-20220228144442782.png)

下载后运行安装即可，安装路径为==C:\Program Files\PsychoPy==

>  confluent-kafka安装（pip install confluent-kafka）

confluent-kafka是python端调用Kafka接口所需要的第三方依赖，可以使用IDE直接安装或者使用pip install安装

confluent-kafka的版本应该在1.5.0以上

> EEGPlatformCommunicationModule安装

EEGPlatformCommunicationModule是我们封装的Kafka接口，我们将调用该模块封装的接口来创建topic、生产消息和消费消息。

在2022BCICompetitionSystemOnline目录下存在一个名为EEGPlatformCommunicationModule4py-package的目录，将使用该目录下的setup.py文件安装该依赖

- 右键开始菜单，以管理员身份运行power shell
- cd到setup.py所在的目录下

```bash
# 该路径为EEGPlatformCommunicationModule4py-package的绝对路径
# 例如：
cd C:\Users\Xrl\Desktop\2022BCICompetitionSystemOnline\EEGPlatformCommunicationModule4py-package
```

- 使用python setup.py develop安装EEGPlatformCommunicationModule依赖

```bash
# 为当前python环境安装该依赖
python setup.py develop
# 为Psychopy的python3.8环境安装该依赖（使用Python的绝对地址安装）
&'C:\Program Files\PsychoPy\python.exe' setup.py develop
```

> 其他模块安装

使用到的其他第三方依赖使用pip install或者IDE直接安装即可

## 子系统介绍

### create-topic.py

该.py文件用于在Kafka服务端创建topic，在实验开始前应先运行该.py文件创建topic

内部的topic_list为要创建的所有topic名称

### StimulationSystem（刺激子系统）

该刺激子系统为40目标SSVEP在线系统demo，各出题单位可以借鉴该在线系统编写相应赛题的刺激。

使用者可以运行StimulationMain.py来运行该刺激系统。

> communication通信模块说明

- config下为通信模块的配置文件
  - consumer-config.json为Kafka消费者所使用的配置文件
  - Initial-config.json为在Kafka服务端创建topic时使用的配置文件
  - producer-config.json为Kafka生产者所使用的配置文件
- CommunicationConsumer实例化后得到Kafka消费者对象，所需传入的参数：
  - topic：消费者订阅的topic名称
  - event_mng：事件管理器，用来处理消费者接收到的消息
- CommunicationProducer实例化后得到Kafka生产者对象，所需传入的参数：
  - topic：生产者发送消息的topic名称

> config配置文件目录说明

该目录下是trigger的配置文件，详细的trigger使用说明可参考trigger目录下的readme.md文件

> event事件目录说明

该目录下是事件管理器的代码实现，主要用来处理消费者接收到的消息

> log目录说明

该目录下是刺激系统产生的日志文件，使用者可以通过查看日志来调试代码

> paradigm范式目录说明

- config目录下是SSVEP刺激的配置文件
- SSVEP.py：40目标SSVEP刺激范式，出题单位主要需要借鉴该.py文件编写自己赛题的刺激范式

> stimulation_generate刺激生成目录说明

该目录下是40目标SSVEP刺激图片，使用者可以将需要使用的刺激内容放在该目录下

> trigger目录

该目录下是trigger控制模块，对于trigger的详细描述，使用者可以查看该目录下的readme.md文件

### ReceiverSystem（采集子系统）

为保证本次脑机接口大赛使用相同的采集设备，期望出题单位在采集脑电数据时使用Neuracle64导脑电放大器、Neuracle485trigger设备以及相应的Neuracle485软件进行数据采集。

==采集系统启动前请检查所有配置文件中的设置是否正确==

运行ReceiverMain.py运行采集系统

> communication通信模块说明

- config下为通信模块的配置文件
  - consumer-config.json为Kafka消费者所使用的配置文件
  - Initial-config.json为在Kafka服务端创建topic时使用的配置文件
  - producer-config.json为Kafka生产者所使用的配置文件

> DeviceModule采集模块说明

- NeuracleEEG.json采集配置文件

```java
{
  "device_name": "Neuracle",  //采集设备名称
  "hostname": "127.0.0.1",    //博睿康采集软件所在主机的ip地址，127.0.0.1为本机地址
  "port": 8712,               //博睿康采集软件发送数据的端口号
  "srate": 1000,              //博睿康采集软件设定的采样率
  "n_chan": 65,               //脑电数据导联数（64导数据+1导trigger）
  "time_buffer":0.04          //单个数据包时长（s）
}
```

> Log目录说明

该目录下是采集系统产生的日志文件，使用者可以通过查看日志来调试代码

### AlgorithmSystem（算法子系统）

运行AlgorithmSystemMain.py启动算法子系统

> AlgorithmImplement算法实现说明

该目录下保存有SSVEP经典算法CCA的实现，算法系统将调用AlgorithmImplementSSVEP中的run()方法来运行算法处理脑电数据。各出题单位可以借鉴该算法实现逻辑，实现自己赛题的标准算法

> communication通信模块说明

- config下为通信模块的配置文件
  - consumer-config.json为Kafka消费者所使用的配置文件
  - Initial-config.json为在Kafka服务端创建topic时使用的配置文件
  - producer-config.json为Kafka生产者所使用的配置文件
- CommunicationConsumer实例化后得到Kafka消费者对象，所需传入的参数：
  - topic：消费者订阅的topic名称
  - event_mng：事件管理器，用来处理消费者接收到的消息
- CommunicationProducer实例化后得到Kafka生产者对象，所需传入的参数：
  - topic：生产者发送消息的topic名称
- ReceiveEEGData实例化后得到接收脑电数据的对象（本质是Kafka消费者），所需传入参数：
  - topic：接收脑电数据需要订阅的topic名称
  - algo_sys_mng：算法系统管理者对象，将接收到的脑电数据传入其中
  - channel_num：采集子系统设置的脑电数据导联数
  - sample_num：采集子系统设置的采样率

> event事件目录说明

该目录下是事件管理器的代码实现，主要用来处理消费者接收到的消息

> Framework框架目录说明

该目录下是算法系统管理者的代码实现，其内部存在脑电数据的数据队列、评分程序等内容

> log目录说明

该目录下是算法系统产生的日志文件，使用者可以通过查看日志来调试代码

