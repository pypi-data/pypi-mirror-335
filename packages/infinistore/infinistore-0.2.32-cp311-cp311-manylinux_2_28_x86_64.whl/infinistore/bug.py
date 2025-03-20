#8309370d65b92d52ae8a04c1c83bab8e11344348
from infinistore import (
    ClientConfig,
    # check_supported,
    DisableTorchCaching,
    InfinityConnection,
)
import infinistore
import torch
import time
import string
import random

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits  # 字母和数字的字符集
    random_string = "".join(random.choice(letters_and_digits) for i in range(length))
    return random_string

def test_read_write_bottom_cache():

    config = ClientConfig(
        host_addr="127.0.0.1",
        service_port=33345,
        log_level="warning",
        connection_type=infinistore.TYPE_LOCAL_GPU,
    )
    conn = infinistore.InfinityConnection(config)
    conn.connect()
    # force the limit, for GPU T4, limited_bar1 must be True

    # allocate a 4(float32) * 100 tensor on GPU, the size is 400MB
    size = 400 << 20

    block_size = 512
    block_size_B = block_size * 4
    num_of_blocks = size // block_size_B


    #bad code this line test will fail .FIXME: why torch.randn will cause the error?
        
    src = torch.randn(num_of_blocks * block_size, device="cuda:0", dtype=torch.float32)
    # src = torch.randn(size, dtype=torch.float32)
    # src = src.cuda()
    key = generate_random_string(20)

    # write the bottom cache
    conn.write_cache(src, [(key, (num_of_blocks - 1) * block_size)], block_size)

    conn.sync()

    time.sleep(3)

    # read the bottom cache
    # dst = torch.zeros(512, device="cuda", dtype=torch.float32)
    # conn.read_cache(dst, [(key, 0)], 512)
    # conn.sync()
    # assert torch.equal(src[-512:], dst)

    dst = torch.zeros(num_of_blocks * block_size, device="cuda:2", dtype=torch.float32)
    conn.read_cache(dst, [(key, 0)], block_size)
    conn.sync()
    assert torch.equal(src[(num_of_blocks - 1) * block_size:].cpu(), dst[0:block_size].cpu())    

    print("done")


test_read_write_bottom_cache()