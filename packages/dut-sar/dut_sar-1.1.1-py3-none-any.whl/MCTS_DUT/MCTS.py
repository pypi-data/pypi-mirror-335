from operator import eq

import cv2
import numpy as np
from pomegranate import *
import copy
from copy import deepcopy

from torchvision import transforms

import DFMCS
from DFMCS import DFMCS
from DFMCS import DFMCS_Parameters
import math
import torch.nn.functional as F


# 通过计算每个结点在结点总UCB值中的占比 返回每个关键点被选中的概率
def RUN_UCB(keypoint_distribution, plays_per_node, TOTAL_PLAYS):
    retval = []
    # 遍历关键点
    for i in range(len(keypoint_distribution)):
        # 计算每个关键点的UCB值
        retval.append(keypoint_distribution[i] + math.sqrt(np.log(plays_per_node[i]) / TOTAL_PLAYS))
    # 转化为数组
    retval = np.asarray(retval)
    # sum函数对序列进行求和
    return retval / sum(retval)


class TreeNode(object):
    visited = False
    num_visits = 1
    # 每个结点的访问次数
    visits_per_node = []
    # 存储关键点
    lst = []
    # 选择关键点的概率
    dst = []
    # 层数
    lvl = []
    # 关键点下标
    id_num = 0

    def __init__(self, lst, dst, lvl, id_num, params):
        if (id_num == -1):
            self.kp_list = None
            self.kp_dist = None
            self.level = -1
            self.id = -1
        """ Creates an node object with a di"""
        # 关键点列表
        self.kp_list = lst
        # 关键点概率
        self.kp_dist = dst
        # 树的层数
        self.level = lvl
        # 当前结点的索引
        self.id = id_num
        # np.one():函数返回给定形状和数据类型的新数组
        # visits_per_node:一维数组，长度为关键点的数目
        self.visits_per_node = np.ones(len(lst))
        # 关键点相关数据
        self.params = params

    def selection(self):
        """ 从关键点列表中选择一个返回 """
        """ Returns a selection from the list of keypoints"""
        val = np.random.choice(range(len(self.kp_list)), p=self.kp_dist)
        self.visits_per_node[val] += 1
        return val

    # 选择UCB值最大的关键点
    def exploration(self):
        """ Returns a keypoint based on the UCB"""
        # 每个结点被选中的概率
        ucb = RUN_UCB(self.kp_dist, self.visits_per_node, self.num_visits)
        return np.random.choice(range(len(self.kp_list)), p=ucb)

    def visit_helper(self, k):
        """输入的k是关键点列表中的其中一个关键点 返回一个元组x, y，该元组对应于我们要操作的坐标"""
        """ Returns a tuple x,y that coresponds to the coords which we will 
        manipulate
        round() 方法返回浮点数x的四舍五入值
        """
        # k.pt[]:关键点的坐标 k.size: 该点的直径大小
        mu_x, mu_y, sigma = int(round(k.pt[0])), int(round(k.pt[1])), k.size
        # Remember, it may be wise to expand simga - greater varience = less honed attack
        sigma += self.params.SIGMA_CONSTANT
        d_x = NormalDistribution(mu_x, sigma)
        d_y = NormalDistribution(mu_y, sigma)
        # 归一化生成高斯混合模型
        x = d_x.sample()
        y = d_y.sample()
        if self.params.small_image:
            x /= self.params.inflation_constant
            y /= self.params.inflation_constant
        if x >= self.params.X_SHAPE:
            x = self.params.X_SHAPE - 1
        elif x < 0:
            x = 0
        if y >= self.params.Y_SHAPE:
            y = self.params.Y_SHAPE - 1
        elif y < 0:
            y = 0
        return int(x), int(y)

    # IMAGE, params.VISIT_CONSTANT, manipulation
    def visit(self, im, vc, manip_list):
        """ 返回修改后的图像和使用的操作指令的集合 """
        # vc 访问最大次数
        for i in range(vc):
            attempts = 0
            while True:
                if attempts == 5:
                    break
                # 将关键点高斯模糊后 获取要操作的点的 x,y 值
                x, y = self.visit_helper(self.kp_list[self.id])
                try:
                    # 如果x,y点还没有操作，并且该点不是白色的话，将该点设置为白色
                    if ((x, y) not in manip_list) and (list(self.params.MANIP(im, x, y)) != list(im[y][x])):
                        manip_list.append((x, y))
                        im[y][x] = self.params.MANIP(im, x, y)
                        attempts = 0
                        break
                    # x,y点操作过了，或者该点是白色，重新选择
                    else:
                        attempts += 1
                except:
                    if ((x, y) not in manip_list) and ((self.params.MANIP(im, x, y)) != (im[y][x])):
                        manip_list.append((x, y))
                        im[y][x] = self.params.MANIP(im, x, y)
                        attempts = 0
                        break
                    else:
                        attempts += 1
        return im, manip_list

    def visit_random(self, im, vc):
        val = np.random.choice(range(len(self.kp_list)), p=self.kp_dist)
        for i in range(vc):
            x, y = self.visit_helper(self.kp_list[val])
            im[y][x] = self.params.MANIP(im, x, y)
        return im

    # 反向传播
    # visited[i + 1].id, params.PROBABILITY - NEW_PROBABILITY, current_level + 1
    def backprop(self, index, reward, severity):
        """ Updates the distribution based upon the
        reward passed in
        根据传入的奖励更新分布
        """
        # severity /=10
        self.kp_dist[index] += (float(reward) / severity)
        if self.kp_dist[index] < 0:
            self.kp_dist[index] = 0
        self.kp_dist = self.kp_dist / sum(self.kp_dist)


