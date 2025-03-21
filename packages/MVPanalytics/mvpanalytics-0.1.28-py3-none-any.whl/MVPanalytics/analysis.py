def weightgiver(api_key, host, comp_id, str_id,  perc_min, per, n_active = [], min_active = 0.5, min_cens = 0.3,prime = [], prime_add = 0.1, send_token = '', send_id = []):
    """
        Функция для раздачи офферам в партнёрке весов (сплитование)
    
        Args:
            api_key: (str) - апи-ключ для доступа в кейтаро
            host: (str) - url для доступа к кейтаро
            comp_id: (int) - id кампании
            str_id: (int) - id потока
            perc_min: (float [0, 1]) - минимальная доля сплита рекламодателя от суммарного epc
            n_active: (list) - список офферов, которых не должно быть в сплите
            
            per: (int) - интервал часов з который парсится информация
            prime: (list) - список из id рекламодателей, которые в главном приоритете
            prime_add: (float) - какая доля отнимается у всех неприоритетных оферов (например, если prime_add = 0.1, то 10% отнимается у всех приоритетов и добавляются к prime)
            send_token: (str) - токен телеграм-бота
            send_id: (str) - id чата
    """
    
    import numpy as np
    from MVPanalytics.keitaro import keitaro_parser
    from datetime import datetime, timedelta
    import telepot
    t=0
    while (t == 0):
        spl = keitaro_parser(api_key, host,
                interval= 'custom_date_range',
                firstdate=  (datetime.now() - timedelta(hours=int(per))).strftime("%Y-%m-%d %H:%M"),
                lastdate= datetime.now().strftime("%Y-%m-%d %H:%M"),
                filters = [{'name': "stream_id", 'operator': "EQUALS", 'expression': int(str_id)},
                        {'name': "campaign_id", 'operator': "EQUALS", 'expression': int(comp_id)}],
            grouping = ["stream", "offer", 'offer_id','affiliate_network', 'affiliate_network_id'],
            metrics = ['epc_confirmed', 'clicks']
            )
        
        t = spl['epc_confirmed'].max()
        per+=12

    if not spl.empty:    
        
        spl = spl.loc[~spl['offer_id'].isin(n_active)]
        remove_df = spl.loc[(1-(spl['epc_confirmed']/spl['epc_confirmed'].max()))>min_active]
        
        if not remove_df.empty:
            

            bot = telepot.Bot(token=send_token)
            
            message = ''
            
            for i in remove_df.index:
                message+=f'''
                \nИз сплита убран оффер {remove_df.loc[i]['offer']} с epc {remove_df.loc[i]['epc_confirmed']} за {per-12} часов , разнница с максимальным epc в потоке составила {round(100-100*remove_df['epc_confirmed'].loc[i]/spl['epc_confirmed'].max(),2)}%
                \n------------------------------------------------------------------------------------------
                '''
                for user in send_id:
                    bot.sendMessage(user, text = message)
        spl = spl.drop(index=remove_df.index)
        
        spl['epc_help'] = spl['epc_confirmed']
        
        min_perc_offrs = spl.loc[(1-(spl['epc_confirmed']/spl['epc_confirmed'].max()))>min_cens]
        
        if not min_perc_offrs.empty:
            
            value_share = min_perc_offrs['epc_help'].sum()
            spl.loc[min_perc_offrs.index, 'epc_help'] = 0
            spl.loc[spl.index.drop(min_perc_offrs.index), 'epc_help'] = spl.loc[spl.index.drop(min_perc_offrs.index), 'epc_help'] + value_share/len(spl.loc[spl.index.drop(min_perc_offrs.index)])
            
            spl.loc[min_perc_offrs.index, 'epc_help'] = spl['epc_help'].sum()*perc_min
            
            
            
        spl['perc'] = (spl.epc_help*100/(spl.epc_help.sum())).round()    
        
        if (spl['affiliate_network_id'].isin(prime).sum()!=0):
            add_value = spl.loc[~spl['affiliate_network_id'].isin(prime),'epc_help']*(prime_add)
                
            spl.loc[~(spl['affiliate_network_id'].isin(prime)), 'epc_help'] = spl.loc[~(spl['affiliate_network_id'].isin(prime)),'epc_help']*(1-prime_add)
            spl.loc[spl['affiliate_network_id'].isin(prime), 'epc_help'] = spl.loc[spl['affiliate_network_id'].isin(prime), 'epc_help']+add_value.sum()/len(spl.loc[spl['affiliate_network_id'].isin(prime), 'epc_help'])
            
            spl['perc'] = (spl.epc_help*100/(spl.epc_help.sum())).round()
        
        if spl['perc'].sum()!=100:
            spl.loc[spl['perc'].idxmax(),'perc'] = spl['perc'].max() + (100-spl['perc'].sum())
    return(spl)

