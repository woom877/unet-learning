# Underwater Network

## 0. 前言

本文严格参考 [Underwater Networks Handbook](https://unetstack.net/handbook/unet-handbook.html)。

## 1. 准备环境

我这里使用的是 WSL 里的 Ubuntu 22.04.5 LTS，shell 是 fish 3.3.1。

### 1.1 Java

准备 Java8 环境，先安装 JDK：

```
sudo apt install openjdk-8-jre
```

因为我之前设置过 Java21 的环境，所以这里需要先修改一下环境，可以运行 `java -version` 来查看自己环境的 Java 版本。

运行下面几个命令来修改系统环境：

```
sudo update-alternatives --config java
sudo update-alternatives --config javac
sudo update-alternatives --config keytool
sudo update-alternatives --config jar
```

运行之后会让我们选择环境，如果已经是 Java8 就不需要动了，如果不是就需要手动输入 Java8 对应的编号。

接下来更新 fish 的环境变量：

```
set -Ux JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
# put JDK8 bin at the front so it wins
set -U fish_user_paths $JAVA_HOME/bin $fish_user_paths
```

运行一下 `java -version`，如果输出如下内容则表示环境配置完毕：

```
$ java -version
openjdk version "1.8.0_462"
OpenJDK Runtime Environment (build 1.8.0_462-8u462-ga~us1-0ubuntu2~22.04.2-b08)
OpenJDK 64-Bit Server VM (build 25.462-b08, mixed mode)
```

### 1.2 UnetStack

[下载](https://unetstack.net/#downloads)社区版的 UnetStack（后简称 Unet）组件。

## 2. 正式开始

### 2.1 第一次信息发射

接下来 `cd` 到 Unet 的目录下，尝试运行一下：

```
$ ./bin/unet ./samples/2-node-network.groovy

2-node network
--------------

Node A: tcp://localhost:1101, http://localhost:8081/
Node B: tcp://localhost:1102, http://localhost:8082/

```

这样就表示运行成功，看名字就能看出来这是一个由两个结点构成的仿真网络，打开浏览器访问后面的 URL 就可以访问两个节点了。

访问之后可以从浏览器的标签页上看到结点的地址，结点 A 的地址是 232，结点 B 的地址是 31。

接下来我们在浏览器里访问结点 A，在 Shell 里输入：

```
> tell 0, 'hello!'
AGREE
```

- `tell`：表示发送消息，用法为 `tell <ADDRESS:String>, <MESSAGE:int>`。
- `0`：地址为 `0` 表示广播。

看到 `AGREE` 说明我们上面的指令运行成功了。

然后转到结点 B，可以在 Shell 里看到：

```
[232]: hello
```

说明我们的 B 收到了来自地址 232（结点 A）的消息。

到这里我们已经成功的实现了两个节点之间的第一次通信。

Unet 会自动分配结点的地址，我们可以通过 `host()` 函数来获取结点的地址，比如：

```
> host('A')
232
> host('B')
31
```

使用方法为 `host(String node)`，需要注意的是，这里的节点名称是以字符串形式传输，而不是以变量形式，所以要加单引号。

接下来我们用 B 给 A 发个消息：

```
> tell 232, 'hi!'
AGREE
```

在 A 的 Shell 里收到了：

```
[31]: hi!
```

我们还可以直接这样：

```
> tell host('A'), 'hi!'
AGREE
```

是不是很熟悉，跟函数调用什么的用法完全一样。

### 2.2 传播延迟与测距

通信必然存在延迟，尤其是对于我们的水声通信，我们知道水中的声速约为 1500m/s（会受到温度、盐度、深度等因素影响），所以这个延迟要比我们日常使用的电磁波通信明显很多。

通过查看结点 A、B 的 Location 可知，两个结点的距离为 1km，信号大约需要 0.7s 的时间来传输。

除开直接查看，我们还可以通过通信的时延来计算大概的距离，在这里我们可以通过如下指令实现，在结点 A 的 Shell 里输入：

```
> range host('B')
999.99976
```

这里计算的就是 A 到 B 的距离，单位是 m，约等于我们所知道的 1km。

### 2.3 发送和接收应用数据

刚才我们已经尝试了发送简单的数据，比如一个简单的字符串，但是在实际应用中，我们经常会面临发送复杂数据的情况，在这种情况下，我们就可以使用 UnetSocket API。

我们先在结点 B 上打开一个 `UnetSocket`： 

```
> s = new UnetSocket(this);
```

- 这里的 `this` 用法跟 C++ 里的差不多，就是我们当前的对象（这里是结点 B），也就是说变量 `s` 绑定了一个在结点 B 上打开的 `UnetSocket`，末尾的 `;` 表示不需要打印返回值。

接下来我们需要获取接收到的信息：

```
> rx = s.receive()  
```

- 这里我们新建了一个变量 `rx` 用于监听 `s` 接收到的信息。

然后去到结点 A 去发送消息，也是先打开一个 `UnetSocket`：

```
> s = new UnetSocket(this);
```

然后调用 `send()` 函数发送消息：

```
> s.send('hello!' as byte[], 0)
true
```

- `s.send('hello!' as byte[], 0)`：可以看出 `send()` 函数的使用方法为 `send(byte[] message, int address)`，`Address` 为 `0` 依然表示广播，因为 `send()` 函数中的 `message` 为 `byte[]` 类型，而字符串默认为 `String` 类型。

返回 `true` 表示发送成功，其他节点将会以 `RxFrameNtf` 消息的形式收到我们发送的字节流。

现在可以用 `close()` 函数关闭我们刚才打开的 `UnetSocket`：

```
> s.close()
```

接下来我们打开结点 A 查看一下：

```
RxFrameNtf:INFORM[type:DATA from:232 rxTime:3958929428 rssi:112.4 (6 bytes)]
```

这说明我们成功接收到了刚才发送的数据，类型为 `DATA` 数据，发送方的地址为 `232`（结点 A），长度为 `6 bytes`。

我们可以通过刚才绑定监听的 `rx` 来查看接收到的数据：

```
> rx.data
[104, 101, 108, 108, 111, 33]
```

这里默认是以 `int` 类型，也就是 ASCII 码的形式输出，我们转换成 `String` 再输出一下：

```
> new String(rx.data)
hello!
```

同样用 `close()` 函数关闭：

```
> s.close()
```

### 2.4 使用 Python 发射和接收

我们刚才一直在浏览器打开的结点里的 Shell 里进行通信，这样不免麻烦而且不具备可复用性。

那么现在我们开始通过编程来进行通信，Unet 支持 Java、C、Python 等多项编程语言，这里我们使用 Python（各个语言在 Unet 的使用上都很相似）。

首先我们需要安装 Unet 的包：

```
$ pip install unetpy
```

启动我们之前已经用过的 2-node network：

```
$ ./bin/unet ./samples/2-node-network.groovy

2-node network
--------------

Node A: tcp://localhost:1101, http://localhost:8081/
Node B: tcp://localhost:1102, http://localhost:8082/

```

可以看到我们的两个结点所对应的主机为 `localhost`，tcp 端口分别为 `1101` 和 `1102`。

接下来我们新建两个文件 `tx.py` 和 `rx.py` 分别用于发射（transmit）和接收（receive）数据。

`tx.py`

```py
from unetpy import UnetSocket

s = UnetSocket('localhost', 1101)
s.send('hello!', 0)
s.close()
```

跟之前我们在 Shell 里的操作大差不差，只不过是需要通过主机和端口来打开 `UnetSocket`。

这里的 `send()` 函数会自动把字符串转换成 `byte[]`，所以我们可以传字符串，当然我们自己编码成 `byte[]` 再发送也没有问题，比如可以写成 `b'hello!'`。

`rx.py`

```py
from unetpy import UnetSocket

s = UnetSocket('localhost', 1102)
rx = s.receive()
print(f"from node {rx.from_}: {bytearray(rx.data).decode()}")
s.close()
```

也跟之前我们在 Shell 里的基本一样，输出直接用 Python 里的方法。

跟我们之前在 Shell 里的操作顺序一样，先运行 `rx.py`：

```
$ python rx.py
```

再运行 `tx.py`：

```
$ python tx.py
```

再切到运行 `rx.py` 的终端看一下：

```
$ python rx.py
from node 232: hello!
```

成功接收到数据，并且结束了接收。

### 2.5 使用声学调制解调器