#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.education import ALL_STR


def getFirstList(zeroList, zeroValue):
    firstList = [ALL_STR]
    for z in zeroList:
        if z[0] == zeroValue:
            firstList = z[1:]
    return firstList


def getSecondList(firstList, firstValue):
    secondList = [ALL_STR]
    for f in firstList:
        if f[0] == firstValue:
            secondList = f[1:]
    return secondList


def getFirstChoiceList(zeroList, zeroValue):
    zeroMapFirstChoiceList = {
        z[0]: [f[0] for f in z[1:]] for z in zeroList
    }
    choiceList = [ALL_STR]
    choiceList.extend(zeroMapFirstChoiceList.get(zeroValue, []))
    return choiceList


def getSecondChoiceList(firstList, firstValue):
    firstMapSecondChoiceList = {
        f[0]: [s[0] for s in f[1:]] for f in firstList
    }
    choiceList = [ALL_STR]
    choiceList.extend(firstMapSecondChoiceList.get(firstValue, []))
    return choiceList


def getThirdChoiceList(secondList, secondValue):
    secondMapThirdChoiceList = {
        s[0]: s[1] for s in secondList
    }
    choiceList = [ALL_STR]
    choiceList.extend(secondMapThirdChoiceList.get(secondValue, []))
    return choiceList


def getPickerMultiExtraValueBySubmit(zeroList, zeroValue, indexList):
    firstChoiceList = getFirstChoiceList(zeroList, zeroValue)
    firstValue = firstChoiceList[indexList[0]]

    firstList = getFirstList(zeroList, zeroValue)
    secondChoiceList = getSecondChoiceList(firstList, firstValue)
    secondValue = secondChoiceList[indexList[1]]

    secondList = getSecondList(firstList, firstValue)
    thirdChoiceList = getThirdChoiceList(secondList, secondValue)
    thirdValue = thirdChoiceList[indexList[2]]

    return [firstValue, secondValue, thirdValue]


def getPickerMultiExtraByColumnChange(zeroList, zeroValue, oldValueList, changedValue, changedColumn):
    indexList = [0, 0, 0]
    if changedColumn == 0:
        indexList = [changedValue, 0, 0]
    elif changedColumn == 1:
        firstChoiceList = getFirstChoiceList(zeroList, zeroValue)
        oldFirstIndex = firstChoiceList.index(oldValueList[0])
        indexList = [oldFirstIndex, changedValue, 0]
    elif changedColumn == 2:
        firstChoiceList = getFirstChoiceList(zeroList, zeroValue)
        oldFirstIndex = firstChoiceList.index(oldValueList[0])

        firstList = getFirstList(zeroList, zeroValue)
        secondChoiceList = getSecondChoiceList(firstList, oldValueList[0])
        oldSecondIndex = secondChoiceList.index(oldValueList[1])

        indexList = [oldFirstIndex, oldSecondIndex, changedValue]
    return getPickerMultiExtraValueBySubmit(zeroList, zeroValue, indexList)
