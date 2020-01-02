import time
def fmz_trading(tp,signal, leverage, stock_value,hold_ratio):
    '''
    :param tp:  交易类型
    :param signal:  信号
    :param price: 现价
    :param leverage: 杠杆倍数
    :param stock_value: 一张合约价值
    :param hold_ratio: 仓位
    :return:
    '''
    ###########   仓位信息返回   ####################

    def mark_hold_ms():
        global dc
        hold_ms = exchange.GetPosition()  # 仓位信息返回 list
        dc = {'short': 0, 'long': 0}
        for i in hold_ms:
            if i['Type'] == 1:
                dc['short'] = i['Amount']
                dc['short_price'] = i['Price']
            if i['Type'] == 0:
                dc['long'] = i['Amount']
                dc['long_price'] = i['Price']
        return dc

    ############# 持仓量计算,买卖函数  ############################

    def calculate_amout( ):
        Account = exchange.GetAccount()
        stock_margin = Account['Stocks']
        ticker = exchange.GetTicker()  # 获取当前行情
        currSell1Price = ticker.Sell  # 拿到当前卖一价格
        will_hold = int(stock_margin * currSell1Price * leverage / stock_value)
        hold_diff = int(will_hold * hold_ratio)
        return hold_diff

    def buy_long(price,ratio=1.01,order_Amount=0):
        exchange.SetDirection("buy")  # 设置交易方向和类型
        if order_Amount==0:
            order_id =exchange.Buy(price * ratio, calculate_amout())  # 开多单
        elif order_Amount!=0:
            order_id = exchange.Buy(price * ratio, order_Amount)  # 开多单
        return order_id

    def sell_short(price,ratio=0.99,order_Amount=0):
        exchange.SetDirection("sell")  # 设置交易方向和类型
        if order_Amount == 0:
            order_id =exchange.Sell(price * ratio, calculate_amout())  # 开空单
        elif order_Amount != 0:
            order_id = exchange.Sell(price * ratio, order_Amount)  # 开空单
        Log('开空', price * 0.99)
        return order_id

    def sell_long(price,ratio=0.99,order_Amount=0):
        exchange.SetDirection("closebuy")  # 设置交易方向和类型
        if order_Amount == 0:
            order_id =exchange.Sell(price *ratio, dc['long'] )  # 卖出平多单
        elif order_Amount != 0:
            order_id = exchange.Sell(price * ratio, order_Amount)  # 卖出平多单
        Log('平多', price * 0.99)
        return order_id

    def buy_short(price,ratio=1.01,order_Amount=0):
        exchange.SetDirection("closesell")  # 设置交易方向和类型
        if order_Amount == 0:
            order_id = exchange.Buy(price * ratio, dc['short'] )  # 买入平空单
        elif order_Amount != 0:
            order_id = exchange.Buy(price * ratio, order_Amount)  # 买入平空单
        Log('平空', price * 1.01)
        return order_id

    ############# 价格  ############################
    def sell_buy_price():
        ticker = exchange.GetTicker()  # 获取当前行情
        currSell1Price = ticker.Sell  # 拿到当前卖一价格
        currBuy1Price = ticker.Buy  # 拿到当前买一价格
        return currSell1Price,currBuy1Price
    def calculate_amount(order_id):
        order_mg = exchange.GetOrder(order_id )
        return order_mg.Amount - order_mg.DealAmount,order_mg.Price

    ############# 买卖  ############################

    if tp==0: # 吃单成交
        mark_hold_ms() #标记多空仓位
        ticker = exchange.GetTicker()  # 获取当前行情
        Last_Price = ticker.Last  # 拿到当前卖一价格
        if signal==1:#先平空 再开多
            buy_short(Last_Price)
            buy_long(Last_Price)
        elif signal == -1: # 先平多 再开空
            sell_long(Last_Price)
            sell_short(Last_Price)

    elif tp==1: # 挂单成交
        dc = mark_hold_ms()
        currSell1Price,currBuy1Price = sell_buy_price()
        if signal == 1:  # 平空开多同时进行
            order_id_buy_short = buy_short(currBuy1Price, ratio=1, order_Amount=dc['short'])#平空
            order_id_buy_long = buy_long(currBuy1Price, ratio=1, order_Amount=dc['long'])#开多
            time.sleep(1)
            while True:
                order_Amount_short,order_price_short =calculate_amount(order_id_buy_short) #计算剩余成交量
                order_Amount_long,order_price_long =calculate_amount(order_id_buy_long) #计算剩余成交量
                currSell1Price, currBuy1Price = sell_buy_price()
                if order_Amount_short>1 and order_price_short!=currBuy1Price :
                    exchange.CancelOrder(order_id_buy_short)
                    order_id_buy_short = buy_short(currBuy1Price, ratio=1, order_Amount=order_Amount_short)
                if  order_Amount_long>1 and order_price_short!=currBuy1Price  :
                    exchange.CancelOrder(order_id_buy_long)
                    order_id_buy_long = buy_long(currBuy1Price, ratio=1, order_Amount=order_Amount_long)
                if (order_Amount_short+order_Amount_long)<1:
                    break
                time.sleep(1)
        if signal == -1:  # 平多开空同时进行
            order_id_sell_long = sell_long(currBuy1Price, ratio=1, order_Amount=dc['long'])  # 平多
            order_id_sell_short  = sell_short(currBuy1Price, ratio=1, order_Amount=dc['short'])  # 开空
            time.sleep(1)
            while True:
                order_Amount_long, order_price_long = calculate_amount(order_id_sell_long)
                order_Amount_short, order_price_short = calculate_amount(order_id_sell_short)
                currSell1Price, currBuy1Price = sell_buy_price()
                if order_Amount_long > 1 and order_price_long != currBuy1Price:
                    exchange.CancelOrder(order_id_sell_long)
                    order_id_sell_long = sell_long(currBuy1Price, ratio=1, order_Amount=order_Amount_long)  # 平多
                if order_Amount_short > 1 and order_price_short != currBuy1Price:
                    exchange.CancelOrder(order_id_sell_short)
                    order_id_sell_short  = sell_short(currBuy1Price, ratio=1, order_Amount=order_Amount_short)  # 开空
                if (order_Amount_short+order_Amount_long)<1:
                    break
                time.sleep(1)













