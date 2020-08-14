
class Edge():
    key_incr:int = 0

    def __init__(
        self,
        v_start:int,
        v_end:int,
        nb_members:int,
        s_born: int = 0,
        num:int = None,
    ):
        self.__key: int = Edge.key_incr
        self.__num = num
        self.v_start = v_start
        self.v_end = v_end
        self.nb_members = nb_members
        self.__s_death = -1
        self.s_born = s_born
        self.__ratio_life = None
        self.__ratio_members = None
        Edge.key_incr += 1

    @property
    def s_born(self):
        return(self.__s_born)

    @property
    def s_death(self):
        return(self.__s_death)

    @property
    def key(self):
        return self.__key

    @property
    def num(self):
        return self.__num

    @property
    def nb_members(self):
        return self.__nb_members

    @property
    def v_start(self):
        return self.__v_start

    @property
    def v_end(self):
        return self.__v_end

    @property
    def ratio_life(self):
        return self.__ratio_life

    @property
    def ratio_members(self):
        return self.__ratio_members

    @ratio_members.setter
    def ratio_members(self, ratio_members):
        if (ratio_members > 1) or (ratio_members < 0):
            raise ValueError("ratio should be within 0-1 range")
        self.__ratio_members = ratio_members


    @ratio_life.setter
    def ratio_life(self, ratio_life):
        if (ratio_life > 1) or (ratio_life < 0):
            raise ValueError("ratio should be within 0-1 range")
        self.__ratio_life = ratio_life

    @s_born.setter
    def s_born(self, s_born):
        if s_born is not None:
            if (s_born < 0):
                raise ValueError("s should be > 0")
            self.__s_born = int(max(s_born, 0))

    @s_death.setter
    def s_death(self, s_death):
        if s_death is not None:
            if (s_death < 0):
                raise ValueError("s should be > 0")
            self.__s_death = int(max(s_death, 1))

    @v_start.setter
    def v_start(self, v_start):
        if v_start is not None:
            if (v_start < 0):
                raise ValueError("v should be > O")
            self.__v_start = int(abs(v_start))

    @v_end.setter
    def v_end(self, v_end):
        if v_end is not None:
            if (v_end < 0):
                raise ValueError("v should be > O")
            self.__v_end = int(abs(v_end))

    @num.setter
    def num(self, num):
        if num is not None:
            if (num < 0):
                raise ValueError("num should be > O")
            self.__num = int(abs(num))

    @nb_members.setter
    def nb_members(self, nb_members):
        if nb_members is not None:
            if (nb_members < 0):
                raise ValueError("number should be > O")
            self.__nb_members = int(abs(nb_members))

