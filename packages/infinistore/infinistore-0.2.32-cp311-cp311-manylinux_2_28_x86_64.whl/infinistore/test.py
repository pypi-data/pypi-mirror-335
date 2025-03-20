import infinistore
from infinistore.lib import InfinityConnection, DisableTorchCaching, check_supported, Logger
import torch
import time
import random
import string

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits  # 字母和数字的字符集
    random_string = "".join(random.choice(letters_and_digits) for i in range(length))
    return random_string

config = infinistore.ClientConfig(
    # host_addr="127.0.0.1",
    host_addr="10.192.24.216",
    service_port=22345,
    # service_port=33345,
    dev_name="mlx5_0"
)
config.connection_type = infinistore.TYPE_LOCAL_GPU if config.host_addr == "127.0.0.1" else infinistore.TYPE_RDMA
# config.connection_type = infinistore.TYPE_RDMA

src_device = "cuda:2"
dst_device = "cuda:3"

conn = infinistore.InfinityConnection(config)
conn.connect()

Logger.info("connected")

# # key is random string
key = generate_random_string(10)
nkey = generate_random_string(10)
# src = [i for i in range(4096)]

# # local GPU write is tricky, we need to disable the pytorch allocator's caching
# with infinistore.DisableTorchCaching():
#     src_tensor = torch.tensor(src, device=src_device, dtype=torch.float32)

# conn.write_cache(src_tensor, [(key, 0)], 4096)
# conn.sync()

# # conn = infinistore.InfinityConnection(config)
# # conn.connect()

# with infinistore.DisableTorchCaching():
#     src_tensor = torch.zeros(4096, device=dst_device, dtype=torch.float32)
# conn.read_cache(src_tensor, [(key, 0)], 4096)
# conn.sync()
# assert torch.equal(src_tensor.cpu(), src_tensor.cpu())

# print(conn.check_exist(key))
# print(conn.check_exist(generate_random_string(10)))

# print(conn.get_match_last_index([key]))


src = [i for i in range(4096*20)]
with infinistore.DisableTorchCaching():
    src_tensor = torch.tensor(src, device=src_device, dtype=torch.float32)

keys = [generate_random_string(10) for i in range(100)]
blocks = [(keys[i], i * 4096) for i in range(100)]
conn.write_cache(src_tensor, blocks, 4096)
conn.sync()

# print(conn.get_match_last_index([]))
print(conn.get_match_last_index([keys[0]]))
# print(conn.get_match_last_index([nkey]))
print(conn.get_match_last_index(keys))
nkeys = [generate_random_string(10) for i in range(2)]
nkeys.extend(keys)
print(conn.get_match_last_index(nkeys))


# print(conn.delete_cache([key, generate_random_string(10)]))

# conn.read_cache(dst, [(key, 0)], 4096)
# conn.sync()

print('done')

def run(conn):
    # # number of blocks = 1GB/32k = 32000
    # # number of blocks = 128MB/32k = 4000
    # num_of_blocks = 1024 * 8
    # keys = [generate_random_string(10) for i in range(num_of_blocks)]
    # # block size: 8192*4=32k, same as mem pool block size
    # block_size = 8192
    # # src = [i for i in range(num_of_blocks * block_size)]

    # with infinistore.DisableTorchCaching():
    #     src_tensor = torch.rand(num_of_blocks * block_size, device=src_device, dtype=torch.float32)

    # blocks = [(keys[i], i * block_size) for i in range(num_of_blocks)]

    # conn.write_cache(src_tensor, blocks, block_size)
    # conn.sync()


    src_device = "cuda:0"
    dst_device = "cuda:2"

    check_supported()
    src = [i for i in range(4096)]
    with DisableTorchCaching():
        src_tensor = torch.tensor(src, device="cuda:0", dtype=torch.float32)
    now=time.time()
    conn.write_cache(src_tensor, [("key1", 0), ("key2", 1024), ("key3", 2048)], 8192)
    conn.sync()
    print(f"write elapse time is {time.time() - now}")


    with DisableTorchCaching():
        dst_tensor = torch.zeros(4096, device="cuda:2", dtype=torch.float32)

    now=time.time()
    conn.read_cache(dst_tensor, [("key1", 0), ("key2", 1024)], 1024)
    conn.sync()
    print(f"read elapse time is {time.time() - now}")


    assert torch.equal(src_tensor[0:1024].cpu(), dst_tensor[0:1024].cpu())

    assert torch.equal(src_tensor[1024:2048].cpu(), dst_tensor[1024:2048].cpu())

    print('done')


# if __name__ == "__main__":
#     conn = InfinityConnection(config)
#     conn.connect()
#     run(conn)