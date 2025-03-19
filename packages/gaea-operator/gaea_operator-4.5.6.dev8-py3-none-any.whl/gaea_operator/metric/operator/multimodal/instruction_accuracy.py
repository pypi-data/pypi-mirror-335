#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/5
# @Author  : yanxiaodong
# @File    : instruction_accuracy.py
"""
from typing import List, Dict, Any
from collections import defaultdict
import json

import bcelogger

from .types import InstructionKind
from ..metric import MetricOperator
from ..check import check_input_length
from gaea_operator.utils import METRIC


@METRIC.register_module('instruction_accuracy')
class InstructionAccuracy(MetricOperator):
    """
    Instruction accuracy is the proportion of correct predictions among the total number of cases processed.
    """

    metric_name = 'precision_recall_accuracy'

    def __init__(self, instructions: List[Dict], **kwargs):
        super(InstructionAccuracy, self).__init__(num_classes=kwargs.get('num_classes', 2))
        self.instructions = [instruction for instruction in instructions
                             if instruction["kind"] == InstructionKind.image_recognition.value]
        self.instruction_name2value = {instruction["name"]: instruction for instruction in self.instructions}

        self.instruction_name2index = {instruction["name"]: index for index, instruction in enumerate(instructions)}
        self.instruction_index2name = {index: name for name, index in self.instruction_name2index.items()}
        self.reference_length_is_zero = False

        self.add_state("instruction_correct", default=[])
        self.add_state("image_correct", default=[])

    def _parse_dt_gt(self, predictions: List[Dict], references: List[Dict]):
        image_id2reference = defaultdict(list)
        image_id2predict = defaultdict(list)

        filter_num = 0
        max_index = max(self.instruction_index2name.keys()) if len(self.instruction_index2name) > 0 else -1
        for reference in references:
            try:
                _ = json.loads(reference["answer"])
                image_id2reference[reference["image_id"]].append(reference)

                if reference.get("instructions") is not None and len(reference["instructions"]) > 0:
                    for instruction in reference["instructions"]:
                        if instruction["name"] not in self.instruction_name2value and \
                                instruction["kind"] == InstructionKind.image_recognition.value:
                            self.instructions.append(instruction)
                            self.instruction_name2value[instruction["name"]] = instruction
                            max_index += 1
                            self.instruction_name2index[instruction["name"]] = max_index
                            self.instruction_index2name[max_index] = instruction["name"]
            except json.JSONDecodeError:
                filter_num += 1
        bcelogger.warning(f"{filter_num} answer is not json format, it will be filtered")

        for prediction in predictions:
            # 如果 reference answer 解析失败，预测结果直接丢掉，没有 reference 无法计算指标
            if prediction["image_id"] not in image_id2reference:
                continue
            image_id2predict[prediction["image_id"]].append(prediction)

        return image_id2predict, image_id2reference

    def _get_correct(self,
                     name: str,
                     pred_answer: Dict,
                     ref_answer: Dict,
                     instruction_correct: List,
                     image_correct: int):
        if name in ref_answer and name in pred_answer:
            if pred_answer[name] == ref_answer[name]:
                instruction_correct[self.instruction_name2index[name]] = 1
            else:
                instruction_correct[self.instruction_name2index[name]] = 0
                image_correct = 0
        elif name in ref_answer and name not in pred_answer:
            instruction_correct[self.instruction_name2index[name]] = 0
            image_correct = 0
        elif name not in ref_answer and name in pred_answer:
            image_correct = 0
        else:
            pass

        return instruction_correct, image_correct

    def _update_image(self, prediction: List, reference: List):
        pred_answer = {}
        ref_answer = {}

        for pred_item, ref_item in zip(prediction, reference):
            ref_answer.update(json.loads(ref_item["answer"]))
            try:
                pred_answer.update(json.loads(pred_item["answer"]))
            except json.JSONDecodeError:
                default_answer = {name: None for name in self.instruction_name2value}
                default_answer.update(pred_answer)
                pred_answer = default_answer

        instruction_correct = [-1 for _ in range(len(self.instructions))]
        image_correct = 1
        for name, instruction in self.instruction_name2value.items():
            instruction_correct, image_correct = \
                self._get_correct(name, pred_answer, ref_answer, instruction_correct, image_correct)

        self.instruction_correct.append(instruction_correct)
        self.image_correct.append(image_correct)

    def update(self, predictions: List[Dict], references: List[Dict]) -> None:
        """
        Computes and returns the middle states, such as TP, etc.
        """
        predictions, references = self._parse_dt_gt(predictions=predictions, references=references)

        if not check_input_length(references=references):
            self.reference_length_is_zero = True
            return

        for image_id, prediction in predictions.items():
            reference = references[image_id]
            self._update_image(prediction=prediction, reference=reference)

    def compute(self) -> Any:
        """
        Computes the metric by middle states.
        """
        if self.reference_length_is_zero:
            return -1, {instruction["name"]: -1 for instruction in self.instructions}

        image_accuracy = round(float(sum(self.image_correct) / len(self.image_correct)), self.decimals)

        instruction_accuracy = {}
        for name, index in self.instruction_name2index.items():
            corrects = [result[index] for result in self.instruction_correct if result[index] != -1]
            accuracy = \
                -1 if all(x == -1 for x in corrects) else round(float(sum(corrects) / len(corrects)), self.decimals)
            instruction_accuracy[name] = accuracy

        return image_accuracy, instruction_accuracy