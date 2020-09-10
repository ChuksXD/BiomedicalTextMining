#!/bin/env python
# -*- coding: utf-8 -*-
"""
Tests with :class:`treetaggerwrapper.TaggerPoll` show limited benefit of
multithreading processing,
probably related to the large part of time spent in the preprocess chunking
executed by Python code and dependant on the Python Global Interpreter Lock
(GIL).

Another solution with Python standard packages is the :mod:`multiprocessing` module,
which provides tools to dispatch computing between different process
in place of threads, each process being independant with its own interpreter
(so its own GIL).

The :mod:`treetaggerpoll` module and its class :class:`TaggerProcessPoll` are for
people preferring natural language processing over multiprocessing programming… :-)

A comparison using the following example, running on a Linux OS with 4 core
Intel Xeon X5450 CPU,
tested with 1  2 3 4 5 and 10 worker process, gives the result in table below —
printed time is for the main process (which wait for its subprocess termination).
This shows great usage of available CPU when using this module for chunking/tagging:

..  list-table:: Workers count comparison
    :header-rows: 1

    * - workers
      - printed time
      - real CPU time
    * - 1
      - 228.49 sec
      - 3m48.527s
    * - 2
      - 87.88 sec
      - 1m27.918s
    * - 3
      - 61.12 sec
      - 1m1.154s
    * - 4
      - 53.86 sec
      - 0m53.907s
    * - 5
      - 50.68 sec
      - 0m50.726s
    * - 10
      - 56.45 sec
      - 0m56.487s


Short example
-------------

This example is available in the source code repository, in :file:`test/` subdirectory.
Here you can see that main module must have its main code wrapped in
a :code:`if __name__ == '__main__':` condition (for correct Windows support).
It may take an optional parameter to select how many workers you want (by default as
many workers as you have CPUs)::

    import sys
    import time

    JOBSCOUNT = 10000

    def start_test(n=None):
        start = time.time()
        import treetaggerpoll

        # Note: print() have been commented, you may uncomment them to see progress.
        p = treetaggerpoll.TaggerProcessPoll(workerscount=n, TAGLANG="en")
        res = []

        text = "This is Mr John's own house, it's very nice. " * 40

        print("Creating jobs")
        for i in range(JOBSCOUNT):
            # print("\tJob", i)
            res.append(p.tag_text_async(text))

        print("Waiting for jobs to complete")
        for i, r in enumerate(res):
            # print("\tJob", i)
            r.wait_finished()
            # print(str(r.result)[:50])
            res[i] = None   # Loose Job reference - free it.

        p.stop_poll()
        print("Finished after {:0.2f} seconds elapsed".format(time.time() - start))

    if __name__ == '__main__':
        if len(sys.argv) >= 2:
            nproc = int(sys.argv[1])
        else:
            nproc = None
        start_test(nproc)

If you have a graphical CPU usage, you should see a high average load on each CPU.


.. warning:: Windows support

    For Windows users, using :class:`TaggerProcessPoll` have implications on your
    code, see `multiprocessing docs`_, especially the Safe importing of main
    module part.

.. _multiprocessing docs: https://docs.python.org/2/library/multiprocessing.html#windows

"""

from __future__ import print_function
from __future__ import unicode_literals

import logging
import multiprocessing
import threading

import treetaggerwrapper


# We don't print for errors/warnings, we use Python logging system.
logger = logging.getLogger("TreeTagger.Poll")
# Avoid No handlers could be found for logger "TreeTagger" message.
logger.addHandler(logging.NullHandler())


DEBUG_MULTITHREAD = True

__all__ = ['TaggerProcessPoll']



