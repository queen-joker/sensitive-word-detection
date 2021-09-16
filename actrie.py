import re
from xpinyin import Pinyin

class Node(object):

    def __init__(self):
        self.children = dict()
        # 敏感词组合序列
        self.length = 0
        self.word = ""
        self.org = ""
        self.fail = None
        self.tail = None


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

    def changejvzhen(self, phrase):
        # 转换为矩阵
        for letter in phrase:
            self.smatrix.append(['['+self.q_worker.get_pinyin(letter).replace('-', '')+']',
                                    self.q_worker.get_pinyin(letter).replace('-', ''),
                                    str.lower(self.q_worker.get_initials(letter).replace('-', ''))])
        self.insertKey(len(phrase))

    def prepareWork(self, phraselist):

        for index, phrase in enumerate(phraselist):
            if index != len(phraselist) - 1:
                self.str2matrix(phrase[:-1])
            else:
                self.str2matrix(phrase)

            for word in self.phrase_list:
                if index != len(phraselist) - 1:
                    self.build_tree(word, phrase[:-1])
                else:
                    self.build_tree(word, phrase)
        self.make_fail()


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



    def dgInsertKey(self, row_now: int, layer: int, phrase: str):
        # 递归建树
        if row_now == layer:
            self.phrase_list.append(phrase)
            return
        else:
            for column_now in range(0, 3):
                self.dgInsertKey(row_now + 1, layer,
                                        phrase + self.smatrix[row_now][column_now])

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
                length += 1
                makeup = phrase[i]
                if makeup not in tmp_root.children:
                    node = Node()
                    node.word = makeup
                    tmp_root.children.update({makeup: node})
                # 都转换成子节点
                tmp_root = tmp_root.children[makeup]
                makeup = ""

        if tmp_root.source == "":
            # 为当前末尾节点添加源词
            tmp_root.source = initial
        # 为当前末尾节点添加当前敏感词组合序列的长度
        tmp_root.length = length


    def make_fail(self):
        tmp_queue = [self.root]
        while len(tmp_queue) != 0:
            # 开始遍历子节点
            childroot = tmp_queue.pop(0)
            q = None
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

    def noWord(letters) -> bool:
        if letters in "0123456789[\"`~!@#$%^&*()+=|{}':;',\\.<>/?~！@#￥%……&*（）——+| {}【】‘；：”“’。，、？_] \n":
            return True
        return False



    def searchorg(self, sentence, line):
        # 查找
        tmp = self.root
        temps = []
        # temps用于存储相应的下标
        for index, letter in enumerate(sentence):
            if self.noWord(letters):
                continue
            letters = self.q_worker.get_pinyin(letters).replace('-', '')
            while tmp.children.get(str.lower(letters)) is None and tmp.fail is not None:
                tmp = tmp.fail
            # 开始匹配
            if tmp.children.get(str.lower(letters)) is not None:
                tmp = tmp.children.get(str.lower(letters))
            # 没有检测到，跳出循环，检索下个字符
            else:
                continue

            if tmp.length:
                # 判断上一敏感词是否属于当前原文敏感词内容
                first_start = self.pipei(node=tmp, org1=sentence, position=index, line=line)
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
                matched_part = pipeisection + org1[position]
                words_length -= 1
            position = position-1
        pipeisection = pipeisection[::-1]

        for letter in pipeisection:
            if '\u4e00' <= letter <= '\u9fff':
                # \u4e00-\u9fff是中文范围
                digit_contain = bool(re.search(r'\d', pipeisection))
                if digit_contain:
                    return -1
        self.combination.append("Line" + str(line) + ": <" + node.source + "> " + pipeisection)
        return position

    #输出
    def writetext(self, file_name):
        file = open(file_name, "a", encoding="utf-8")
        file.write("Total: " + str(len(self.combination)) + "\n")
        for element in self.combination:
            file.write(element + "\n")
        file.close()
        pass

'''
        # 过滤敏感词
        def filterSensitiveWords(self, message, repl="*"):
            message = message.lower()
            ret = []
            start = 0
            while start < len(message):
                level = self.keyword_chains
                step_ins = 0
                message_chars = message[start:]
                for char in message_chars:
                    if char in level:
                        step_ins += 1
                        if self.delimit not in level[char]:
                            level = level[char]
                        else:
                            ret.append(repl * step_ins)
                            start += step_ins - 1
                            break
                    else:
                        ret.append(message[start])
                        break
                start += 1

            return ''.join(ret)
'''

'''
if __name__ == "__main__":
    test_words = ["盗版", "垃圾"]
    test_text = "拉圾网站，我这里有盗@#版软件。"
    model = Trie()
    model.prepareWork(test_words)
    model.search(test_text, 1)
    model.writeFile('ans.txt')
    result = gfw.filterSensitiveWords(text)
	print(result)
'''