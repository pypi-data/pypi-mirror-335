#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)



def combine_df(df_value, old_df):
    """
    输入ndarray值，然后根据给的老df的column列名来输出一个新的df
    :param df_value:
    :param old_df:
    :return:
    """
    new_df = pd.DataFrame(df_value, columns=old_df.columns)
    return new_df


def change_df_type(df, column_name, type):
    """
    输入 df column_name type
    将df的某个列的类型更改为某个type 比如float等

    :param df:
    :param column_name:
    :param type:
    :return:
    """
    df[column_name] = df[column_name].astype(type)


def rename_df_columns(df, columns):
    """
    重新设置列名
    """
    df.rename(columns=columns, inplace=True)


def rename_df_column_by_index(dataset, index, to):
    """
    将index column 名字修改为 to
    :param dataset:
    :param index:
    :param to:
    :return:
    """
    assert isinstance(index, int)

    d = {dataset.columns[index]: to}
    logger.debug(f'dataset column {dataset.columns[index]}  renamed to {to}')
    dataset.rename(columns=d, inplace=True)
    return dataset


def rename_df_column_by_name(dataset, name, to):
    """
    将某个column 名字修改为 to
    :param dataset:
    :param name:
    :param to:
    :return:
    """
    assert isinstance(name, str)
    assert isinstance(to, str)

    d = {name: to}
    logger.debug(f'dataset column {name} renamed to {to}')
    dataset.rename(columns=d, inplace=True)
    return dataset


def get_all_column(df, column_name, remove_duplicate=True):
    """
    获取一列所有的值 默认去重
    :param column_name:
    :param remove_duplicate:
    :return:
    """
    column_values = df[column_name].values
    if remove_duplicate:
        column_values = set(column_values)

    column_values = list(column_values)

    return column_values



def mean(obj):
    """
    计算均值
    """
    return obj.mean()


def median(obj, axis=None):
    """
    计算中位数
    """
    return np.median(obj, axis=axis)


from collections import Counter


def mode(obj):
    """
    计算众数，支持最大相同记数返回
    """

    c = Counter(obj)

    most = 0
    first = True
    for k, v in c.most_common():
        if first:
            most = v
            first = False
            yield k
        else:
            if most == v:
                yield k
            else:
                break


def quantile(obj, seq=None):
    """
    计算分位数
    """

    if seq is None:
        seq = range(0, 101, 25)

    res = pd.Series(np.percentile(obj, seq), index=seq)
    return res


def pvariance(obj):
    """
    计算总体方差
    """
    return np.var(obj)


def pstd_deviation(obj):
    """
    计算总体标准差
    """
    return np.std(obj)


def variance(obj):
    """
    计算样本方差
    """
    return np.var(obj, ddof=1)


def std_deviation(obj):
    """
    计算样本标准差
    :param obj:
    :return:
    """
    return np.std(obj, ddof=1)


def permutation(n, k):
    """
    排列数 n!(n-k)!
    :param n:
    :param k:
    :return:
    """
    from scipy.special import perm
    return perm(n, k, exact=True)


def combination(n, k):
    """
    组合数 n!/k!(n-k)!
    :param n:
    :param k:
    :return:
    """
    from scipy.special import comb
    return comb(n, k, exact=True)


def n_choose_k(n, k, order=None):
    """
    n个元素选择k个
    :param n:
    :param k:
    :param order: 默认为None，也就是组合数，其他输入值将进行bool处理，获得True之后返回排列数。
    :return:
    """
    if order is None or not bool(order):
        return combination(n, k)
    elif bool(order):
        return permutation(n, k)
