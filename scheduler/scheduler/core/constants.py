class TASK_STATUS:
    WAITING = 'waiting'
    PROCESSING = 'processing'
    DONE = 'done'
    ERROR = 'error'

    @classmethod
    def choices(cls):
        return [
            (cls.WAITING, 'Waiting'),
            (cls.PROCESSING, 'Processing'),
            (cls.DONE, 'Done'),
            (cls.ERROR, 'Error'),
        ]


class SUBTASK_TYPE:
    ACTION = 'action'
    CRAWl = 'crawl'
    ANALYSIS = 'analysis'

    @classmethod
    def choices(cls):
        return [
            (cls.ACTION, 'Action'),
            (cls.CRAWl, 'Crawl'),
            (cls.ANALYSIS, 'Analysis'),
        ]
