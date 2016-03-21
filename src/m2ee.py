#!/usr/bin/python
#
# Copyright (c) 2009-2015, Mendix bv
# All Rights Reserved.
#
# http://www.mendix.com/
#

import cmd
import string
import sys

from m2ee import M2EE, logger

# Use json if available. If not (python 2.5) we need to import the simplejson
# module instead, which has to be available.
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError, ie:
        logger.critical("Failed to import json as well as simplejson. If "
                        "using python 2.5, you need to provide the simplejson "
                        "module in your python library path.")

if not sys.stdout.isatty():
    import codecs
    import locale
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


class CLI(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.m2ee = M2EE()
        self.prompt = "m2ee: "

    def do_status(self, args):
        feedback = self.m2ee.client.runtime_status().get_feedback()
        logger.info("The application process is running, the MxRuntime has "
                    "status: %s" % feedback['status'])

        critlist = self.m2ee.client.get_critical_log_messages()
        if len(critlist) > 0:
            logger.error("%d critical error(s) were logged. Use show_critical"
                         "_log_messages to view them." % len(critlist))

        max_show_users = 10
        total_users = self._who(max_show_users)
        if total_users > max_show_users:
            logger.info("Only showing %s logged in users. Use who to see a "
                        "complete list." % max_show_users)

    def do_show_critical_log_messages(self, args):
        critlist = self.m2ee.client.get_critical_log_messages()
        if len(critlist) == 0:
            logger.info("No messages were logged to a critical loglevel since "
                        "starting the application.")
            return
        print("\n".join(critlist))

    def do_check_health(self, args):
        health_response = self.m2ee.client.check_health()
        if not health_response.has_error():
            feedback = health_response.get_feedback()
            if feedback['health'] == 'healthy':
                logger.info("Health check microflow says the application is "
                            "healthy.")
            elif feedback['health'] == 'sick':
                logger.warning("Health check microflow says the application "
                               "is sick: %s" % feedback['diagnosis'])
            elif feedback['health'] == 'unknown':
                logger.info("Health check microflow is not configured, no "
                            "health information available.")
            else:
                logger.error("Unexpected health check status: %s" %
                             feedback['health'])
        else:
            health_response.display_error()

    def do_statistics(self, args):
        stats = self.m2ee.client.runtime_statistics().get_feedback()
        stats.update(self.m2ee.client.server_statistics().get_feedback())
        print(json.dumps(stats, sort_keys=True,
                         indent=4, separators=(',', ': ')))

    def do_show_cache_statistics_raw(self, args):
        stats = self.m2ee.client.cache_statistics().get_feedback()
        print(json.dumps(stats, sort_keys=True,
                         indent=4, separators=(',', ': ')))

    def do_who(self, args):
        if args:
            try:
                limitint = int(args)
                self._who(limitint)
            except ValueError:
                logger.warn("Could not parse argument to an integer. Use a "
                            "number as argument to limit the amount of logged "
                            "in users shown.")
        else:
            self._who()

    def do_w(self, args):
        self.do_who(args)

    def do_loglevel(self, args):
        args = string.split(args)
        if len(args) == 3:
            (subscriber, node, level) = args
            self._set_log_level(subscriber, node, level)
        else:
            if len(args) == 0:
                self._get_log_levels()
            print("To adjust loglevels, use: loglevel <subscribername> "
                  "<lognodename> <level>")
            print("Available levels: NONE, CRITICAL, ERROR, WARNING, INFO, "
                  "DEBUG, TRACE")

    def _get_log_levels(self):
        log_levels = self.m2ee.get_log_levels()
        print("Current loglevels:")
        log_subscribers = []
        for (subscriber_name, node_names) in log_levels.iteritems():
            for (node_name, subscriber_level) in node_names.iteritems():
                log_subscribers.append("%s %s %s" %
                                       (subscriber_name,
                                        node_name,
                                        subscriber_level))
        log_subscribers.sort()
        print("\n".join(log_subscribers))

    def _set_log_level(self, subscriber, node, level):
        level = level.upper()
        response = self.m2ee.set_log_level(subscriber, node, level)
        if response.has_error():
            response.display_error()
            print("Remember, all parameters are case sensitive")
        else:
            logger.info("Loglevel for %s set to %s" % (node, level))

    def do_show_current_runtime_requests(self, args):
        m2eeresp = self.m2ee.client.get_current_runtime_requests()
        m2eeresp.display_error()
        if not m2eeresp.has_error():
            feedback = m2eeresp.get_feedback()
            if not feedback:
                logger.info("There are no currently running runtime requests.")
            else:
                print("Current running Runtime Requests:")
                print(json.dumps(feedback))

    def do_show_all_thread_stack_traces(self, args):
        m2eeresp = self.m2ee.client.get_all_thread_stack_traces()
        m2eeresp.display_error()
        if not m2eeresp.has_error():
            feedback = m2eeresp.get_feedback()
            print("Current JVM Thread Stacktraces:")
            print(json.dumps(feedback, sort_keys=True,
                             indent=4, separators=(',', ': ')))

    def do_interrupt_request(self, args):
        if args == "":
            logger.error("This function needs a request id as parameter")
            logger.error("Use show_current_runtime_requests to view currently "
                         "running requests")
            return
        m2eeresp = self.m2ee.client.interrupt_request({"request_id": args})
        m2eeresp.display_error()
        if not m2eeresp.has_error():
            feedback = m2eeresp.get_feedback()
            if feedback["result"] is False:
                logger.error("A request with ID %s was not found" % args)
            else:
                logger.info("An attempt to cancel the running action was "
                            "made.")

    def do_exit(self, args):
        return -1

    def do_quit(self, args):
        return -1

    def do_EOF(self, args):
        print
        return -1

    def _who(self, limitint=None):
        limit = {}
        if limitint is not None:
            limit = {"limit": limitint}
        m2eeresp = self.m2ee.client.get_logged_in_user_names(limit)
        m2eeresp.display_error()
        if not m2eeresp.has_error():
            feedback = m2eeresp.get_feedback()
            logger.info("Logged in users: (%s) %s" %
                        (feedback['count'], feedback['users']))
            return feedback['count']
        return 0

    def precmd(self, line):
        if line:
            logger.trace("Executing command: %s" % line)
        return line

    # if the emptyline function is not defined, Cmd will automagically
    # repeat the previous command given, and that's not what we want
    def emptyline(self):
        pass

    def do_help(self, args):
        print("""Welcome to m2ee, the Mendix Runtime helper tools.

Available commands:
 status - display Mendix Runtime status (is the application running?
 who, w - show currently logged in users
 loglevel - view and configure loglevels
 show_current_runtime_requests - show action stack of current running requests
 interrupt_request - cancel a running runtime request
 exit, quit, <ctrl>-d - exit m2ee

Advanced commands:
 statistics - show all application statistics that can be used for monitoring
 show_all_thread_stack_traces - show all low-level JVM threads with stack trace
 profiler - start the profiler (experimental)
 check_health - manually execute health check
""")

        print("Hint: use tab autocompletion for commands!")

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        help="increase verbosity of output (-vv to be even more verbose)"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="count",
        dest="quiet",
        help="decrease verbosity of output (-qq to be even more quiet)"
    )
    (options, args) = parser.parse_args()

    # how verbose should we be? see
    # http://docs.python.org/release/2.7/library/logging.html#logging-levels
    verbosity = 0
    if options.quiet:
        verbosity = verbosity + options.quiet
    if options.verbose:
        verbosity = verbosity - options.verbose
    verbosity = verbosity * 10 + 20
    if verbosity > 50:
        verbosity = 100
    if verbosity < 5:
        verbosity = 5
    logger.setLevel(verbosity)

    cli = CLI()
    if args:
        cli.onecmd(' '.join(args))
    else:
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("^C")
            sys.exit(130)  # 128 + SIGINT
