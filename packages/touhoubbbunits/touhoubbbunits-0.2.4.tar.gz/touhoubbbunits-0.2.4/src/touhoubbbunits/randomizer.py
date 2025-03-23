def rd():
    from random import randint
    import tkinter as tk
    import touhoubbbunits as bbb
    bingzhong_list=bbb.UNIT_LIST
    #随机自机系统
    def random_ziji():
        x=randint(0,110)%11
        ziji_list=["八云紫","灵梦","魔理沙","天子","蕾米","阿空","永琳","早苗","幽幽子","⑨","幽香"]
        window.update()
        output[0].insert(0,ziji_list[x])
    #涉及兵种随机的总控制函数
    def controller(t):
        #初始化临时空集合，用于保证全随机不重复
        temp_set=set()
        #随机选出一个兵种，添加到临时集合
        def random_bingzhong():
            y=randint(0,10*len(bingzhong_list))%len(bingzhong_list)
            temp_set.add(bingzhong_list[y])
        #用于生产全随机函数的内函数
        def wd_rd(_,_1):
            for i in range(_):
                while _1-len(temp_set):
                    random_bingzhong()
                output[i].insert(0,list(temp_set))
                temp_set.clear()
        #内函数，用于在写入前清空文本框
        def del_wrapper():
            for each in output:
                each.delete(0,"end")
            #内函数，用于判断，在不同情况下生产不同的函数
            def func():
                #随机自机
                if t=="ziji":
                    return random_ziji()
                #随机兵种
                elif t=="bz":
                    def wd_bz():
                        random_bingzhong()
                        output[0].insert(0,list(temp_set))
                        temp_set.clear()
                    return wd_bz()
                #随机自机+兵种
                elif t=="zb":
                    def wd_zjbz():
                        random_bingzhong()
                        output[0].insert(0,list(temp_set))
                        temp_set.clear()
                        output[0].insert(0,"  ")
                        random_ziji()
                    return wd_zjbz()
                #11全随机
                elif t=="random":
                    return wd_rd(2,9)
                #22全随机
                elif t=="random22":
                    return wd_rd(4,6)
                    
                
            #返回加上判断条件的函数    
            return func()
        #返回一个函数对象，command的输入实质上是del_wrapper
        return del_wrapper 
        
    #创建主窗口
    window=tk.Tk()
    window.title("BBB随机器")
    window.geometry("537x332")
    #得到主窗口大小
    window.update()
    wd=window.winfo_width()
    hi=window.winfo_height()
    #创建文本标识
    label = tk.Label(window, text="东方大战争随机器",)
    label.pack()
    #创建右侧框体
    right=tk.LabelFrame(window,text="随机选项")
    right.place(anchor="ne",x=wd,y=0.1*hi,height=0.9*hi,width=0.75*wd)
    #创建右侧框的输出部分
    output=[tk.Entry(right,width=54,justify="center") for i in range(4)]
    for each in output:
        each.pack(expand=True)

    #创建左侧框体
    left=tk.LabelFrame(window,text="随机结果")
    left.place(anchor="nw",x=0,y=0.1*hi,height=0.9*hi,width=0.25*wd)
    #创建左侧按钮
    tk.Button(left, text="随机自机",width=8,command=controller("ziji")).pack(expand=True)
    tk.Button(left, text="随机兵种",width=8,command=controller("bz")).pack(expand=True)
    tk.Button(left, text="随机自机+兵种",width=12,command=controller("zb")).pack(expand=True)
    tk.Button(left, text="11全随机",width=8,command=controller("random")).pack(expand=True)
    tk.Button(left, text="22全随机",width=8,command=controller("random22")).pack(expand=True)

    #启动循环
    window.mainloop()