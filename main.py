import sys
import re
from xpinyin import Pinyin
import time

'''
time1 = time.time()
# 开始计时

    def addSensitiveWords(self, keyword):
        # 生成敏感词树
            keyword = keyword.lower()
            chars = keyword.strip()
            if not chars:
                return
            level = self.keyword_chains
            for i in range(len(chars)):
                if chars[i] in level:
                    level = level[chars[i]]
                else:
                    if not isinstance(level, dict):
                        break
                    for j in range(i, len(chars)):
                        level[chars[j]] = {}
                        last_level, last_char = level, chars[j]
                        level = level[chars[j]]
                    last_level[last_char] = {self.delimit: 0}
                    break
                if i == len(chars) - 1:
                    level[self.delimit] = 0
'''


class Node(object):

    def __init__(self):
        self.children = dict()
        # 敏感词组合序列
        self.length = 0
        self.word = ""
        self.org = ""
        self.fail = None
        self.tail = None


'''class BTree:
    def __init__(self, value):
        self.left = None
        self.data = value
        self.right = None

    def insertLeft(self, value):
        self.left = BTree(value)
        return self.left

    def insertRight(self, value):
        self.right = BTree(value)
        return self.right

    def show(self):
        print(self.data)
'''

class Trie(object):

    def __init__(self):
        self.root = Node()
        # 处理汉字拼音
        self.q_worker = Pinyin()
        # 存放汉字
        self.phrase_list = []
        # 存放匹配的组合内容
        self.smatrix = []
        # 存放相关的词组序列
        self.combination = []


    def printq(self):
        print('这题好难QAQ')

    def prepareWork(self, phraselist):

        for index, phrase in enumerate(phraselist):
            if index == len(phraselist) - 1:
                self.changejvzhen(phrase)
            else:
                self.changejvzhen(phrase[:-1])

            for word in self.phrase_list:
                if index == len(phraselist) - 1:
                    self.trietree(word, phrase)
                else:
                    self.trietree(word, phrase[:-1])
        self.make_fail()

    def changejvzhen(self, phrase):
        # 转换为矩阵
        for letter in phrase:
            self.smatrix.append(['[' + self.q_worker.get_pinyin(letter).replace('-', '') + ']',
                                 self.q_worker.get_pinyin(letter).replace('-', ''),
                                 str.lower(self.q_worker.get_initials(letter).replace('-', ''))])
        self.insertKey(len(phrase))

    def dgInsertKey(self, row_now: int, layer: int, phrase: str):
        # 递归建树
        if row_now == layer:
            self.phrase_list.append(phrase)
            return
        else:
            for column_now in range(0, 3):
                self.dgInsertKey(row_now + 1, layer,
                                 phrase + self.smatrix[row_now][column_now])


    def func(name, *numbers):
        print(name)
        print(numbers)

    def func(name, **kvs):
        print(name)
        print(kvs)


    def insertKey(self, layer: int):
        # 递归建树
        self.dgInsertKey(0, layer, "")
        self.smatrix.clear()


    def trietree(self, phrase, initial: str):
        # 字典树
        tmp_root = self.root
        # 判断
        makeup = ''
        length = 0
        together = 0

        for i in range(0, len(phrase)):
            # 添加重组的拼音串
            if phrase[i] == '[':
                together = True
                continue
            if phrase[i] == ']':
                together = False
                length += 1
                if makeup not in tmp_root.children:
                    node = Node()
                    node.word = makeup
                    tmp_root.children.update({makeup: node})
                tmp_root = tmp_root.children[makeup]
                # 转换成子节点
                makeup = ""
                continue

            if together:
                makeup += phrase[i]
                continue
            else:

                makeup = phrase[i]
                length += 1
                if makeup not in tmp_root.children:
                    node = Node()
                    node.word = makeup
                    tmp_root.children.update({makeup: node})
                # 都转换成子节点
                tmp_root = tmp_root.children[makeup]
                makeup = ""

        if tmp_root.org == "":
            # 为当前末尾节点添加源词
            tmp_root.org = initial
        # 为当前末尾节点添加当前敏感词组合序列的长度
        tmp_root.length = length

    def make_fail(self):
        tmp_queue = [self.root]
        while len(tmp_queue) != 0:
            # 开始遍历子节点
            childroot = tmp_queue.pop(0)

            # 判断子节点与根节点
            for key, value in childroot.children.items():
                if childroot != self.root:
                    q = childroot.fail
                    while q is not None:
                        if key in q.children:
                            childroot.children[key].fail = q.fail
                            break
                        q = q.fail
                    if q is None:
                        childroot.children[key].fail = self.root
                else:
                    childroot.children[key].fail = self.root

                tmp_queue.append(childroot.children[key])

    def searchorg(self, jvzi, line):
        # 查找
        tmp = self.root
        temps = []
        # temps用于存储相应的下标
        for index, letter in enumerate(jvzi):
            if self.noWord(letter):
                continue
            letter = self.q_worker.get_pinyin(letter).replace('-', '')
            while tmp.children.get(str.lower(letter)) is None and tmp.fail is not None:
                tmp = tmp.fail
            # 开始匹配
            if tmp.children.get(str.lower(letter)) is not None:
                tmp = tmp.children.get(str.lower(letter))
            # 没有检测到，跳出循环，检索下个字符
            else:
                continue

            if tmp.length:

                first_start = self.pipei(node=tmp, org1=jvzi, position=index, line=line)
                if len(temps):
                    if first_start == temps[len(temps) - 1]:
                        self.combination.pop(len(self.combination) - 2)
                temps.append(first_start)

    def pipei(self, node, org1, position, line: int) -> int:

        words_length = node.length
        pipeisection = ""

        while words_length:

            if self.noWord(org1[position]):
                pipeisection = pipeisection + org1[position]

            else:
                pipeisection = pipeisection + org1[position]
                words_length -= 1
            position = position - 1
        pipeisection = pipeisection[::-1]

        for letter in pipeisection:
            if '\u4e00' <= letter <= '\u9fff':
                # \u4e00-\u9fff是中文范围
                digit_contain = bool(re.search(r'\d', pipeisection))
                if digit_contain:
                    return -1
        self.combination.append("Line" + str(line) + ": <" + node.org + "> " + pipeisection)
        return position

    @staticmethod
    def noWord(letter) -> bool:
        if letter in "0123456789[\"`~!@#$%^&*()+=|{}':;',\\.<>/?~！@#￥%……&*（）——+| {}【】‘；：”“’。，、？_] \n":
            return True
        return False

    # 输出
    def writetext(self, file_name):
        file = open(file_name, "a", encoding="utf-8")
        file.write("Total: " + str(len(self.combination)) + "\n")
        for element in self.combination:
            file.write(element + "\n")
        file.close()
        pass

args = sys.argv

if len(args) != 4:
    print("wrong")
    exit(-1)

theAcTrie = Trie()
work_line = []

try:
    # 打开敏感词文件
    file = open(args[1], encoding="utf-8")
    word_line = file.readlines()
    file.close()

    # 敏感词插入
    theAcTrie.prepareWork(word_line)

    # 打开待检测文件
    file = open(args[2], encoding="utf-8")
    contents = file.readlines()
    file.close()

    # 开始匹配
    for line, content in enumerate(contents):
        theAcTrie.searchorg(content, line + 1)

    theAcTrie.writetext(args[3])
    # 输出
except FileNotFoundError:
    print("not exit")

'''
if __name__ == "__main__":
    time2 = time.time()
    print('总共耗时:' + str(time2 - time1) + 's')
    # 运行程序总耗时
'''