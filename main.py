#!/usr/bin/env python3
import sys
import time
import aiorun
import asyncio
from shterens_tools import *

MIN_PYTHON = (3, 10)
USE_MULTI = config.getboolean("MultipleInstances", "enable")


if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


if sys.platform in ("linux", "darwin"):
    try:
        import uvloop
    except ModuleNotFoundError:
        loop = asyncio.new_event_loop()
    else:
        loop = uvloop.new_event_loop()
else:
    loop = asyncio.new_event_loop()
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


if USE_MULTI:
    from aiogram.utils.executor import start_webhook
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    
    from pyngrok import ngrok

    from shterens_tools.common.multi_instance.realprocessing import (
        ExQueue,
        RealProcess,
        RealLock,
        RealEvent,
        current_realprocess
    )
    from shterens_tools.common.multi_instance.network import (
        ExManager,
        NginxManager,
        get_available_port
    )
    
    WEBAPP_PORT = 3001
    INSTANCES = config.getint("MultipleInstances", "instances")
    NGROK_AUTHTOKEN = config.get("MultipleInstances", "ngrokAuthtoken")

    dispatcher.middleware.setup(LoggingMiddleware())


def run_one_instance():
    if USE_MULTI:
        with lock:
            WEBAPP_PORT = queue.get()
            WEBAPP_PORT = get_available_port(WEBAPP_PORT)
            queue.put(WEBAPP_PORT+1)
        
        loop.create_task(
            start_webhook(
                dispatcher=dispatcher, 
                webhook_path="",
                on_startup=main,
                skip_updates=True, 
                host="localhost", 
                port=WEBAPP_PORT
            )
        )
    else:
        loop.create_task(main())

    aiorun.run(loop=loop, shutdown_callback=on_shutdown)


async def main(dispatcher: Dispatcher=dispatcher):
    await app.start()
    
    if USE_MULTI:
        ngrokStarted.wait()
        for attempt in range(5):
            try:
                await bot.set_webhook(url=queue.get())
            except (RetryAfter, BotAPIBadRequest) as e:
                time.sleep(2)
                error_handler(loop=loop, context={"exception": e})
            else:
                break
        else:
            raise BotAPIBadRequest
    else:
        await dispatcher.skip_updates()
        await dispatcher.start_polling()


def error_handler(loop: asyncio.AbstractEventLoop, context: dict):
    exception = context["exception"]
    errors.critical(
        f"{exception.__class__.__name__} : {exception}", 
        exc_info=(
            exception.__class__, 
            exception, 
            exception.__traceback__
        )
    )


async def on_shutdown(loop: asyncio.AbstractEventLoop):
    if USE_MULTI:
        await bot.delete_webhook()
        if current_realprocess() != "MainProcess":
            return
        else:
            for tunnel in ngrok.get_tunnels():
                ngrok.disconnect(tunnel.public_url)
            
            NginxManager.stop()
    
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    
    mongoClient.close()
    logging.shutdown()


loop.set_exception_handler(error_handler)
asyncio.set_event_loop(loop)


if __name__ == "__main__":
    
    if USE_MULTI:
        
        ExManager.create_object("queue", ExQueue)
        ExManager.create_object("counter", ExQueue)
        #  Create counter for waiting
        ExManager.get_object("queue").wait_init(ExManager.get_object("counter"))
        ExManager.register_access_method("get_queue", "queue")

        ExManager.create_object("lock", RealLock)
        ExManager.register_access_method("get_lock", "lock")

        ExManager.create_object("ngrok", RealEvent)
        ExManager.register_access_method("get_ngrok", "ngrok")

        manager = ExManager(address=("localhost", 21000))
        manager.run_server()

        lock: RealLock = manager.lock
        queue: ExQueue = manager.queue
        ngrokStarted: RealEvent = manager.ngrok

        #  Put first port to queue
        queue.put(WEBAPP_PORT)
        queue.wait_reset()
        
        processes: typing.List[RealProcess] = []
        
        for _ in range(INSTANCES):
            process = RealProcess(
                target=("run_one_instance", run_one_instance),
                targetGlobals={"lock": RealLock, "queue": ExQueue, "ngrokStarted": RealEvent},
                manager=manager
            )
            process.start()
            processes.append(process)
        
        #  Waiting for ports from child processes
        ports = queue.wait(INSTANCES)
        queue.wait_end()

        NginxManager.generate_config(ports)
        NginxManager.start()
        
        ngrok.install_ngrok()
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
        tunnel: ngrok.NgrokTunnel = ngrok.connect(NginxManager.serverPort)
        #  Put webhook url as many times as INSTANCES
        queue.put(obj=link_to_https(tunnel.public_url), amount=INSTANCES)
        ngrokStarted.set()
        
        while True:
            try:
                for process in processes:
                    process.join()
            except KeyboardInterrupt:
                for process in processes:
                    process.terminate()
                break
    
    else:
        run_one_instance()
