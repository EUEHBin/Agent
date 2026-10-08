import socket
import asyncio
import run


def async_connect(host: str, port: int) -> asyncio.Future:
    loop = asyncio.get_running_loop()  # 获取当前的事件循环
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个socket
    sock.setblocking(False)  # 设置为非阻塞模式
    try:
        sock.connect((host, port))
    except BlockingIOError:
        pass

    fut = asyncio.Future()

    def on_writable() -> None:
        err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        loop.remove_writer(sock)
        if err == 0:
            fut.set_result(sock)
        else:
            fut.set_exception(ConnectionError(f"Connect failed: {err}"))

    # 监听文件描述符的可写事件，当socket连接成功时，文件描述符会变为可写
    loop.add_writer(sock, on_writable)
    return fut


def async_read(sock: socket.socket, host: str, port: int, path: str) -> asyncio.Future:
    loop = asyncio.get_running_loop()
    fut = asyncio.Future()
    req = f"""GET {path} HTTP/1.1
Host: {host}:{port}
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,ru;q=0.6
Cache-Control: no-cache
Connection: close
Pragma: no-cache
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36

""".replace("\n", "\r\n")
    sock.setblocking(False)
    sock.send(req.encode())
    data = b""

    def on_readable() -> None:
        nonlocal data
        try:
            chunk = sock.recv(4096)
            if chunk:
                data += chunk
            else:
                loop.remove_reader(sock)
                fut.set_result(data.decode())
        except BlockingIOError:
            pass

    loop.add_reader(sock, on_readable)
    return fut


def async_request(host: str, port: int, path: str) -> asyncio.Future:
    fut = asyncio.Future()

    def on_connected(f: asyncio.Future) -> None:
        try:
            sock = f.result()
            read_fut = async_read(sock, host, port, path)
            read_fut.add_done_callback(lambda rf: fut.set_result(rf.result()))
        except Exception as e:
            fut.set_exception(e)

    connect_fut = async_connect(host, port)
    connect_fut.add_done_callback(on_connected)
    return fut


def main() -> None:
    def on_response(f: asyncio.Future) -> None:
        try:
            response = f.result()
            print(response)
        except Exception as e:
            print(f"Request failed: {e}")
        finally:
            asyncio.get_running_loop().stop()

    async_request("shae-learn.yuanjin.tech", 80, "/").add_done_callback(on_response)


run.run(main)
