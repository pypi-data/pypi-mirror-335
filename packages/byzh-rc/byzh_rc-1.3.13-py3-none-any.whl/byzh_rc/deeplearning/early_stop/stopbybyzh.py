from ..early_stop import BStopByAcc, BStopByLoss
from ..early_stop import BStopByAccDelta, BStopByLossDelta
from ..early_stop import BStopByOverfitting

class BStopByBYZH:
    def __init__(self, rounds=10, loss_delta=0.002, acc_delta=0.003):
        '''
        BStopByBYZH 是一个综合早停策略的实现，通过结合多个早停条件判断是否终止训练。

        参数:
        - rounds (int): 用于每种策略的轮次，决定观察的历史轮次数量，默认为 10。
        - loss_delta (float): 损失函数变化的阈值，当损失函数变化小于该值时触发早停，默认为 0.002。
        - acc_delta (float): 精度变化的阈值，当准确率变化小于该值时触发早停，默认为 0.003。

        该类通过以下几个早停策略来判断是否终止训练:
        1. 基于损失函数变化的早停策略 (`BStopByLossDelta`).
        2. 基于准确率变化的早停策略 (`BStopByAccDelta`).
        3. 基于过拟合的早停策略 (`BStopByOverfitting`).
        4. 基于损失函数和准确率的变化幅度来决定是否停止训练。

        每个策略根据训练的损失值、训练准确度和验证准确度进行检查，并根据不同条件来更新标志（`flags`），当任意一个策略触发时，即可停止训练。
        '''
        self.rounds = rounds
        self.loss_delta = loss_delta
        self.acc_delta = acc_delta
        self.flags = [False, False, False, False]

        self.stop_by_loss = BStopByLoss(rounds=rounds, delta=loss_delta)
        self.stop_by_loss_delta = BStopByLossDelta(rounds=rounds, delta=loss_delta)
        self.stop_by_acc = BStopByAcc(rounds=rounds, delta=acc_delta)
        self.stop_by_acc_delta = BStopByAccDelta(rounds=rounds, delta=acc_delta)
        self.stop_by_overfitting = BStopByOverfitting(rounds=rounds, delta=0.1)

    def __call__(self, train_loss, train_acc, val_acc):

        flag1 = self.stop_by_acc(val_acc)
        flag2 = self.stop_by_acc_delta(val_acc)
        self.flags[0] = flag1 or flag2

        self.flags[1] = self.stop_by_loss(train_loss)
        self.flags[2] = self.stop_by_loss_delta(train_loss)

        self.flags[3] = self.stop_by_overfitting(train_acc, val_acc)

        # 统计self.flags中True的个数
        count = sum(self.flags)
        if count >= 3:
            return True

        return False