def white_manipulation(val=None, dim=0, path=None):
    # # print("val: ", val)
    # if val is None:
    #     val = [255, 255, 255]
    # if not (val == [255, 255, 255]).any():
    #     return [255, 255, 255]
    # else:
    return [255, 255, 255]


def is_dark_pixel(image, x, y, threshold=128):
    # 转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 获取像素点的亮度值
    pixel_brightness = gray_image[y, x]
    # print(pixel_brightness)

    if pixel_brightness < threshold:
        new_pixel_value = np.random.randint(1, 128, size=3)
    elif pixel_brightness >= threshold:
        new_pixel_value = np.random.randint(129, 255, size=3)
    else:
        raise ValueError("Pixel value is out of range.")

    # 判断像素点的亮度值是否小于阈值
    return new_pixel_value


class MCTS_Parameters(object):
    def __init__(self, image, true_class, model, predshape=(1, 3, 224, 224)):
        self.model = model
        # copy.deepcopy()是深拷贝，会拷贝对象及其子对象，哪怕以后对其有改动，也不会影响其第一次的拷贝
        # 拷贝图片
        self.ORIGINAL_IMAGE = copy.deepcopy(image)
        # 图像的正确分类
        self.TRUE_CLASS = true_class
        self.MANIP = white_manipulation
        # 总访问次数
        self.VISIT_CONSTANT = 50
        # sigma常数
        self.SIGMA_CONSTANT = 15
        # xy是图片长度
        self.X_SHAPE = image.shape[0]
        self.Y_SHAPE = image.shape[1]
        # 之前的形态
        self.predshape = predshape
        self.QUERY = 0
        self.kp, self.des, self.r = [], [], []
        self.verbose = False
        self.small_image = False
        self.inflation_constant = 15
        # 仿真终止
        self.simulations_cutoff = 10

        # 更改数组的形态
        def preproc(im):
            trans_val = transforms.Compose(
                [transforms.ToTensor(),
                 transforms.Resize((224, 224))
                 ])
            im_pred = trans_val(im).unsqueeze(0)
            return im_pred

        self.preprocess = preproc

        def predi(im):
            im_pred = self.preprocess(im)
            # predict是训练后返回预测结果，是标签值
            prob = self.model(im_pred)
            prob = F.softmax(prob, dim=1).detach().numpy()
            # b=np.argmax(a)#取出a中元素最大值所对应的索引，此时最大值位6，其对应的位置索引值为4，（索引值默认从0开始）
            pred = np.argmax(np.asarray(prob))
            self.QUERY += 1
            return pred, prob

        self.predict = predi
        pred, prob = self.predict(image)
        self.PROBABILITY = max(max(prob))
        self.backtracking_constant = 10

        # def check_query():
        #     return self.QUERY


