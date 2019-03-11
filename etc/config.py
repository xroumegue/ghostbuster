
class Config:

    MACHINES = [ 'a72', 'i6950x']
    MACHINE_DEFAULT = 'i6950x'
    PERF_CMD = "perf \
        stat \
        -x \',\' \
        -a \
        --append \
        --delay {:} \
        --interval-print {:} \
        -o {:s} \
        -e {:s} \
        {:s}"

    LOOP=10

class a72(Config):
# TRM A72: Chapitre 11.8
#
# 0x11: cpu_cycles
# 0x12: Predicatvle branch speculatively executed
# 0x10: Mispredicted or not predicted branch speculatively executed
# 0x42: L1 data cache refill read
# 0x43: L1 data cache refill write
# 0x46: L1 data cache back write back victim
# 0x47: L1 data cache back write back clean
# 0x48: L1 data cache invalidate
# 0x70: Operation speculatively executed: load
# 0x71: Operation speculatively executed: store
# 0x72: Operation speculatively executed: load/store


    INTERVAL = '2500'

    DELAY_MIN = 0
    DELAY_MAX = 100
    DELAY_SCALE = 10
    DELAY_OFFSET = 1500
    EVENTS = [
        "cycles",
        "r10",
        "r12",
        "r42",
        "r48",
        "r72"
        ]

    USECASES = [
        {
            "name" : "sleep",
            "args" : ["/bin/sleep", "180"],
        },
        {
            "name" : "iozone",
            "args" : ["iozone", "-a"],
        },

        {
            "name" : "iozone_sdcard",
            "args" : ["iozone", "-a", "-g", "128M", "-f", "/run/media/mmcblk1p2/tmp/test.bin"],
        },
        {
            "name" : "glmark2",
            "args" : ["glmark2-es2-wayland", "--fullscreen"],
        },
        {
            "name" : "iperf",
            "args" : ["iperf", "-c", '10.161.68.210', "-t", "240"],
        },
        {
            "name" :"fio",
            "args" : ["fio",
                "--randrepeat=1",
                "--ioengine=libaio",
                "--direct=1",
                "--gtod_reduce=1",
                "--name=test",
                "--filename=random_read_write.fio",
                "--bs=4k",
                "--iodepth=64",
                "--size=256M",
                "--readwrite=randrw",
                "--rwmixread=75"
            ],
        },
        {
            "name" : "openssl",
            "args" : ["openssl", "speed", "aes-256-cbc", "rsa4096", "ecdsap521", "sha512", "dsa2048"],
        },
        {
            "name" : "lmbench",
            "args" : ["lmbench-run"],
        },
        {
            "name" : "Spectre",
            "args" : ["/usr/local/bin/spectre"],
        }
    ]


class i6950x(Config):
#
# Intel core
# https://download.01.org/perfmon/readme.txt
# i7 core - i7 6950x
# https://download.01.org/perfmon/BDW/broadwell_core_v23.tsv
#
#

# 0x88,0x81,BR_INST_EXEC.TAKEN_CONDITIONAL,Taken speculative and retired macro-conditional branches,"0,1,2,3","0,1,2,3,4,5,6,7",200003,0,0,0,0,0,0,0,0,0,0,0
# 0x89,0x41,BR_MISP_EXEC.NONTAKEN_CONDITIONAL,Not taken speculative and retired mispredicted macro conditional branches,"0,1
#
#
# Only 4 counters available on i7
# A 5th one can be enabled by disabled the nmi watchdog:
# 'echo 0 > /proc/sys/kernel/nmi_watchdog
#

    INTERVAL = '100'

    DELAY_MIN = 0
    DELAY_MAX = 100
    DELAY_SCALE = 10
    DELAY_OFFSET = 1000
    EVENTS = [
            "cycles",
            "r8188",
            "r4189",
            "L1-dcache-loads",
            "l1d.replacement",
        ]

    USECASES = [
        {
            "name" : "sleep",
            "args" : ["/bin/sleep", "180"],
        },
        {
            "name" : "iozone",
            "args" : ["iozone", "-a"],
        },

        {
            "name" : "iozone_sdcard",
            "args" : ["iozone", "-a", "-g", "128M", "-f", "/media/xavier/MMC/tmp/test.bin"
],
        },
        {
            "name" : "glmark2",
            "args" : ["glmark2", "--fullscreen"],
        },
        {
            "name" : "iperf",
            "args" : ["iperf", "-c", '192.168.1.4', "-t", "240"],
        },
        {
            "name" :"fio",
            "args" : ["fio",
                "--randrepeat=1",
                "--ioengine=libaio",
                "--direct=1",
                "--gtod_reduce=1",
                "--name=test",
                "--filename=random_read_write.fio",
                "--bs=4k",
                "--iodepth=64",
                "--size=256M",
                "--readwrite=randrw",
                "--rwmixread=75"
            ],
        },
        {
            "name" : "openssl",
            "args" : ["openssl", "speed", "aes-256-cbc", "rsa4096", "ecdsap521", "sha512", "dsa2048"],
        },
        {
            "name" : "lmbench",
            "args" : ["lmbench-run"],
        },
        {
            "name" : "Spectre",
            "args" : ["/usr/local/bin/spectre"],
        }
    ]


