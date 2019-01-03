from optparse import OptionParser
import socket
import os
import re
import math
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import queue
import sys
import traceback


__chunk_size__ = 128  # bytes
__timeout__ = 15  # seconds


def lock_method(meth):
    def wrapper(*args):
        self_ = args[0]
        pid = args[1]
        # print('decorator lock method', args, meth)
        with self_.get_lock(pid):
            returned_val = meth(*args)
        return returned_val
    return wrapper


def getNbProcess():
    return mp.cpu_count()*2


def writeoutput(output_path, line):
    if output_path and len(line):
        with open(output_path, "a") as f:
            f.write(line)
            if line[-1] != '\n':
                f.write('\n')


def split_addr_port(str):
    ip = ''
    port = 1080
    ip_regex = re.compile(r'(\d+(?:\.\d+){3})')
    port_regex = re.compile(r'(\d+(?:\.\d+){3}):(\d+)')

    m = ip_regex.search(str)
    if m:
        ip = m[0]
    else:
        raise Exception("Bad IP Format for", str)
    m = port_regex.search(str)
    if m and m.lastindex == 2:
        port = int(m[2])
    return(ip, port)


def test_socks5_server(ip_addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global __timeout__
    s.settimeout(__timeout__)
    ret = False
    try:
        s.connect((ip_addr, port))
        # \x05: VERSION \x01: NB AUTH METHODS, 1 \x00 METHOD: NO AUTHENTICATION
        s.send(b'\x05\x01\x00')
        resp = s.recv(2)
        # print('{0:#x} {1:#x}'.format(resp[0],resp[1]))
        ret = resp == b'\x05\x00'
        s.close()
    except Exception as e:
        raise Exception(
            "ERROR: {0}:{1:d} Exception {2}".format(ip_addr, port, e))
    if not ret:
        raise Exception(
            'ERROR: {0}:{1:d} proxy sock connection failure'.format(ip_addr, port))


def process_address(line):
    (ip, port) = split_addr_port(line)
    test_socks5_server(ip, port)


def process_file(file_name, logger):
    try:

        file = open(file_name, 'r')
        line = file.readline()
        while len(line) > 0:
            try:
                process_address(line)
                print('{0} connection success'.format(line))
                logger.log_file(line)
            except Exception as e:
                print(e)
            line = file.readline()
        file.close()
    except IOError as ioe:
        print(ioe)

# multi process with scheduler (task assignation when a process is done)


class SchedulerClass(object):
    DONE = 0
    BOUNDARY = 1
    LOCK = 2

    def __init__(self):

        self._procs = {}

    def register(self, pid, boundary):
        l = [0 for _ in range(3)]

        l[SchedulerClass.DONE] = boundary[0]
        l[SchedulerClass.BOUNDARY] = boundary
        l[SchedulerClass.LOCK] = mp.Lock()
        self._procs[pid] = l

    # @lock_method
    def get_boundary(self, pid):
        boundary = self._procs[pid][SchedulerClass.BOUNDARY]
        return boundary

    # @lock_method
    def get_done(self, pid):
        return self._procs[pid][SchedulerClass.DONE]

    def get_lock(self, pid):
        return self._procs[pid][SchedulerClass.LOCK]

    # @lock_method
    def progress(self, pid, file_pos):
        self._procs[pid][SchedulerClass.DONE] = file_pos

    def done(self, pid, split_function, file_name):
        # inner function
        print('process with pid=%d is done' % pid)

        def donesize(p):
            # with self.get_lock(p):
            done = self.get_done(p)
            _, end = self.get_boundary(p)
            # print("process pid=%d has to done size=%d" % (p, (end-done)))
            return end - done
        # --------------------------------------------
        pid_to_split = max(self._procs, key=donesize)
        # with self.get_lock(pid_to_split):
        start, end = self.get_boundary(pid_to_split)
        pos = self.get_done(pid_to_split)
        # print('max to done process is pid=%d with size to done=%d and boundary (%d,%d)' %
        # (pid_to_split, (end-pos), start, end))
        split = split_function(pos, start, end, file_name)
        if split > 0:
            # print('split process task from(%d,%d) to (%d,%d) and (%d,%d)' %
                  # (start, end, start, split, split, end))
            self._procs[pid_to_split][SchedulerClass.BOUNDARY] = (
                start, split)
            pid_data = self._procs[pid]
            pid_data[SchedulerClass.BOUNDARY] = (
                split, end)
            pid_data[SchedulerClass.DONE] = split
            return (split, end)
        # else:
            # print('chunk is to short to be splitted for pid=%d' % pid_to_split)
        return None


class LoggerClass(object):
    def __init__(self, file_path):
        self._file_path = file_path
        open(self._file_path, 'w+').close()

        self._nblines = 0

    def log_console(self, logline):
        self._nblines += 1
        print("{0}".format(self._nblines), logline)

    def log_file(self, line):
        with open(self._file_path, "a") as f:
            f.write(line)
            if line[-1] != '\n':
                f.write('\n')

    def end(self):
        print("Log process stopped. Nb lines read:", self._nblines)


class ManagerClass(BaseManager):
    pass


ManagerClass.register('Scheduler', SchedulerClass)
ManagerClass.register('Logger', LoggerClass)


def process_file_chunk(args):

    pid, file_name, scheduler, logger, chunk_boundary = args
    start, end = chunk_boundary

    print(
        "starting worker process pid={0} [{1}-{2}]".format(pid, start, end))

    with open(file_name, "r") as fd:
        fd.seek(start)
        pos = fd.tell()
        while pos < end:

            line = fd.readline()
            pos = fd.tell()

            percent = (pos-start)/(end-start)
            try:
                process_address(line)
                logger.log_console('[{0}] {1} connection success done={2:.2%}'.format(
                    os.getpid(), line.replace('\n', ''), percent))  # log console
                logger.log_file(line)  # log to file
            except Exception as e:
                logger.log_console('[{0}] {1} (done={2:.2%})'.format(
                    os.getpid(), str(e), percent))

            scheduler.progress(pid, pos)
            _, end = scheduler.get_boundary(pid)


def split_boundary(pos, start, end, file_name):
    middle = math.floor((pos+end)/2)
    global __chunk_size__
    # print("split_boundary middle=%d for boundary(%d,%d)" %
    # (middle, start, end))
    chunk_size = (middle-pos)
    if (middle-pos) > (__chunk_size__/4):
        with open(file_name, "r") as fd:
            middle = get_chunk_boundary(pos, chunk_size, fd, end)
            # print("split_boundary return middle=%d for boundary(%d,%d) after readjustment" %
            # (middle, start, end))
            if middle < end:
                return middle
    return -1


def get_chunk_boundary(start, chunk_size, file_desc, file_size):

    file_desc.seek(min(start+chunk_size, file_size), 0)
    ch = file_desc.read(1)
    while ch != "\n" and ch != "":
        ch = file_desc.read(1)

    end = file_desc.tell()

    if end <= start:
        raise Exception(
            "Error chunk boundary: start <= end ({0} <= {1})".format(start, end))

    return end


def get_file_chunk_boundaries(file_name):
    file_size = 0
    try:
        file_size = os.stat(file_name).st_size
    except FileNotFoundError:
        print("Error: file", file_name, "not found")
        return None

    global __chunk_size__
    chunk_size = __chunk_size__  # min_chunk_size

    nbparts = min(getNbProcess(), math.floor(file_size / chunk_size))
    chunk_size = math.ceil(file_size / nbparts)

    print("file size", file_size, "nb parts",
          nbparts, "chunk size", chunk_size)

    with open(file_name, "r") as fd:
        start = 0
        while(start < file_size):

            end = get_chunk_boundary(start, chunk_size, fd, file_size)
            yield (start, end)

            start = end


def worker_proc(file_name, scheduler, logger, chunk_boundary):

    pid = os.getpid()
    scheduler.register(pid, chunk_boundary)
    try:

        while not chunk_boundary is None:
            process_file_chunk(
                (pid, file_name, scheduler, logger, chunk_boundary))
            chunk_boundary = scheduler.done(pid, split_boundary, file_name)

    except KeyboardInterrupt:
        print("Keyboard interrupt => exit worker process {0}".format(
            os.getpid()))
    except FileNotFoundError as ioe:
        print("error opening file", ioe)
    except Exception as e:
        print("error while reading %s" % e)
        traceback.print_exc()


def process_file_mp(file_name, output_path):

    mgr = ManagerClass()
    scheduler = None
    try:
        open(output_path, 'w+').close()

        mgr.start()
        logger = mgr.Logger(output_path)
        scheduler = mgr.Scheduler()

        nb = getNbProcess()
        pool = mp.Pool(nb)

        for chunk_boundary in get_file_chunk_boundaries(file_name):
            print(chunk_boundary)
            pool.apply_async(worker_proc, [
                             file_name, scheduler, logger, chunk_boundary])

        print("pool ruuning")
        # Exit the completed jobs
        pool.close()
        pool.join()

        print("all processes terminated")
    except KeyboardInterrupt:
        print("Keyboard interrupt => exit process {0}".format(os.getpid()))
    except Exception as e:
        print("Exception ", e)
    finally:
        # shutdown log process
        print("output processe terminated")
        mgr.shutdown()


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", action="store_true",
                      default=False, help="if set, arguments processed as files")
    parser.add_option("-o", "--output", action="store",
                      default=None, help="if set, arguments processed as files")
    (options, args) = parser.parse_args()

    if options.output and os.path.isfile(options.output):
        os.remove(options.output)
    if len(args) > 0:
        if options.file:
            for f in args:
                process_file_mp(f, options.output)
        else:
            for addr in args:
                process_address(addr)
    else:
        print("no arguments provided")


if __name__ == "__main__":
    main()