def SIFT_Filtered(image, parameters, threshold=0.00):
    # We need to expand the image to get good keypoints
    # parameters 原始图像
    if parameters.small_image:
        xs = parameters.X_SHAPE * parameters.inflation_constant
        ys = parameters.Y_SHAPE * parameters.inflation_constant
        image = cv2.resize(image, (xs, ys))
    orb = cv2.ORB_create()
    # 寻找关键点
    kp1 = orb.detect(image)
    # 计算描述符
    kp, des = orb.compute(image, kp1)  # 计算哪张图片的用哪张图片的关键点。

    # 画出关键点
    # outimg1 = cv2.drawKeypoints(image, keypoints=kp, outImage=None)

    # 这里是把两张图片在同一个窗口中显示。
    # outimg3 = np.hstack([outimg1, outimg2])
    # cv2.imshow("Key Points", outimg1)
    # cv2.waitKey(0)
    # # FILTER RESPONSES:
    responses = []
    for x in kp:
        responses.append(x.response)
    responses.sort()
    ret = []
    index_tracker = 0
    for x in kp:
        if x.response >= threshold:
            ret.append((x, des[index_tracker], x.response))
        index_tracker = index_tracker + 1
    retval = sorted(ret, key=lambda tup: tup[2])
    return zip(*retval)


