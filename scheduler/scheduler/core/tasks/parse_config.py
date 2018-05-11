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


def execute_action(action_name: str, all_actions: dict, executed_actions: set):
    if action_name in executed_actions:
        return [], []
    action = all_actions[action_name]
    executed_chain = []

    # Satisfy all dependencies
    for dependency in action.get('depends') or []:
        if dependency in executed_actions:
            continue
        temp_chain, _ = execute_action(dependency, all_actions, executed_actions)
        executed_chain += temp_chain

    # Check if all dependencies are satisfied
    # This check is needed in case one dependency blocks another
    for dependency in action.get('depends') or []:
        if dependency not in executed_actions:
            return [], [action_name]

    # Now that all dependencies are satisfied it's allowed to execute action
    executed_chain.append(action_name)
    executed_actions.add(action_name)
    executed_actions -= set(action.get('blocks') or [])

    return executed_chain, []


def build_action_chain(actions):
    unvisited_actions = []
    action_chain = []
    executed_actions = set()
    for action in actions:
        executed_action_chain, failed_actions = execute_action(action, actions, executed_actions)
        action_chain += executed_action_chain
        unvisited_actions += failed_actions
    return action_chain, unvisited_actions


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


