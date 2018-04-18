class CRAWL_STATUS:
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
