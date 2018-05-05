import time


def act(task_config, subtask_config):
    time.sleep(1)
    return None


def crawl(task_config, subtask_config):
    time.sleep(30)
    # returns [url1, url2, url3...]
    return ['https://www.google.ru/short_path', 'https://www.google.ru/quite_a_long_path']  # mocked


def analyse(task_config, subtask_config, links):
    # links: {username: [link1, link2, link3...] for username in users}
    time.sleep(5)
    # returns [(link1, owner1, intruder1), (link2, owner2, intruder2), ...]
    return [('https://www.google.ru/quite_a_long_path', 'normal_user', 'moderator_1')]  # mocked
