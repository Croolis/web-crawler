from collections import defaultdict
import copy
from itertools import chain
import json

from scheduler.core.constants import SUBTASK_TYPE
from scheduler.core.models import Task, Subtask


def first_group(iterable, key=lambda x: x):
    if not iterable:
        return []

    sorted_elems = sorted(iterable, key=key)
    return [x for x in sorted_elems if key(x) == key(sorted_elems[0])]


def build_action_chain(actions):
    allowed = {action for action in actions if not actions[action].get('depends')}
    blocked = set()
    action_chain = []

    blocks = defaultdict(list)
    dependants = defaultdict(list)
    allowers = defaultdict(list)

    for action, content in actions.items():
        blocks[action] = content.get('blocks', [])

        depends = content.get('depends', [])
        allowers[action] = depends
        for elem in depends:
            dependants[elem].append(action)

    while allowed:
        # Determining new action
        candidates = first_group(allowed, key=lambda x: len(blocks[x]))  # with fewest blocked actions
        action = sorted(candidates, key=lambda x: len(dependants[x]))[-1]  # with most dependent actions

        # Deleting new action from records
        action_chain.append(action)
        allowed.remove(action)
        blocked.add(action)
        for elem in chain(blocks.values(), dependants.values()):
            if action in elem:
                elem.remove(action)
        # Blocking other actions
        for elem in blocks[action]:
            blocked.add(elem)
            for newelem in chain(blocks.values(), dependants.values()):
                if elem in newelem:
                    newelem.remove(elem)
        # Unblocking newly-available actions
        for key, value in allowers.items():
            if action in value:
                value.remove(action)
            if not value and key not in blocked:
                allowed.add(key)

    unvisited_actions = set(actions) - set(action_chain)
    return action_chain, sorted(unvisited_actions)


def build_stage(action, stage, config, task):
    if action is not None:
        action_config = {
            'action': action,
        }
        Subtask.objects.create(
            parent_task=task,
            stage=stage,
            type=SUBTASK_TYPE.ACTION,
            configuration=json.dumps(action_config),
        )

    users = config['users']
    for user in users:
        user_config = {
            'user': user,
        }
        Subtask.objects.create(
            parent_task=task,
            stage=stage,
            type=SUBTASK_TYPE.CRAWL,
            configuration=json.dumps(user_config),
        )

    analysis_config = {}
    Subtask.objects.create(
        parent_task=task,
        stage=stage,
        type=SUBTASK_TYPE.ANALYSIS,
        configuration=json.dumps(analysis_config)
    )


def parse_config(name, config):
    action_chain, unvisited_actions = build_action_chain(copy.deepcopy(config['actions']))
    if unvisited_actions:
        info = 'These actions will not be executed: %s' % ','.join(unvisited_actions)
    else:
        info = None

    stages_number = len(action_chain) + 1
    task = Task.objects.create(
        name=name,
        configuration=json.dumps(config),
        stages_number=stages_number,
        info=info,
    )

    actions = [None] + action_chain
    for stage, action in enumerate(actions):
        build_stage(action, stage+1, config, task)

    return task