def off_analyzer(data,target, report_type, showcases = False):
    
    """
        Функция, позволяющая выявлять витрины по потоку (или офферу), на которых его: target < EPC, 0 < EPC < target, EPC=0
        
        Args:
            data: (pd.Dataframe) - спаршенные данные с кейтаро, которые должны содержать колонки ['epc_confirmed', 'external_id', 'clicks', 'sale_revenue']
            target: (float) - нижнее удовлетворяющее значеие EPC
            showcases: (bool) - нужна ли подробная таблица, которая выдаёт сами external с epc ниже таргета (рботает для report_type == 'offer')
            report_type: (str) - Вид отчёта, если 'city' - делает разбивку по городам, если 'offer' - то отчёт по !Одному! офферу. Отчёт по городам рабоатет для всех офферов
            
            Выдача:
                Если showcases = False/report_type == 'city' : Возвращает одну таблицу, которая показывает сколько кликов отливается на витрины с epc по потоку/потоку+городу target < EPC, 0 < EPC < target, EPC=0 без уточнения того, какие это витрины
                Если showcases = True: Возвращает 2 таблицы, первая - как из showcases = False, вторая - вместе с external_id
    """
    
    import pandas as pd
    import numpy as np
    if report_type == 'offer':
        data['more'] = data['epc_confirmed'].apply(lambda x: f'more than {target} epc' if x >target else( f'less then {target}' if ((x<target)&(x>0))  else 'zero_epc'))
        gr = data[['more', 'epc_confirmed','clicks','sale_revenue']].groupby(by='more').agg({'clicks':['sum','mean','max'], 'sale_revenue':'sum', 'epc_confirmed':['min', 'max']})

        gr['epc_agregated'] = gr[('sale_revenue','sum')]/gr[('clicks', 'sum')]
        if showcases == False:
            return(gr)
        else:
            gr_1 = data[['more', 'external_id','clicks','epc_confirmed']].groupby(by=['more','external_id']).sum().sort_values(by=['more','clicks'], ascending=False)
            return(gr, gr_1)
    
    if report_type == 'city':
        gr = data[['offer','city','epc_confirmed','clicks','sale_revenue']].groupby(by=['offer','city']).agg({'clicks':['sum','mean','max'], 'sale_revenue':'sum', 'epc_confirmed':['min', 'max']}).sort_values(by = ['offer',('clicks', 'sum')],ascending = False)

        gr['epc_agregated'] = gr[('sale_revenue','sum')]/gr[('clicks', 'sum')]
    
        gr[('clicks', '% of offer')] = 100*(data[['offer', 'city','clicks']].groupby(['offer', 'city']).sum())/(data[['offer', 'clicks']].groupby('offer').sum())
        return(gr.round(2))

def streamdiff(params_pars, target, metric, channel,minclick):
    '''
    Скрипт позволяет смотреть, сколько в рамках какого-то канала(витрина, вебмастер, пртнёр и тд) за промежуток времени(указыывается в параметрах запроса) было моментов в ремени в который целевая метрика была больше и меньше таргета
    
    Args:
    params_pars: dict() - параметры запроса функции keitaro_parser
    target: float - целевое значение с которым сравнивается
    metrics: string - метрика, по которой будет подсчёт
    channel: string - то, по чему должна идти группировка (stream/offer...)
    minclick: int - минимальное количество кликов, при который наблюдение будет взято для подсчёта сводной таблицы (напимер, если minclick=10, то в выборку не пойдут дни(если группировка по дням) в которые на потоке (если channel = 'streaam') было строго больше эктого количествоа кликов)
    
    '''
    from MVPanalytics.keitaro import keitaro_parser
    import matplotlib.pyplot as plt 
    import numpy as np 
    import pandas as pd 
    strm = keitaro_parser(**params_pars)
    strm = strm.loc[strm['clicks']>minclick]
    retr = strm[strm[metric] > target].groupby(channel).count()[[metric]].merge(strm[strm[metric] < target].groupby(channel).count()[[metric]], right_index=True, left_index=True, how = 'outer', suffixes = ['_more '+str(target), '_less '+str(target)]).fillna(0)
    retr['percent >'+str(target)] = retr[metric+'_more '+str(target)]*100/(retr[metric+'_more '+str(target)] + retr[metric+'_less '+str(target)])
    retr = retr.merge(strm[[channel, 'clicks']].groupby(channel).sum()['clicks'], right_index = True, left_index = True)
    if metric == 'epc_confirmed':
        retr = retr.merge(strm[[channel, 'sale_revenue']].groupby(channel).sum()['sale_revenue'], right_index = True, left_index = True)
        retr[metric+' for period'] = retr['sale_revenue']/retr['clicks']
        retr.drop(columns=['sale_revenue'], inplace=True)
    return(retr.sort_values('percent >'+str(target), ascending = 0))