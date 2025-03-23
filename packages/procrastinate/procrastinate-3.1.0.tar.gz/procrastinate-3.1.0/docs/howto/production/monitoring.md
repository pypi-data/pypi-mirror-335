# Monitor Procrastinate in a real environment

## The baseline: a smoke test

The command line interface gives a basic monitoring available through the console.

```console
$ procrastinate healthchecks
App configuration: OK
DB connection: OK
Found procrastinate_jobs table: OK
```

## The administration shell

The procrastinate shell is a tool to administrate jobs and overview queues and tasks.
It is an interactive shell that you can run with the following command.

_Experimental feature_.

```console
$ procrastinate shell
Welcome to the procrastinate shell.   Type help or ? to list commands.

procrastinate> help

Documented commands (type help <topic>):
========================================
EOF  cancel  exit  help  list_locks  list_jobs  list_queues  list_tasks  retry
```

:::{note}
Shell commands can also be launched non-interactively by passing a single command.
In that case, the command will be executed, and the shell will exit immediately.

```console
$ procrastinate shell list_jobs
```

:::

As usual, you should use `--app` argument or `PROCRASTINATE_APP` environment
variable to specify the application you want to use (see {doc}`../basics/command_line`).

There are commands to list all the jobs (`list_jobs`), tasks (`list_tasks`),
queues (`list_queues`) and locks (`list_locks`).
And commands to retry (`retry`) & cancel (`cancel`) a specific job.

You can get help for a specific command _cmd_ by typing `help cmd`.

## Error reporting

When a job throws an error, procrastinate logs an error including `exc_info`.
Some error capture tools will automatically collect tracebacks from these logs.

A non-exhaustive list of tools which do this:

-   Sentry via its [logging integration](https://docs.sentry.io/platforms/python/guides/logging/) (enabled by default)
-   Google Cloud, although you may need to set up [json log formatting](https://cloud.google.com/error-reporting/docs/formatting-error-messages)

## The administration web portal

_Not yet, maybe someday._
