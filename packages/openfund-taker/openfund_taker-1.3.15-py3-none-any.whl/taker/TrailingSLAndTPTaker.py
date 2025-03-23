
from taker.TrailingSLTaker import TrailingSLTaker
'''
自动设置移动止损单
'''
class TrailingSLAndTPTaker(TrailingSLTaker):
    def __init__(self,g_config, platform_config, feishu_webhook=None, monitor_interval=4,logger=None):
        super().__init__(g_config, platform_config, feishu_webhook, monitor_interval,logger)
        self.all_TP_LS_ratio = float(platform_config.get("all_TP_LS_ratio",1.5)) #The profit-loss ratio 盈亏比
        self.all_take_profit_pct = self.stop_loss_pct *  self.all_TP_LS_ratio
   
    def set_stop_loss_take_profit(self, symbol, position, stop_loss_price=None, take_profit_price=None) -> bool:
        is_successful = super().set_stop_loss_take_profit(symbol, position, stop_loss_price, take_profit_price)
        # take_profile_pct = self.stop_loss_pct *  2
        order_take_profit_price = take_profit_price
        if take_profit_price is None:
            order_take_profit_price = self.calculate_take_profile_price(symbol, position, self.all_take_profit_pct)
            is_successful = self.set_take_profit(symbol, position, order_take_profit_price)
    
        
        return is_successful

