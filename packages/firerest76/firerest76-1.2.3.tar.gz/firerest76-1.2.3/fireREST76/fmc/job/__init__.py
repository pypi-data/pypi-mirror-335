from fireREST76.fmc import Connection
from fireREST76.fmc.job.taskstatus import TaskStatus


class Job:
    def __init__(self, conn: Connection):
        self.taskstatus = TaskStatus(conn)
