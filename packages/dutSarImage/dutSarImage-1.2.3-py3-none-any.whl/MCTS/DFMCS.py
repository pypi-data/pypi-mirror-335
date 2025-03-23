import os
from operator import eq
from os import listdir
from os.path import isfile, join
import random

import cv2
import numpy as np
from pomegranate import *
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import math
import copy


def white_manipulation(val=None, dim=0):
    # print("val: ", val)
    if not eq(val.all(), [255, 255, 255]):
        return [255, 255, 255]
    else:
        return [255, 0, 0]


def UCB1(keypoint_distribution, plays_per_node, totalplays):
    retval = []
    for i in range(len(keypoint_distribution)):
        value = keypoint_distribution[i]
        value += math.sqrt(np.log(plays_per_node[i]) / totalplays)
        retval.append(value)
    retval = np.asarray(retval)
    return retval / sum(retval)


class DFMCS_Parameters:
    # def __init__(self, image, true_class, model, predshape=(1, 368, 368, 3)):
    #     self.model = model
    #     self.ORIGINAL_IMAGE = copy.deepcopy(image)
    #     self.TRUE_CLASS = true_class
    #     self.SIGMA_CONSTANT = 15
    #     self.VISIT_CONSTANT = 5
    #     self.manip_method = white_manip
    #     self.X_SHAPE = 368
    #     self.Y_SHAPE = 368
    #     self.predshape = predshape
    #     self.EPSILON = 50
    #     self.MANIPULATIONS = []
    #     self.TOTAL_PLAYS = 1
    #     self.PLAYS_ARRAY = np.ones(len(self.kp))
    #     self.MISCLASSIFIED = False
    #     self.verbose = False
    #     self.small_image = False
    #     self.inflation_constant = 15
    #     self.kp, self.des, self.r = [], [], []
    #
    #     # 前提准备 修改通道值
    #     def preproc(im):
    #         im_pred = IMAGE.reshape(params.predshape)
    #         im_pred = im_pred.astype('float')
    #         return image
    #
    #     self.preprocess = preproc
    #
    #     def predi(im):
    #         """ 返回图像被分为不同类别的概率，以及每个测试集概率最大的下标 """
    #         im = self.preprocess(im)
    #         # X_test：为即将要预测的测试集
    #         # batch_size:为一次性输入多少张图片给网络进行训练，最后输入图片的总数为测试集的个数
    #         # verbose:1代表显示进度条，0不显示进度条，默认为0
    #         # 返回值：每个测试集的所预测的各个类别的概率
    #         prob = self.model.predict(im)
    #         # np.argmax(x,axis=1)函数，默认axis=1
    #         # axis=1从x的每一行中找出最大数值的下标,（这里下标代表类别）（默认）
    #         # axis=0从x的每一列找出最大数值的下标
    #         # pred保存每个测试集被预测的类别，即一行中概率最大的值的下标
    #         pred = np.argmax(np.asarray(prob))
    #         return pred, prob
    #
    #     self.predict = predi
    #     pred, prob = self.predict(image)
    #     self.PROBABILITY = max(max(prob))
    #     self.SOFT_MAX_ARRAY = prob
    #     self.backtracking_constant = 10

    def __init__(self, MCTS_params, image):
        self.model = MCTS_params.model
        self.ORIGINAL_IMAGE = copy.deepcopy(image)
        self.TRUE_CLASS = MCTS_params.TRUE_CLASS
        self.manip_method = MCTS_params.MANIP
        self.VISIT_CONSTANT = MCTS_params.VISIT_CONSTANT
        self.SIGMA_CONSTANT = MCTS_params.SIGMA_CONSTANT
        self.X_SHAPE = MCTS_params.X_SHAPE
        self.Y_SHAPE = MCTS_params.Y_SHAPE
        self.predshape = MCTS_params.predshape
        self.kp = MCTS_params.kp
        self.des = MCTS_params.des
        self.r = MCTS_params.r
        self.EPSILON = 50
        self.MANIPULATIONS = []
        self.TOTAL_PLAYS = 1
        self.PLAYS_ARRAY = np.ones(len(self.kp))
        self.MISCLASSIFIED = False
        self.verbose = MCTS_params.verbose
        self.preprocess = MCTS_params.preprocess
        self.predict = MCTS_params.predict
        self.small_image = MCTS_params.small_image
        self.inflation_constant = 15
        pred, prob = self.predict(image)
        self.PROBABILITY = max(max(prob))
        self.SOFT_MAX_ARRAY = prob
        self.backtracking_constant = MCTS_params.backtracking_constant