def MCTS(params):
    ATTACK_SUCCESS = True
    # 特征提取
    params.kp, params.des, params.r = SIFT_Filtered(params.ORIGINAL_IMAGE, params)
    params.r = np.asarray(params.r)
    # 计算关键点响应强度占总比
    params.r = params.r / sum(params.r)
    # lst, dst, lvl, id_num, params
    root = TreeNode(params.kp, params.r, 0, 0, params)
    # 保存每一层中包含的节点信息
    levels = [[root]]
    current_level = 0
    node = root
    manipulation = []
    # 存储访问过的树节点
    visited = [root]
    IMAGE = copy.deepcopy(params.ORIGINAL_IMAGE)
    # 总遍历次数
    raw_searches = params.simulations_cutoff
    count_searches = 0
    min_severity = -1
    best_image = None
    MISCLASSIFIED = False
    severities_over_time = []
    raw_severities = []
    avg_severities = []
    count_prior_saturation = 0
    while True:
        # print(count_searches) 循环超过35次结束仿真
        print("count_searches：%d" % count_searches)
        if count_searches == raw_searches:
            break
        count_searches += 1
        explored = False
        # 选择UCB值最大的关键点
        nxt = node.exploration()
        # First, we need to make sure that the layer we are going to
        # initialize even exists
        try:
            test = levels[current_level + 1]
        # 情况一：访问新的一层：创建新的一层结点，并使用初始化要访问的结点，进入访问，访问结束（找到对抗样本）后回到根节点，并进入情况二
        # 情况二：选择的节点还没有被访问过：进入对应的层并初始化结点，进入访问，访问结束（找到对抗样本）后回到根节点，选择下一个要操作的关键点，若选到的关键点之前被访问过，则进入情况三
        # 情况三：选择的结点被访问过：进入该节点进行操作仿真
        # 对以上三种情况进行详细说明
        # —————————————————————————————————————————————————————
        # 循环的出口：
        # 情况一：到达指定迭代次数，循环结束，返回操作次数最少的严重程度；
        # 情况二：
        # —————————————————————————————————————————————————————
        # 如果树中还没有该层 则创建新一层
        except:
            # 扩展结点 创建与图片关键点个数相同的一层结点
            # If the layer does not exist, then we create the layers
            levels.append([TreeNode(params.kp, params.r, -1, -1, params) for i in range(len(params.kp))])
            if params.verbose:
                print("Exploring new keypoints on a new layer: %s on node: %s" % (current_level + 1, nxt))

            # Initialize the new node in the tree
            # levels 中存储的是节点
            # 每一层存储的结点都是关键点 根据ucb计算出的值作为索引找到下一个将要操作的关键点
            levels[current_level + 1][nxt] = TreeNode(params.kp, params.r, current_level + 1, nxt, params)
            IMAGE, manipulation = levels[current_level + 1][nxt].visit(IMAGE, params.VISIT_CONSTANT, manipulation)
            # visited中放的是结点
            visited.append(levels[current_level + 1][nxt])

            # Visit the new node
            pred, prob = params.predict(IMAGE)
            NEW_PROBABILITY = prob[0][pred]
            print("预处理后的分类：", pred)
            # 分类错误 跳出循环
            if pred != int(params.TRUE_CLASS):
                print("随机处理阶段分类错误，跳出循环，分类为：%s" % pred)
                adv = copy.deepcopy(IMAGE)
                best_image = copy.deepcopy(adv)
                min_severity = len(manipulation)
                MISCLASSIFIED = True
                break

            # Generate a DFS Adversarial example
            # 操作指令集的长度就是对抗样本与原始图像的距离
            prior_severity = len(manipulation)
            print("prior severity = " + str(prior_severity))
            if prior_severity > min_severity:
                count_prior_saturation += 1

            if MISCLASSIFIED:
                print("Satisfied before simulation")
                adv = copy.deepcopy(IMAGE)
                softmax = copy.deepcopy(prob)
                severity = prior_severity

            else:
                dparams = DFMCS_Parameters(params, IMAGE)
                adv, softmax, severity, kpd = DFMCS(dparams, cutoff=min_severity)
                # 找到严重程度更小的点
                if severity != -1:
                    severity += prior_severity
                # 对该关键点周围像素进行修改后未找到对抗样本且总访问次数为1 为什么这种情况下就结束循环？？？？
                # 一次迭代没找到对抗样本 说明该图像没有对抗样本
                elif severity == -1 and count_searches == 1:
                    print("攻击失败！")
                    ATTACK_SUCCESS = False
                    break
            if (severity < min_severity or min_severity == -1) and severity != -1:
                severities_over_time.append(severity)
                min_severity = severity
                best_image = copy.deepcopy(adv)
            else:
                severities_over_time.append(min_severity)

            if severity != -1:
                raw_severities.append(severity)
            else:
                raw_severities.append(min_severity)

            avg_severities.append(np.average(raw_severities[-10:]))

            if params.verbose == True:
                print("Back propogating and restarting search. Current Severity: %s" % (severity))
                print("Best severity: %s" % (min_severity))
                print("=================================================================\n")
            # Backprop
            for i in range(len(visited)):
                if i == (len(visited) - 1):
                    break
                else:
                    visited[i].backprop(visited[i + 1].id, params.PROBABILITY - NEW_PROBABILITY, current_level + 1)

            IMAGE = copy.deepcopy(params.ORIGINAL_IMAGE)
            current_level = 0
            visited = [root]
            manipulations = []
            # 退回根结点 访问另一个节点
            node = root
            explored = True
        # 如果有该层，但是该关键点对应的节点还没有被访问 更新当前访问节点的相关信息：所在层数以及下一个要访问的结点
        if not explored:
            adv_list = []
            # 当前结点已经访问过了 则转下一种情况
            if not (levels[current_level + 1][nxt].id == -1):
                pass
            else:
                if params.verbose == True:
                    print("Exploring new keypoints on an existing layer: %s on node: %s" % (current_level + 1, nxt))

                # Initialize the new node in the tree
                levels[current_level + 1][nxt] = TreeNode(params.kp, params.r, current_level + 1, nxt, params)
                IMAGE, manipulation = levels[current_level + 1][nxt].visit(IMAGE, params.VISIT_CONSTANT, manipulation)
                visited.append(levels[current_level + 1][nxt])
                print("prior severity = " + str((current_level + 1) * params.VISIT_CONSTANT))
                pred, prob = params.predict(IMAGE)
                print("IMAGE分类：", pred)
                NEW_PROBABILITY = prob[0][pred]
                if pred != int(params.TRUE_CLASS):
                    MISCLASSIFIED = True
                    break

                # Generate a DFS Adversarial example
                prior_severity = (current_level + 1) * params.VISIT_CONSTANT
                if prior_severity > min_severity:
                    count_prior_saturation += 1

                if MISCLASSIFIED:
                    adv = copy.deepcopy(IMAGE)
                    adv_list.append(adv)  # 添加反例
                    softmax = copy.deepcopy(prob)
                    severity = prior_severity
                else:
                    dparams = DFMCS_Parameters(params, IMAGE)
                    adv, softmax, severity, kpd = DFMCS(dparams, cutoff=min_severity)
                    if severity != -1:
                        severity += prior_severity
                # 当算法在某些迭代中没有找到对抗性的例子时，我们让算法返回最小的严重程度
                # severities_over_time保存最小的严重程度
                if (severity < min_severity or min_severity == -1) and severity != -1:
                    severities_over_time.append(severity)
                    min_severity = severity
                    best_image = copy.deepcopy(adv)
                else:
                    severities_over_time.append(min_severity)

                # raw_severities保存每次的严重程度
                if severity != -1:
                    raw_severities.append(severity)
                else:
                    raw_severities.append(min_severity)

                # 近十次平均严重程度 画图要用
                avg_severities.append(np.average(raw_severities[-10:]))

                if params.verbose == True:
                    print("Back propogating and restarting search. Current Severity: %s" % (severity))
                    print("Best severity: %s" % (min_severity))
                    print("=================================================================\n")

                for i in range(len(visited)):
                    if i == (len(visited) - 1):
                        break
                    else:
                        visited[i].backprop(visited[i + 1].id, params.PROBABILITY - NEW_PROBABILITY, current_level + 1)

                # 找到对抗样本并更新该路径的奖励值之后 退回第一层重新开始蒙特卡洛树操作
                IMAGE = copy.deepcopy(params.ORIGINAL_IMAGE)
                current_level = 0
                visited = [root]
                manipulations = []
                node = root
                explored = True
        # 如果该关键点对应的节点存在(选中之前访问过的点)，则进入访问
        # 此时manipulation中保存着之前的操作
        if not explored:
            if params.verbose == True:
                print("manipulating and continuing the search: %s" % (nxt))
            # Visit this node 访问这个节点的下一个节点时 不算入循环次数
            count_searches -= 1
            IMAGE, manipulation = levels[current_level + 1][nxt].visit(IMAGE, params.VISIT_CONSTANT, manipulation)
            print("prior severity = " + str(len(manipulation)))
            # Predict image class
            pred, prob = params.predict(IMAGE)
            NEW_PROBABILITY = prob[0][pred]
            if pred != int(params.TRUE_CLASS):
                MISCLASSIFIED = True
                break

            visited.append(node)
            # 将当前访问的节点作为父节点
            node = levels[current_level + 1][nxt]
            current_level = current_level + 1
        # 如果当前严重性程度大于最小严重程度的次数 超过关键点的个数，结束循环
        if count_prior_saturation >= float(len(params.kp)):
            break

    if best_image is not None:
        pred, prob = params.predict(best_image)
        print("best_image:", pred)
        NEW_PROBABILITY = prob[0][pred]

    else:
        pred, prob = params.predict(IMAGE)
        NEW_PROBABILITY = prob[0][pred]
        best_image = params.ORIGINAL_IMAGE
        min_severity = 0

    stats = (severities_over_time, raw_severities, avg_severities)

    return best_image, min_severity, pred, stats, params.QUERY, ATTACK_SUCCESS
