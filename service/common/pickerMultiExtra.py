#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.education import DEFAULT_EDUCATION_MULTI_CHOICE_LIST


def getFirstChoiceList(zeroChoiceList, zeroValue):
    zeroMapFirstChoiceList = {
        z[0]: [f[0] for f in z[1:]] for z in zeroChoiceList
    }
    choiceList = DEFAULT_EDUCATION_MULTI_CHOICE_LIST
    choiceList.extend(zeroMapFirstChoiceList.get(zeroValue, []))
    return choiceList


def getSecondChoiceList(firstChoiceList, firstValue):
    firstMapSecondChoiceList = {
        f[0]: [s[0] for s in f[1:]] for f in firstChoiceList
    }
    choiceList = DEFAULT_EDUCATION_MULTI_CHOICE_LIST
    choiceList.extend(firstMapSecondChoiceList.get(firstValue, []))
    return choiceList


def getThirdChoiceList(secondChoiceList, secondValue):
    secondMapThirdChoiceList = {
        s[0]: s[1] for s in secondChoiceList
    }
    choiceList = DEFAULT_EDUCATION_MULTI_CHOICE_LIST
    choiceList.extend(secondMapThirdChoiceList.get(secondValue, []))
    return choiceList


def getPickerMultiExtraValueBySubmit(zeroChoiceList, zeroValue, indexList):
    firstChoiceList = getFirstChoiceList(zeroChoiceList, zeroValue)
    firstValue = firstChoiceList[indexList[0]]
    secondChoiceList = getSecondChoiceList(firstChoiceList, firstValue)
    secondValue = secondChoiceList[indexList[1]]
    thirdChoiceList = getThirdChoiceList(secondChoiceList, secondValue)
    thirdValue = thirdChoiceList[indexList[2]]
    return [firstValue, secondValue, thirdValue]


def getPickerMultiExtraByColumnChange(zeroChoiceList, zeroValue, oldValueList, changedValue, changedColumn):
    indexList = [0, 0, 0]
    if changedColumn == 0:
        indexList = [changedValue, 0, 0]
    elif changedColumn == 1:
        firstChoiceList = getFirstChoiceList(zeroChoiceList, oldValueList[0])
        oldFirstIndex = firstChoiceList.index(oldValueList[0])
        indexList = [oldFirstIndex, changedValue, 0]
    elif changedColumn == 2:
        firstChoiceList = getFirstChoiceList(zeroChoiceList, oldValueList[0])
        oldFirstIndex = firstChoiceList.index(oldValueList[0])
        secondChoiceList = getSecondChoiceList(firstChoiceList, oldValueList[0])
        oldSecondIndex = secondChoiceList.index(oldValueList[1])
        indexList = [oldFirstIndex, oldSecondIndex, changedValue]
    return getPickerMultiExtraValueBySubmit(zeroChoiceList, zeroValue, indexList)
