def plot_acf_pacf(data,lags=30):    
    """
    Строит графики ACF и PACF для временного ряда.

    Args:
        data: Временной ряд (pandas Series или numpy array).
        lags: Максимальное количество лагов для построения графиков (по умолчанию 30).
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from statsmodels.tsa.stattools import acf, pacf
    
    # Вычисляем ACF и PACF
    acf_values = acf(data, nlags=lags)
    pacf_values = pacf(data, nlags=lags)

    # Строим графики
    fig, axs = plt.subplots(2, 1, figsize=(10, 5))

    axs[0].plot(acf_values, marker = 'o')
    axs[0].axhline(y=0, linestyle='--', color='gray')
    axs[0].axhline(y=-1.96/np.sqrt(len(data)), linestyle='--', color='gray')
    axs[0].axhline(y=1.96/np.sqrt(len(data)), linestyle='--', color='gray')
    axs[0].set_title('ACF')
    axs[0].set_xlabel('Lag')

    axs[1].plot(pacf_values, marker = 'o')
    axs[1].axhline(y=0, linestyle='--', color='gray')
    axs[1].axhline(y=-1.96/np.sqrt(len(data)), linestyle='--', color='gray')
    axs[1].axhline(y=1.96/np.sqrt(len(data)), linestyle='--', color='gray')
    axs[1].set_title('PACF')
    axs[1].set_xlabel('Lag')

    plt.tight_layout()
    plt.show()
    
    
def plot_external(params_chan, params_all, type_, external_name):
    """
    Строит графики для сравнения динамики по каким-то каналам (витринам\офферам\потомкам)

    Args:
        sub_14: list() - список из необходимых sub_14 (нужен и sms и feed).
        type_: string - FS, если необходимо сравнить feed и sms в рамках external: FF, если необходимо сравнить feed всего трафика и feed в рамках external; SS если необходимо сравнить smsвсего трафика и sms в рамках external.
        external_name: string - Название external
        params_chan: dict() - параметры запроса в keitro_parser в external для считывания данных по уникальному каналу, который необходимо посмотреть (витрина\оффер\поток и тд) (в metrics обязана быть epc_confirmed в grouping - ["sub_id_12", "day"])
        params_all: dict() - параметры запроса в keitro_parser в external для считывания данных по общему потоку (в metrics обязана быть epc_confirmed в grouping - ["sub_id_12", "day"])
    
    """
    from MVPanalytics.keitaro import keitaro_parser
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    
    pars = keitaro_parser(**params_chan).sort_values('day')
    
    
    pars_all = keitaro_parser(**params_all).sort_values('day')
    
    
    if type_ == 'FS':
        plt.plot(pars.loc[pars['sub_id_12']=='feed'].set_index('day')['epc_confirmed'], marker = 'o', label = 'feed')
        plt.plot(pars.loc[pars['sub_id_12']=='sms'].set_index('day')['epc_confirmed'], marker = 'o', label = 'sms')

        plt.legend()
        plt.title(external_name)
        plt.xlabel('date')
        plt.ylabel('EPC')
        plt.xticks(rotation = 45)

        plt.show()
    elif type_ == 'FF':
        plt.plot(pars_all.loc[pars_all['sub_id_12']=='feed'].set_index('day')['epc_confirmed'], marker = 'o', label = 'feed all')
        plt.plot(pars.loc[pars['sub_id_12']=='feed'].set_index('day')['epc_confirmed'], marker = 'o', label = 'feed '+external_name)


        plt.legend()
        plt.title(f'{external_name} vs all')
        plt.xlabel('date')
        plt.ylabel('EPC')
        plt.xticks(rotation = 45)

        plt.show()
    elif type_ == 'SS':
        plt.plot(pars_all.loc[pars_all['sub_id_12']=='sms'].set_index('day')['epc_confirmed'], marker = 'o', label = 'sms all')
        plt.plot(pars.loc[pars['sub_id_12']=='sms'].set_index('day')['epc_confirmed'], marker = 'o', label = 'sms '+external_name)


        plt.legend()
        plt.title(f'{external_name} vs all')
        plt.xlabel('date')
        plt.ylabel('EPC')
        plt.xticks(rotation = 45)

        plt.show()
    else:
        return(print('ОШИБКА: Неверный тип графика. Тип должен быть "FS", "FF", "SS"'))