# ==============================================================================
class TaggerProcessPoll(object):
    """Keep a poll of TreeTaggers process for processing with different threads.

    Each poll manage a set of processes, able to do parallel chunking and tagging.
    All taggers in the same poll are created for same processing (with same options).

    :class:`TaggerProcessPoll` objects have same high level interface than :class:`TreeTagger`
    ones with ``_async`` at end of methods names.

    Each of ``…_asynch`` method returns a :class:`ProcJob` object
    allowing to know if processing is finished, to wait for it, and to get the
    result.

    If you want to **properly terminate** a :class:`TaggerProcessPoll`, you must
    call its :func:`TaggerProcessPoll.stop_poll` method.
    """
    def __init__(self, workerscount=None, keepjobs=True, wantresult=True,
                 keeptagargs=True, **kwargs):
        """Creation of a new TaggerProcessPoll.

        By default a :class:`TaggerProcessPoll` creates same count of process than there
        are CPU cores on your computer .

        :param workerscount: number of worker process (and taggers) to create.
        :type workerscount: int
        :param keepjobs: poll keep references to Jobs to manage signal of
            their processing and store back processing results — default to True.
        :type keepjobs: bool
        :param wantresult: worker process must return processing result to be stored
            in the job — default to True.
        :type wantresult: bool
        :param keeptagargs: must keep tagging arguments in :class:`ProcJob` synchronization object
            — default to True.
        :type keeptagargs: bool
        :param kwargs: same parameters as :func:`treetaggerwrapper.TreeTagger.__init__`
            for :class:`TreeTagger` creation.
        """
        if workerscount is None:
            workerscount = multiprocessing.cpu_count()
        # Security, we need at least one worker and one tagger.
        if workerscount < 1:
            raise ValueError("Invalid workerscount %s", workerscount)

        if DEBUG_MULTITHREAD:
            logger.debug("Creating TaggerProcessPoll, %d workers", workerscount )

        if wantresult and not keepjobs:
            logger.debug("TaggerProcessPoll can't wantresult without keepjobs." )
            raise treetaggerwrapper.TreeTaggerError("Can't have wantresult without keepjobs.")

        # We create a temporary tagger and tag a small text to be able to detect any
        # problem and raise exception from here (and not in created subprocess).
        tmptagger = treetaggerwrapper.TreeTagger(**kwargs)
        tmptagger.tag_text(tmptagger.dummysequence)
        del tmptagger

        self._keepjobs = keepjobs
        self._wantresult = wantresult
        self._keeptagargs = keeptagargs
        self._stopping = False
        self._workers = []
        self._pendingjobs = multiprocessing.Queue()
        self._finishedjobs = multiprocessing.Queue()
        self._jobsrefs = {}
        self._jobslock = multiprocessing.Lock()

        if self._keepjobs:
            # Following thread retrieve results, store them in corresponding ProcJob, and
            # signal them.
            self._jobsmonitor = threading.Thread(target=self._monitor_main)
            self._jobsmonitor.daemon = True
            self._jobsmonitor.start()
        else:
           self._jobsmonitor = None

        self._build_workers(workerscount, kwargs)

        if DEBUG_MULTITHREAD:
            logger.debug("TaggerProcessPoll ready")

    def _build_workers(self, workerscount, taggerargs):
        if DEBUG_MULTITHREAD:
            logger.debug("Creating workers for TaggerProcessPoll")
        for i in range(workerscount):
            p = multiprocessing.Process(target=worker_main,
                            args=(self._pendingjobs, self._finishedjobs, taggerargs,
                                  self._keepjobs, self._wantresult))
            self._workers.append(p)
            p.start()

    def _create_job(self, methname, **kwargs):
        if self._stopping:
            raise TreeTaggerError("TaggerProcessPoll is stopped working.")
        job = ProcJob(self, methname, self._keepjobs, (kwargs if self._keeptagargs else None))
        if DEBUG_MULTITHREAD:
            logger.debug("ProcJob %d created, queuing it", id(job))
        if self._keepjobs:
            with self._jobslock:
                self._jobsrefs[id(job)] = job
        # We put just pickleable data inside a tuple.
        self._pendingjobs.put((id(job), methname, kwargs))
        return job

    def _monitor_main(self):
        while True:
            workresult = self._finishedjobs.get()
            if workresult is None:
                break
            workid, result = workresult
            with self._jobslock:
                job = self._jobsrefs.pop(workid)
            job._set_result(result)

    def stop_poll(self):
        """Properly stop a :class:`TaggerProcessPoll`.

        Takes care of finishing waiting threads, and deleting TreeTagger
        objects (removing pipes connexions to treetagger process).

        Once called, the :class:`TaggerProcessPoll` is no longer usable.
        """
        if DEBUG_MULTITHREAD:
            logger.debug("TaggerProcessPoll stopping")
        if not self._stopping:          # Just stop one time.
            if DEBUG_MULTITHREAD:
                logger.debug("Signaling to threads")
            self._stopping = True       # Prevent more Jobs to be queued.
            # Put one None by process (will awake processes).
            stopmonitor = True
            for x in range(len(self._workers)):
                self._pendingjobs.put(None)
        else:
            stopmonitor = False
        # Wait for processed to be finished.
        for p in self._workers:
            if DEBUG_MULTITHREAD:
                logger.debug("Signaling to process %s (pid %d)", p.name, p.pid)
            p.join()
        # Put None for monitoring thread to be finished (we do that only
        # after the joining of workers, to retrieve all processed feeback
        # before stopping the monitoring thread).
        if self._keepjobs and stopmonitor:
            self._finishedjobs.put(None)
            self._jobsmonitor.join()

        # Remove refs to process/threads.
        if self._workers:
            self._workers = []
        if self._jobsmonitor:
            self._jobsmonitor = None
        if DEBUG_MULTITHREAD:
            logger.debug("TaggerProcessPoll stopped")

    #---------------------------------------------------------------------------
    # Below methods have same interface than TreeTagger to tag texts.
    # --------------------------------------------------------------------------
    def tag_text_async(self, text, numlines=False, tagonly=False,
                 prepronly=False, tagblanks=False, notagurl=False,
                 notagemail=False, notagip=False, notagdns=False,
                 nosgmlsplit=False):
        """
        See :func:`TreeTagger.tag_text` method and :class:`TaggerProcessPoll` doc.

        :return: a :class:`ProcJob` object about the async process.
        :rtype: :class:`ProcJob`
        """
        return self._create_job('tag_text', text=text, numlines=numlines,
                                tagonly=tagonly, prepronly=prepronly,
                                tagblanks=tagblanks, notagurl=notagurl,
                                notagemail=notagemail, notagip=notagip,
                                notagdns=notagdns, nosgmlsplit=nosgmlsplit)

    # --------------------------------------------------------------------------
    def tag_file_async(self, infilepath, encoding=treetaggerwrapper.USER_ENCODING,
                 numlines=False, tagonly=False,
                 prepronly=False, tagblanks=False, notagurl=False,
                 notagemail=False, notagip=False, notagdns=False,
                 nosgmlsplit=False):
        """
        See :func:`TreeTagger.tag_file` method and :class:`TaggerProcessPoll` doc.

        :return: a :class:`ProcJob` object about the async process.
        :rtype: :class:`ProcJob`
        """
        return self._create_job('tag_file', infilepath=infilepath,
                                encoding=encoding, numlines=numlines,
                                tagonly=tagonly, prepronly=prepronly,
                                tagblanks=tagblanks, notagurl=notagurl,
                                notagemail=notagemail, notagip=notagip,
                                notagdns=notagdns, nosgmlsplit=nosgmlsplit)

    # --------------------------------------------------------------------------
    def tag_file_to_async(self, infilepath, outfilepath, encoding=treetaggerwrapper.USER_ENCODING,
                    numlines=False, tagonly=False,
                    prepronly=False, tagblanks=False, notagurl=False,
                    notagemail=False, notagip=False, notagdns=False,
                    nosgmlsplit=False):
        """
        See :func:`TreeTagger.tag_file_to` method and :class:`TaggerProcessPoll` doc.

        :return: a :class:`ProcJob` object about the async process.
        :rtype: :class:`ProcJob`
        """
        return self._create_job('tag_file_to', infilepath=infilepath,
                                outfilepath=outfilepath,
                                encoding=encoding, numlines=numlines,
                                tagonly=tagonly, prepronly=prepronly,
                                tagblanks=tagblanks, notagurl=notagurl,
                                notagemail=notagemail, notagip=notagip,
                                notagdns=notagdns, nosgmlsplit=nosgmlsplit)