def SIFT_Filtered(image, parameters, threshold=0.00):
    # We need to expand the image to get good keypoints
    if parameters.small_image:
        xs = parameters.X_SHAPE * parameters.inflation_constant
        ys = parameters.Y_SHAPE * parameters.inflation_constant
        image = cv2.resize(image, (xs, ys))

    sift = cv2.xfeatures2d.SIFT_create()
    # 获取到图片中的所有关键点和向量
    kp, des = sift.detectAndCompute(image, None)
    # FILTER RESPONSES:
    responses = []

    for x in kp:
        responses.append(x.response)
    responses.sort()
    ret = []
    index_tracker = 0
    # 去掉一部分不重要关键点（根据响应强度）
    for x in kp:
        if x.response >= threshold:
            ret.append((x, des[index_tracker], x.response))
        index_tracker = index_tracker + 1
    # 将元组按照响应强度进行排序
    retval = sorted(ret, key=lambda tup: tup[2])
    return zip(*retval)


"""
Input: image, true_class, manip_method（操作指令）, kp_selection（关键点选择） (optional)
Output: adv_image, softmax_array（测试集最终输出类别的概率）, L0 Severity, kp_selection
"""


# cutoff是最小严重性程度
def DFMCS(params, cutoff=-1):
    """ Output: adv_image, softmax_array, L0 Severity, kp_selection """
    image = copy.deepcopy(params.ORIGINAL_IMAGE)
    if (params.kp == []):
        # SIFT_Filtered返回关键点、关键点的向量以及关键点的响应强度
        temp_params = SIFT_Filtered(params.ORIGINAL_IMAGE, params)
        params.kp = temp_params[0]
        params.des = temp_params[1]
        params.r = temp_params[2]
        params.r = np.asarray(params.r)
        # 概率
        params.r = params.r / sum(params.r)
    if (cutoff != -1):
        enforce_cutoff = True
    else:
        enforce_cutoff = False

    # 返回操作元组
    def sample_from_kp(k):
        """ 生成高斯混合模型 并返回操作元组 """
        mu_x, mu_y, sigma = int(round(k.pt[0])), int(round(k.pt[1])), k.size
        # Remember, it may be wise to expand simga
        #  greater varience = less honed attack
        sigma += params.SIGMA_CONSTANT
        # 表示一个正态分布 (高斯分布)，它的均值为 mu_x，标准差为 σ
        # 通过高斯方程求出像素点的G值
        d_x = NormalDistribution(mu_x, sigma)
        d_y = NormalDistribution(mu_y, sigma)
        # 对x，y进行归一化处理 生成高斯混合模型
        x = d_x.sample()
        y = d_y.sample()
        # 扩展坐标
        if (params.small_image):
            x /= params.inflation_constant
            y /= params.inflation_constant
        x = int(x)
        y = int(y)
        if (x >= params.X_SHAPE):
            x = params.X_SHAPE - 1
        elif (x < 0):
            x = 0
        if (y >= params.Y_SHAPE):
            y = params.Y_SHAPE - 1
        elif (y < 0):
            y = 0
        return int(x), int(y)

    # 奖励值反向传播
    def backprop(keypoint_distribution, expored_index, reward):
        # 为什么除以25
        keypoint_distribution[expored_index] += (float(reward) / 0.5)
        # keypoint_distribution[expored_index] += (float(reward) / 25)
        if keypoint_distribution[expored_index] < 0:
            keypoint_distribution[expored_index] = 0
        # keypoint_distribution += (max(keypoint_distribution)/4)
        keypoint_distribution /= sum(keypoint_distribution)
        return keypoint_distribution

    # 计算奖励值
    # params.SOFT_MAX_ARRAY,prob, true_class, target_class
    def calculate_reward(orig, new, true_class, target_class=None):
        if target_class is None:
            return orig[0][true_class] - new[0][true_class]
        else:
            return new[0][target_class] - orig[0][target_class]

    def calculate_cumulative_reward(orig, new, true_class, target_class):
        sum_reward = 0
        for i in target_class:
            sum_reward += orig[0][i] - new[0][i]
        return sum_reward / len(target_class)

    # 通过蒙特卡洛树搜索扩展结点，并对关键点上像素进行修改，判断计算关键点的奖励值
    # 重复的过程不是对同一个关键点进行操作，而是根据奖励值反向传播，得到新的关键点强度分布，之后根据np的函数重新选择关键点，并对其周围的像素进行操作
    # 简而言之，就是每次攻击都是在对整张图片进行操作，而不是特定的某个区域
    def run_mcts_exploitation_step(model, dfmcs_image, true_class, keypoints,
                                   keypoint_distribution, backpropogation,
                                   TOTAL_PLAYS, target_class=None):
        """
        keypoint_distribution, image, TOTAL_PLAYS, MISCLASSIFIED
        """
        # 计算关键点强度
        for i in range(len(keypoint_distribution)):
            if keypoint_distribution[i] < 0:
                keypoint_distribution[i] = 0
        keypoint_distribution = np.asarray(keypoint_distribution)
        keypoint_distribution /= sum(keypoint_distribution)
        # Choose a keypoint from the keypoint distribution (exploitation)
        kp_len_array = range(len(keypoint_distribution))
        # 玩家一 选出一个关键点
        kis = np.random.choice(kp_len_array, p=keypoint_distribution)
        # (4b) - Expore that keypoint up to some bound
        expiter = 0
        # white = 0
        # 对关键点周围的像素进行有限次修改
        while expiter != params.VISIT_CONSTANT:
            # 根据关键点选择一个操作元组
            # x,y会根据西格玛改变
            x, y = sample_from_kp(keypoints[kis])
            # print("选中的点为：", x, y, image[y][x])
            try:
                # list() 将元组转换为列表
                # 如果修改前后像素无变化 就跳过 修改下一个像素
                if (((x, y) in params.MANIPULATIONS) or
                        list(dfmcs_image[y][x]) ==
                        list(params.manip_method(dfmcs_image, x, y))):
                    # if white >= 5:
                    #     image[y][x] = params.manip_method(image[y][x], params.EPSILON)
                    # white += 1
                    continue
            except:
                if (((x, y) in params.MANIPULATIONS) or
                        (dfmcs_image[y][x]) ==
                        (params.manip_method(dfmcs_image, x, y))):
                    continue
            # 对像素进行修改
            dfmcs_image[y][x] = params.manip_method(dfmcs_image, x, y)
            params.MANIPULATIONS.append((x, y))

            expiter += 1

        # 观察预测分类和值
        d_pred, d_prob = params.predict(dfmcs_image)
        # 如果是反例 返回
        if ((d_pred != int(true_class) and target_class is None) or
                (d_pred != target_class and target_class is not None)):
            if params.verbose:
                print("\n")
                print("Adversarial Example Found")
                f = """Current Probability: %s
                       Current Class: %s
                       Manipulations: %s
                """ % (d_prob[0][d_pred], d_pred, len(params.MANIPULATIONS))
                sys.stdout.write("\r" + str(f))
                sys.stdout.flush()
            MISCLASSIFIED = True
            return keypoint_distribution, dfmcs_image, TOTAL_PLAYS, MISCLASSIFIED

        # !*!计算奖励值
        reward = calculate_reward(params.SOFT_MAX_ARRAY,
                                  d_prob, true_class, target_class)
        # print("奖励值为：%s" % reward)

        if reward < 0:
            # replace中保存MANIPULATIONS中的最后这VISIT_CONSTANT个的操作元组
            # 也就是恢复刚刚修改过的像素值 变为原来的图片
            # print("撤销操作！")
            replace = params.MANIPULATIONS[-params.VISIT_CONSTANT:]
            for x, y in replace:
                dfmcs_image[y][x] = params.ORIGINAL_IMAGE[y][x]
        MISCLASSIFIED = False
        # (4c) - Backpropogation
        # 反向传播
        keypoint_distribution = backpropogation(keypoint_distribution,
                                                kis, reward)
        # 访问次数
        params.PLAYS_ARRAY[kis] += 1
        params.TOTAL_PLAYS += 1
        if (params.verbose):
            f = """Current Probability: %s
                   Current Class: %s
                   Current Destribution: %s
                   Manipulations: %s
                """ % (d_prob[0][d_pred], d_pred, np.max(keypoint_distribution), len(params.MANIPULATIONS))
            sys.stdout.write("\r" + str(f))
            sys.stdout.flush()
        return keypoint_distribution, dfmcs_image, TOTAL_PLAYS, MISCLASSIFIED

    params.MISCLASSIFIED, mis = False, False
    pred, prob = params.predict(image)
    NEW_PROBABILITY = prob[0][pred]
    params.SOFT_MAX_ARRAY = prob

    if pred != params.TRUE_CLASS:
        print("在DFMCS中，当前分类错误！")
        MISCLASSIFIED, mis = True, True
        return params.ORIGINAL_IMAGE, params.SOFT_MAX_ARRAY, 0, None

    iters = 0
    cutoff_enforced = False
    if params.verbose:
        print("Starting DFMCS. Cuttoff: %s" % cutoff)
        print("params.VISIT_CONSTANT: %s" % params.VISIT_CONSTANT)
    # 循环进行像素操作 两种情况：还没有找到最小严重性程度（cutoff == -1）或已找到
    if cutoff == -1:
        print("还没有找到对抗样本：")
        # while not params.MISCLASSIFIED:
        condition = image.shape[0]*image.shape[1]
        print(len(params.MANIPULATIONS))
        while len(params.MANIPULATIONS) <= 67000 and not params.MISCLASSIFIED:
            retvals_from_run = run_mcts_exploitation_step(params.model,
                                                          image,
                                                          params.TRUE_CLASS,
                                                          params.kp,
                                                          params.r,
                                                          backprop,
                                                          params.TOTAL_PLAYS)
            params.r = retvals_from_run[0]
            image = retvals_from_run[1]
            # 总访问次数
            params.TOTAL_PLAYS = retvals_from_run[2]
            params.MISCLASSIFIED = retvals_from_run[3]
            # 如果一次就使图像错误分类 则返回
            if params.MISCLASSIFIED:
                break
            retvals_from_run = run_mcts_exploitation_step(params.model,
                                                          image,
                                                          params.TRUE_CLASS,
                                                          params.kp,
                                                          params.r,
                                                          backprop,
                                                          params.TOTAL_PLAYS)
            params.r = retvals_from_run[0]
            image = retvals_from_run[1]
            params.TOTAL_PLAYS = retvals_from_run[2]
            params.MISCLASSIFIED = retvals_from_run[3]
            iters += 1
            # if(iters >= 10):
            # cutoff_enforced = False
            # break
        if params.MISCLASSIFIED:
            cutoff_enforced = False
        else:
            cutoff_enforced = True
    else:
        print("之前的操作中找到了对抗样本：")
        cutoff_enforced = True
        # 有限次循环中查找对抗样本，没有找到就返回严重性程度-1
        # 当前操作集超过最小操作集 无需再进入此循环
        for i in range(int(cutoff / int(1.5 * params.VISIT_CONSTANT))):
            retvals_from_run = run_mcts_exploitation_step(params.model,
                                                          image,
                                                          params.TRUE_CLASS,
                                                          params.kp,
                                                          params.r,
                                                          backprop,
                                                          params.TOTAL_PLAYS)
            params.r = retvals_from_run[0]
            image = retvals_from_run[1]
            params.TOTAL_PLAYS = retvals_from_run[2]
            params.MISCLASSIFIED = retvals_from_run[3]
            if params.MISCLASSIFIED:
                cutoff_enforced = False
                break

            retvals_from_run = run_mcts_exploitation_step(params.model,
                                                          image,
                                                          params.TRUE_CLASS,
                                                          params.kp,
                                                          params.r,
                                                          backprop,
                                                          params.TOTAL_PLAYS)
            params.r = retvals_from_run[0]
            image = retvals_from_run[1]
            params.TOTAL_PLAYS = retvals_from_run[2]
            params.MISCLASSIFIED = retvals_from_run[3]
            if params.MISCLASSIFIED:
                cutoff_enforced = False
                break

    # 回溯：将找到的对抗样本撤销操作，直到他分类正确，计算最小的严重性
    def backtracking(adversarial_image, original_image,
                     manipulations, true_class, cluster=0, target_class=None):
        l_zero = len(manipulations)
        best_bad_example = copy.deepcopy(adversarial_image)
        pixels_at_a_time = cluster
        progress = 0
        for x, y in manipulations:
            if pixels_at_a_time != 0:
                adversarial_image[y][x] = original_image[y][x]
                pixels_at_a_time -= 1
                continue
            else:
                adversarial_image[y][x] = original_image[y][x]
                pixels_at_a_time = cluster
            pred, prob = params.predict(image)
            if pred != int(true_class):
                best_bad_example = copy.deepcopy(adversarial_image)
                # l_zero -= (cluster + 1)
                l_zero -= cluster
            else:
                adversarial_image = copy.deepcopy(best_bad_example)
            progress += 1
            if params.verbose:
                f = """Backtracking Step L_0: %s
                       Probability: %s Class: %s,
                       progress: %s/%s
                    """ % (l_zero, prob[0][pred],
                           pred, progress * cluster, len(manipulations))
                sys.stdout.write("\r" + str(f))
                sys.stdout.flush()
        return best_bad_example, manipulations, l_zero

    # for i in range(10):
    if params.verbose and not cutoff_enforced:
        print("Backtracking")
    # 找到了对抗样本 进行回溯
    if cutoff_enforced is False:
        # image, params.MANIPULATIONS, l_zero
        returned_array = backtracking(image,
                                      params.ORIGINAL_IMAGE,
                                      params.MANIPULATIONS,
                                      params.TRUE_CLASS,
                                      cluster=params.backtracking_constant)
        image = returned_array[0]
        params.MANIPULATIONS = returned_array[1]
        l_zero = returned_array[2]
    if params.verbose and not cutoff_enforced:
        print("\n Done backtracking")
    pred, prob = params.predict(image)
    # Output: adv_image, softmax_array, L0 Severity, kp_selection
    # 如果没找到对抗样本 (或该严重程度不是最小的) 则严重程度返回-1
    if cutoff_enforced:
        return image, prob, -1, params.r
    else:
        return image, prob, l_zero, params.r
