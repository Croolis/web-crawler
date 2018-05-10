from django.test import TestCase

from scheduler.core.tasks import parse_config


class BuildActionChainTestCase(TestCase):

    def test_simple_chain(self):
        actions = {
            "2": {},
            "3": {
                "depends": [
                    "2"
                ]
            },
            "4": {
                "depends": [
                    "2"
                ]
            }
        }
        action_chain, unvisited_actions = parse_config.build_action_chain(actions)
        self.assertEqual(len(unvisited_actions), 0)

    def test_action_blocking(self):
        actions = {
          "2": {},
          "3": {
            "depends": [
              "2"
            ]
          },
          "4": {
            "depends": [
              "2"
            ]
          },
          "5": {
            "depends": [
              "3",
              "4"
            ]
          },
          "6": {
            "depends": [
              "5"
            ]
          },
          "7": {
            "depends": [
              "3"
            ],
            "blocks": [
              "7"
            ]
          },
          "8": {
            "depends": [
              "4"
            ],
            "blocks": [
              "8"
            ]
          },
          "9": {
            "depends": [
              "2"
            ],
            "blocks": [
              "3",
              "4",
              "5",
              "6",
              "7",
              "8",
              "9"
            ]
          },
          "10": {
            "depends": [
              "3"
            ]
          },
          "11": {
            "depends": [
              "10"
            ]
          },
          "12": {
            "depends": [
              "11",
              "5"
            ]
          },
          "13": {
            "depends": [
              "12"
            ],
            "blocks": [
              "12",
              "17"
            ]
          },
          "14": {
            "depends": [
              "11",
              "12",
              "13"
            ],
            "blocks": [
              "12",
              "14"
            ]
          },
          "15": {
            "depends": [
              "10"
            ],
            "blocks": [
              "11",
              "12",
              "13",
              "14",
              "15"
            ]
          },
          "16": {
            "depends": [
              "4"
            ]
          },
          "17": {
            "depends": [
              "12",
              "16"
            ]
          },
          "18": {
            "depends": [
              "16"
            ],
            "blocks": [
              "17"
            ]
          }
        }
        action_chain, unvisited_actions = parse_config.build_action_chain(actions)
        self.assertEqual(len(unvisited_actions), 0)