class ProcJob(object):
    """Asynchronous job to process a text with a Tagger.

    These objects are automatically created for you and returned by
    :class:`TaggerProcessPoll` methods :func:`TaggerProcessPoll.tag_text_async`,
    :func:`TaggerProcessPoll.tag_file_async` and :func:`TaggerProcessPoll.tag_file_to_async`.

    You use them to know status of the asynchronous request, eventually
    wait for it to be finished, and get the final result.

    .. note::

        If your :class:`TaggerProcessPoll` has been created with ``keepjobs`` param set to False,
        you can't rely on the ProcJob object (neither finish state or result).
        And if you used ``wantresult`` param set to False, the final result can only be
        :code:`"finished"` or an exception information string.

    :ivar finished: Boolean indicator of job termination.
    :ivar result: Final job processing result — or exception.
    """
    def __init__(self, poll, methname, keepjobs, kwargs):
        self._poll = poll
        self._methname = methname
        self._kwargs = kwargs
        if keepjobs:
            self._event = threading.Event()
        else:
            self._event = None
        self._finished = False
        self._result = None

    def _set_result(self, result):
        self._result = result
        self._finished = True
        self._event.set()
        if DEBUG_MULTITHREAD:
            logger.debug("ProcJob %d finished", id(self))

    @property
    def finished(self):
        if self._event is None:
            raise treetaggerwrapper.TreeTaggerError("Can't know about a ProcJob state with keepjobs False.")
        return self._finished

    def wait_finished(self):
        """Lock on the ProcJob event signaling its termination.
        """
        if self._event is None:
            raise treetaggerwrapper.TreeTaggerError("Can't wait on a ProcJob with keepjobs False.")
        self._event.wait()

    @property
    def result(self):
        if self._event is None:
            raise treetaggerwrapper.TreeTaggerError("Can't rely on a ProcJob result with keepjobs False.")
        return self._result


