try:
    import Queue as queue
except ImportError:
    import queue
import collections
import re
import subprocess
import sys
import threading

PingResult = collections.namedtuple('PingResult', 'host ping_rtt')


class PingSweeper(object):
    """Class used for performing ping sweeping."""
    ping_result_queue = queue.Queue()
    thread_count = 15
    host_queue = queue.Queue()

    def __init__(self, rtt_threshold_ms=1000):
        self.rtt_threshold_ms = rtt_threshold_ms

    def sweep(self, hosts):
        """Perform a ping sweep of the given hosts."""
        print('Performing ping test on {0} hosts...'.format(str(len(hosts))))

        for _ in range(self.thread_count):
            worker = threading.Thread(target=self._threaded_ping, args=(_, self.host_queue))
            worker.setDaemon(True)
            worker.start()

        for host in hosts:
            self.host_queue.put(host)

        # Wait until worker threads are done to exit
        self.host_queue.join()

        ping_results = []
        while True:
            try:
                ping_result = self.ping_result_queue.get_nowait()
            except queue.Empty:
                break

            ping_results.append(ping_result)

        return ping_results

    def _threaded_ping(self, _, q):
        """Ping hosts in queue using system ping command."""
        while True:
            # Get a host item form queue and ping it
            host = q.get()
            args = ['/bin/ping', '-c', '3', '-W', '1', str(host)]
            p_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

            # Save ping stdout
            p_ping_out = p_ping.communicate()[0]

            if p_ping.wait() == 0:
                # Example output: rtt min/avg/max/mdev = 22.293/22.293/22.293/0.000 ms
                search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',
                                   p_ping_out,
                                   re.M | re.I)
                ping_rtt = float(search.group(2))
                if ping_rtt < self.rtt_threshold_ms:
                    # Use sys.stdout.write instead of print because of threading issues
                    sys.stdout.write('Pinged {0} with average rtt {1}ms\n'.format(str(host), ping_rtt))

                self.ping_result_queue.put(PingResult(host=host, ping_rtt=ping_rtt))

            # Update queue: this host is processed
            q.task_done()
