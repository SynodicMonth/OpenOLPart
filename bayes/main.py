import time
import subprocess
import os
import matplotlib.pyplot as plt

docker_id_map = {
    "img-dnn": "b7c786",
    "masstree": "e93de1",
}

def init_benchmark(bench_name, QPS, threads, cores):
    cmd = f"docker exec {docker_id_map[bench_name]} taskset -c {cores} /home/tailbench-v0.9/{bench_name}/run_gdw_{bench_name}.sh {QPS} {threads} &"
    subprocess.call(cmd, shell=True)

def get_ipc(cores):
    """
    get the IPC of the cores using perf
    """
    cmd = f"sudo perf stat -e instructions,cycles -C {cores} sleep 1"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
    print(result.stdout)

def get_latency(bench_name):
    dir = f'./share/{bench_name}.txt'
    while not os.path.exists(dir) or os.path.getsize(dir) == 0:
        time.sleep(1)
    
    with open(dir, "r") as f:
        first_line = f.readline()
        assert "latency" in first_line, "Lat file read failed!"
        lat = first_line.split("|")[0][24:-3]
        p95 = float(lat)
        print(f"p95 latency of {bench_name}: {p95}")

    os.remove(dir)
    return p95

def terminate_benchmark(bench_name):
    cmd = f"docker exec {docker_id_map[bench_name]} pkill -f /home/tailbench-v0.9/{bench_name}/.*_integrated"
    subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    terminate_benchmark("img-dnn")
    terminate_benchmark("masstree")
    # init_benchmark("img-dnn", 1000, 12, "1")
    # init_benchmark("masstree", 1000, 12, "2-8")

    # # get_ipc(1)
    # # get_ipc(2)

    # get_latency("img-dnn")
    # get_latency("masstree")

    # terminate_benchmark("img-dnn")
    # terminate_benchmark("masstree")

    img_dnn_latencies = []
    mass_latencies = []

    for img_dnn_cores in range(1, 12):  # 1 to 11 cores for img-dnn
        img_core_range = f"1-{img_dnn_cores}"

        # Run img-dnn
        init_benchmark("img-dnn", 10000, 24, img_core_range)

        time.sleep(1)
        
        img_lat = get_latency("img-dnn")
        img_dnn_latencies.append(img_lat)
        terminate_benchmark("img-dnn")

        time.sleep(1)

    for img_dnn_cores in range(1, 12):
        mass_core_range = f"1-{img_dnn_cores}"

        # Run masstree
        init_benchmark("masstree", 10000, 24, mass_core_range)

        time.sleep(1)
        
        mass_lat = get_latency("masstree")
        mass_latencies.append(mass_lat)
        terminate_benchmark("masstree")

        time.sleep(1)

    # plot
    plt.plot(range(1, 12), img_dnn_latencies, label="img-dnn")
    plt.plot(range(1, 12), mass_latencies, label="masstree")
    plt.xlabel("Number of cores")
    plt.ylabel("p95 latency")
    plt.legend()
    plt.savefig("latency.png")