# ==============================================================================
def worker_main(requestsqueue, resultsqueue, taggerargs, keepjobs, wantresult):
    """Main function of a worker process.

    The worker process first create a :class:`treetaggerwrapper.TreeTagger`
    object corresponding to options in :parapm:`taggerargs`.
    Then it loop on picking up a job work from the poll shared works queue,
    process it, and put back its result in the poll shared results queue.
    The loop exit when the picked work is None.

    :param requestsqueue: incoming requests queue of works to do.
    :type requestsqueue: Queue
    :param resultsqueue: outgoing result queue of works done.
    :type resultsqueue: Queue
    :param taggerargs: named parameters dict for creating the
        tagger.
    :type taggerargs: dict
    """
    tagger = treetaggerwrapper.TreeTagger(**taggerargs)
    while True:
        if DEBUG_MULTITHREAD:
            logger.debug("Worker waiting for work to pick…")
        work = requestsqueue.get()  # Pickup a job work.
        if work is None:
            if DEBUG_MULTITHREAD:
                logger.debug("Worker finishing")
            break   # Put Nones in works queue to stop workers.
        # Do the work
        workid, workmeth, workargs = work
        if DEBUG_MULTITHREAD:
            logger.debug("Worker doing picked work %d", workid)
        try:
            meth = getattr(tagger, workmeth)
            result = meth(**workargs)
            # If user don't want back result, just store a "finished" to distinguish
            # from exception.
            if not wantresult:
                result = "finished"
        except Exception as e:
            if DEBUG_MULTITHREAD:
                logger.debug("Work %d exit with exception", workid)
            result = str(e)
        # Send back result.
        if keepjobs:
            resultsqueue.put((workid, result))
    del tagger  # Explicitely remove object.
