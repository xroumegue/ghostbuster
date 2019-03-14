# Spectre and Machine learning: "GhostBuster"
## Scope

The proof of concept idea is to learn a model thanks to some machine learning algorithm able to detect a "spectre" (v1) attack at runtime.

This PoC targets a ARM v7/v8 or x86 speculative machine as the victim target, and uses the [spectre PoC](https://github.com/xroumegue/spectre)

Ghostbuster offers the following services:
* Collecting the raw dataset samples while exercising the system with different usecases.
* Aggregate the measurements, and build a labeled dataset
* Train a classification supervised machine learning model
* Detect at runtime a spectre attack, and kills the aggressive process

## Setup the environment

To install all libraries python3 dependencies, you can run the installer script:

```console
$bin/pyBuddy.sh
```

Then to activate and enter the python virtual environment:
```console
$ . venv/bin/activate
```

## Collecting the raw dataset samples

The [doMeasurement.py helper script](https://github.com/xroumegue/ghostbuster/blob/main/bin/doMeasurement.py) is collecting the raw measurements.

The script is running different usecases, such as:
* standby, using sleep
* IO activities on NFS, using iozone
* IO activities on SD card, using iozone
* GPU activities, running glmark2
* Network transactions, using iperf
* IO activies on NFS, using FIO
* Cryptographic computing
* Various low level libc operations, using lmbench
* ... and the spectre attack

[Linux kernel perf tool](https://perf.wiki.kernel.org/index.php/Tutorial) is used to collect the dataset features.

A measurement is completed every 2.5s(a72)/100ms(i6950x) for the whole run duration, starting the measurement with a random offset.

All measurements are repeated 10 times.

Note that you have to run iperf -s on the server before to start the measurements.

The measurements will be written to "reports" folder

## Aggregating and consolidating the raw measurements to a dataset

The [collect-reports.py](https://github.com/xroumegue/ghostbuster/blob/main/bin/collect-reports.py) is used to do it.
```bash
$ bin/collect-reports.py --help
usage: collect-reports.py [-h] -r ROOTDIR

Scikit learn SVM spectre attack seeker

optional arguments:
  -h, --help            show this help message and exit
  -r ROOTDIR, --rootdir ROOTDIR
                        Folder collecting the reports
  -m {a72,i6950x}, --machine {a72,i6950x}
                        Machine
```

## Training the model

[ProtonPack](https://github.com/xroumegue/ghostbuster/blob/main/bin/protonPack.py) does train a model, and output its performance.

```console
$ bin/protonPack.py --help
usage: protonPack.py [-h] -i INPUT [-v]

GhostBuster server

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Classsified dataset in CSV format
  -v, --verbose         Be verbose...
```

```console
$ bin/protonPack.py  --input dataset.txt
INFO -load-68  -Dataset loaded: 16417 samples, 5 features
INFO -load-82  -Using 4105 samples as test set
INFO -validate-109 -Confusion matrix:
[[3878    1]
 [   0  226]]
INFO -validate-112 -Classification report:
             precision    recall  f1-score   support

          0      1.000     1.000     1.000      3879
          1      0.996     1.000     0.998       226

avg / total      1.000     1.000     1.000      4105
```

## Hunting the ghosts

### Running the firehouse server.
[FireHouse](https://github.com/xroumegue/ghostbuster/blob/main/bin/fireHouse.py) trains the model, and then waits for prediction queries on a dedicated port on a server in the "cloud" :)

```console
$ bin/fireHouse.py --help
usage: fireHouse.py [-h] [-p PORT] -i INPUT [-v]

GhostBuster 's firehouse jail

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  port to listen
  -i INPUT, --input INPUTbin
                        Classsified dataset in CSV format
  -v, --verbose         Be verbose...
```

So on a PC, with let's say the ip address 10.168.1.100 :

```console
$ bin/fireHouse.py --input dataset.txt
INFO -load-68  -Dataset loaded: 16417 samples, 5 features
INFO -load-82  -Using 4105 samples as test set
INFO -validate-109 -Confusion matrix:
[[3871    3]
 [   0  231]]
INFO -validate-112 -Classification report:
             precision    recall  f1-score   support

          0      1.000     0.999     1.000      3874
          1      0.987     1.000     0.994       231

avg / total      0.999     0.999     0.999      4105

INFO -start-34  -Server listening on , port 12345
```

### Running the ghostbuster agent hunter.
[GhostBuster](https://github.com/xroumegue/ghostbuster/blob/main/bin/ghostBuster.py) hunts the ghosts on the embedded devices, scanning the most actives processes.
This collects the samples, and sends them to the firehouse, requesting a classification

If the firehouse's answer is a ghost, the ghostbuster agent kills the process:

```console
$ bin/ghostBuster.py --help
usage: ghostBuster.py [-h] [-p PORT] [-a ADDRESS] [-v]

GhostBuster server

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  port to listen
  -a ADDRESS, --address ADDRESS
                        Firehouse ip address
  -v, --verbose         Be verbose...
  -m {a72,i6950x}, --machine {a72,i6950x}
                        Machine

```

so, getting ghostbuster agent hunting for ghost is as simple as:

```console
$bin/ghostBuster.py --address 10.168.1.100 --machine i6950x
```
