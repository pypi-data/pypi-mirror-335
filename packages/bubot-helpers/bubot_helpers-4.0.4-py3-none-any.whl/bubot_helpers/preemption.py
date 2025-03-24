import asyncio
import datetime


def dest_time_with_preemption(dest_time, preemption):
    if preemption > 0:
        return dest_time - datetime.timedelta(seconds=preemption)
    else:
        return dest_time + datetime.timedelta(seconds=preemption * -1)


def delta_seconds(time1, time2):
    if time1 > time2:
        delta = (time1 - time2).total_seconds()
    else:
        delta = (time2 - time1).total_seconds() * -1
    return delta


async def wait_dest_time(dest_time: datetime.datetime):
    while True:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        delta = (dest_time - current_time).total_seconds() / 2
        if delta > 20:
            await asyncio.sleep(delta)
            continue
        break

    while datetime.datetime.now(datetime.timezone.utc) <= dest_time:
        await asyncio.sleep(0.001)


class ServerTimeDifference:
    def __init__(self, request_param, *, debug_time_offset=None):
        self.request_param = request_param
        self.debug_time_offset = debug_time_offset

    async def _test_request(self, preemption):
        import aiohttp
        t0 = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=1)).replace(microsecond=0)
        start_time = dest_time_with_preemption(t0, preemption)
        await wait_dest_time(start_time)

        t1 = datetime.datetime.now(datetime.timezone.utc)
        async with aiohttp.ClientSession() as session:
            async with session.request(**self.request_param) as response:
                t2 = datetime.datetime.now(datetime.timezone.utc)
                headers_date = response.headers['Date']
                ts = datetime.datetime.strptime(headers_date, '%a, %d %b %Y %H:%M:%S GMT').replace(
                    tzinfo=datetime.timezone.utc)
                if self.debug_time_offset:
                    ts = dest_time_with_preemption(t2, self.debug_time_offset).replace(microsecond=0)
                # resp = await response.text()
                # print(resp, t2)
        return t0, t1, t2, ts

    @classmethod
    async def calc(cls, request_param, *, debug_time_offset=None):
        self = cls(request_param, debug_time_offset=debug_time_offset)

        preemption = 0.0
        t0, t1, t2, ts = await self._test_request(preemption)
        zero_delta = delta_seconds(ts, t0)
        delta = zero_delta
        step = 0.4
        k = 1
        preemptions = [preemption]
        while step >= 0.025:
            preemption0 = round(preemption + step * k, 2)
            if preemption0 in preemptions:
                if zero_delta == delta:
                    if k < 0:
                        k *= -1
                else:
                    if k > 0:
                        k *= -1
                step /= 2
                preemption = round(preemption + step * k, 2)
            else:
                preemption = preemption0
            preemptions.append(preemption)
            t0, t1, t2, ts = await self._test_request(preemption * -1)
            delta = delta_seconds(ts, t0)
            if zero_delta == delta:
                if k < 0:
                    k *= -1
                    step /= 2
            else:
                if k > 0:
                    k *= -1
                    step /= 2
        if zero_delta == delta:
            ts0 = ts + datetime.timedelta(seconds=1 - step * 2)
        else:
            ts0 = ts - datetime.timedelta(seconds=step * 2)
        result = delta_seconds(t2, ts0)
        return result