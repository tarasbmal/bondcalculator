import pandas as pd
import numpy as np 
import datetime 
from pyxirr import xirr
import streamlit as st
import fi 
#----------------------------------------------------
#----------------------------------------------------
#-------  Главный модуль ----------------------------        
#----------------------------------------------------
#----------------------------------------------------
st.set_page_config(layout="wide")
col1, col2 = st.columns([1.2,1])
with col1:    
    st.subheader("Доходность облигации") 
with col1:   
    #---------  Описание ------
    st.markdown("Добро пожаловать на сервис расчета ключевого параметра облигации - эффективной доходности к погашению !")
    st.markdown("Если вы выбираете облигацию для приобретения, то значение доходности - это один из основных критериев при принятии решения.")
    st.markdown("В отличие от других аналогичных сервисов, акцент здесь сделан на точность учета всех денежных потоков, включая комиссию при покупке и подоходный налог.")
    #st.markdown("Эффективная доходность к погашению - это ключевой показатель при принятии решения о приобретении облигации.")
    #sss = ""
    #sss = sss + "Этот универсальный и независимый от особенностей погашения показатель позволяет сравнивать различные облигации и другие аналогичные инструменты, например, банковские депозиты. "  
    #st.markdown(sss)
    #sss = ""
    #sss = sss + "Для корректного расчета необходимо учитывать все денежные потоки, связанные с ценной бумагой - сумму покупки, комиссии, купоны, погашение номинала, в том числе, частичное. "
    #sss = sss + "Для частного инвестора необходимо также учесть подоходный налог на доходы физических лиц. "
    #sss = sss + "Также, важно иметь ввиду, что даты ваших реальных денежных потоков немного расходятся с датами расчетов на бирже."
    #st.markdown(sss)
    st.markdown("**Немного математики...**")
    st.markdown("Эффективная доходность - это значение переменной IRR в следующем уравнении:")
#col1, col2 = st.columns([2.3,1])
with col1:  
    #------------
    st.latex(r'''   
            0 = \sum_{n=0}^{N}
                \frac{CF_n}{\left(1+IRR\right)^{\left(Date_n-Today\right)/365}}
        ''')
#col1, col2, col3 = st.columns([1,3,1])
with col1:  
    st.markdown(", где $CF_n$ и $Date_n$  -  сумма и дата n-го денежного потока.")
    st.markdown("В приложении Excel задача решается применением формулы ЧИСТВНДОХ (XIRR) к таблице денежных потоков.")
#----   Масссив всех доступных облигаций во фрейм для последующего выбора и массив цен 
sec_all  = fi.micex_get_sec_all(0)
#sec_all.to_csv("sec_all.csv",sep=";")   #-----  Выгрузка в файл для тестирования
price_all = fi.micex_get_price_all(0)
#price_all.to_csv("price_all.csv",sep=";")   #-----  Выгрузка в файл для тестирования
#------------------------------------------------------------------------------        
#col1, col2, col3 = st.columns([1,2.2,1],gap="medium")
isn = ""
st.sidebar.markdown("**Шаг 1. Введите любой из параметров облигации: ISIN, № гос.регистрации или часть наименования и нажмите Enter**")
sec_mask = st.sidebar.text_input("", label_visibility="collapsed")
#----- Тестовые данные (недокументированная возможность)
if sec_mask == "0": # Тестовый режим перебора всех облигаций
    ntest = st.sidebar.number_input("N теста", value=1, min_value=1, max_value=2000)
    i = 0
    for index,row in sec_all.iterrows():
        i = i+1
        if i == ntest:
            sec_mask = row['ISIN'] 
elif sec_mask == "1": # Обычный случай с офертой 
    sec_mask= "RU000A1041B2"
elif sec_mask == "2": # С аммортизацией тела - Бизнес-Недвижимость
    sec_mask= "RU000A1022G1"
elif sec_mask == "3": # С аммортизацией тела (много аммортизаций )
    sec_mask= "RU000A107C91"
elif sec_mask == "4": # Замещающая
    sec_mask= "RU000A1056U0"    
elif sec_mask == "5": # Ошибка
    sec_mask= "XS1951067039"    
#-----  Фильтруем  кодам  ----
sec_filter = sec_all[(sec_all["SECID"] == sec_mask) | (sec_all["ISIN"] == sec_mask) | (sec_all["REGNUMBER"] == sec_mask)]	
#st.sidebar.text("-111->"+sec_mask+"<--"+str(sec_filter.shape[0]))
if sec_filter.shape[0] == 0:    #-- число записей = 0, т.е. не нашли по номеру, ищем по имени
    sec_filter = sec_all[sec_all["SECNAME"].str.contains(sec_mask, case=False)]
    #st.sidebar.text("-222->"+sec_mask+"<--"+str(sec_filter.shape[0]))
if sec_filter.shape[0] == 1:
    #st.sidebar.text("-333->"+sec_mask+"<--"+str(sec_filter.shape[0]))
    isn = sec_filter["ISIN"].iloc[0]     
if sec_mask != "" and sec_filter.shape[0] > 1: #-- число записей больше 1, нужно уточнить
    #st.sidebar.text("-444->"+sec_mask+"<--"+str(sec_filter.shape[0]))
    #-----------------   Выбор из списка  ----------------------------------------
    #st.sidebar.text("-->"+sec_mask+"<--")
    st.sidebar.markdown("**Уточните свой выбор, пожалуйста**")
    ppp = st.sidebar.selectbox("Выбрать облигацию", sec_filter['SHORTNAME']+ " ,  " +sec_filter['ISIN'], label_visibility="collapsed")   
    isn = ""
    if ppp != None:     
        isn = ppp[-12:]
if sec_mask != "" and isn == "":
    st.sidebar.text("Не могу найти такую бумагу (")
if isn != "":    
    #--------  получаем данные по облигации ---
    sec_id,sec_name,sec_isin,mat_date,offer_date,nom_sum,nom_cur,r_cur,coup_sum,coup_date,coup_prc,coup_period,nkd_sum,set_date,price=fi.get_sec_one(sec_filter, isn)
    if sec_id == "":
        st.error("Не найдена облигация с ISIN: " + isn + " !!!")
    else: 
        f_buydate = datetime.datetime.today().date()
        f_s_buydate = set_date 
        #f_buydate = datetime.datetime(2024, 2, 9).date()
        #----------------  Результаты работы -------------
        with col1:
            st.divider()
            st.subheader(sec_name) 
            st.markdown("**ISIN: " + isn + "**")
            #--------  Разделим колонку еще на 2 колонки 
            c1, c2 = col1.columns([1,1])
            with c1:
                if nom_cur == "SUR":
                    nom_cur = "RUB"
                st.markdown("**Текущий номинал: " + str(int(nom_sum)) + " " + nom_cur + "**")
                st.markdown("**Накопленный купонный доход (НКД): " + str(round(nkd_sum,2)) + "**")
            with c2:
                if offer_date != "":
                    st.markdown("**Дата оферты:         " + offer_date.strftime("%d-%m-%Y") + "**")
                else:
                    st.markdown("**Дата оферты:**")            
                if mat_date != "":
                    st.markdown("**Дата погашения: " + mat_date.strftime("%d-%m-%Y") + "**")
                else:
                    st.markdown("**Дата погашения:**")
        #-------  Ищем текущую цену, чтобы предложить по умолчанию
        price_filter = price_all[price_all["SECID"] == sec_id]	
        if price_filter.shape[0] > 0:    #-- число записей = 0, поэтому берем цену из свежих
            price = round((price_filter["BID"].iloc[0] + price_filter["OFFER"].iloc[0])/2,2) 
            #st.sidebar.text("--Новая цена !!!--")   
        #else:
        #    st.sidebar.text("--Старая цена--")            
        #------- Вводим параметры расчета -------
        #st.sidebar.divider()
        st.sidebar.markdown("#")
        #st.sidebar.markdown("#")
        st.sidebar.markdown('**Шаг 2. Введите параметры для расчета и нажмите кнопку "Рассчитать"**')
        price = st.sidebar.number_input("Цена покупки, %", value=price, min_value=5.0, max_value=300.0)
        com_pr = st.sidebar.number_input("Комиссия при покупке, %", value=0.04, min_value=0.0, max_value=1.0)
        use_offer = "Погашения"
        if offer_date != "":
            use_offer = st.sidebar.radio("Рассчитывать до даты",["Оферты","Погашения"])     
        use_nalog = st.sidebar.checkbox('Учесть подоходный налог 13%', value=True)
        #st.sidebar.divider()
        st.sidebar.markdown('##')
        button1 = st.sidebar.button("$$\kern1.5cm Рассчитать \kern1.5cm$$")
        if button1:
            #-----------  Получаем данные по купонам -------------------------------------
            ret, coup = fi.get_coups(sec_id)
            #-------------------------------------------------------------------------------------
            #coup.to_csv("c.csv",sep=";")   #-----  Выгрузка в файл для тестирования
            if mat_date == "":         
                st.error("У облигации отсутствует дата погашения. Расчет доходности невозможен !")            
            elif ret < 0:
                st.error("Не найдена таблица - календарь купонов по облигации. Расчет доходности не представляется возможным !")
            elif ret == 0:
                st.error("Таблица - календарь купонов по облигации - пуста. Расчет доходности не представляется возможным !")
            elif coup['amounts'][0]=="—":
                st.error("В таблице - календаре купонов нет сумм. Скорее всего, это облигация с плавающим купоном (флоутер). Расчет доходности не представляется возможным !")
            else:                
                #----  Номиналы
                nom_00 = float(nom_sum)   # Начальный
                nom_now = nom_00        # Текущий
                nom_prev = nom_now      # Предыдущий
                #---------   Вычисляем парамеры в нужном формате 
                f_buysum = round(nom_00*price/100,2)+round(float(nkd_sum),2)
                com_sum = round(f_buysum*com_pr/100,2) 
                if use_offer == 'Оферты':
                    f_s_enddate = offer_date
                else:
                    f_s_enddate = mat_date
                f_enddate = fi.get_next_work_day(f_s_enddate)
                #------------------------------------------------
                #----------  Немного улучшаем фрейм по купонам --
                #------------------------------------------------
                #---------  Фильтр - Оставляем только все данные по купонам до погашения или оферты и не раньше расчетной даты покупки 
                coup = coup[coup['s_dates'] > f_s_buydate]              
                coup = coup[coup['s_dates'] <= f_s_enddate]              
                #------  Если суммы нет, то 0 (ноль)
                coup.loc[coup['amounts'] == "—", 'amounts'] = 0.00
                #------  Устанавливаем правильный тип поля  
                coup[['amounts']] = coup[['amounts']].astype(float)
                #------------------------------------------------
                #----------  Сохраняем в общий фрейм   ----------
                #------------------------------------------------    
                pl = coup[["dates","s_dates","amounts","comment"]].copy()    #-- оставляем только нужные поля    
                pl.reset_index(drop= True , inplace= True )     #-- сброс индекса      
                #--------  Если купон = 0, ту устанавливаем последний известный 
                amounts_prev = 0
                for index, row in pl.iterrows():
                    if row['amounts'] == 0:
                        pl['amounts'].loc[index] = amounts_prev
                        pl['comment'].loc[index] = "Купон(здесь=сумме последнего известного купона)"
                    else:
                        amounts_prev = row['amounts']     
                #---- Если купон не до даты погашения тела, то вычисляем 
                if len(pl.index)>0:
                    last_coup_date = pl['s_dates'].iloc[-1]  
                    if last_coup_date < f_s_enddate:    
                        part_sum = round(float(nom_sum)*float((f_s_enddate-last_coup_date).days)*float(coup_prc)/36500,2)
                        #pl.loc[len(pl.index)] = [f_enddate, f_s_enddate, part_sum,"Купон (часть)"]  
                        pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': part_sum,'comment': "Купон (часть)"}, index=[0])],ignore_index=True)                              
                #---------   Добавляем налог с купонов ---
                if use_nalog:
                    n = 0
                    for index,row in pl.iterrows():
                        if pl['amounts'][index] !=0:
                            n = n + 1
                            if n == 1:
                                #------ для 1-го купона база скорректирована на сумму НКД при покупке ---
                                pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 's_dates': pl['s_dates'][index],'amounts': round((pl['amounts'][index]-nkd_sum)*(-0.13),2),'comment': "Налог с суммы купона за вычетом НКД при покупке"}, index=[0])],ignore_index=True)                              
                            else:                            
                                pl = pd.concat([pl, pd.DataFrame({'dates': pl['dates'][index], 's_dates': pl['s_dates'][index],'amounts': round(pl['amounts'][index]*(-0.13),2),'comment': "Налог с суммы купона"}, index=[0])],ignore_index=True)                              
                #---------   Добавляем покупку  -----------
                #pl.to_csv("pl_.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #pl.loc[len(pl.index)] = [f_buydate, f_s_buydate, f_buysum*(-1),"Сумма сделки покупки, включая НКД"]
                pl = pd.concat([pl, pd.DataFrame({'dates': f_buydate, 's_dates': f_s_buydate,'amounts': f_buysum*(-1),'comment': "Сумма сделки покупки, включая НКД"}, index=[0])],ignore_index=True)                              
                #pl.to_csv("pl__.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #---------   Добавляем комиссию   -----------
                if com_sum>0:
                    #pl.loc[len(pl.index)] = [f_buydate, f_s_buydate, com_sum*(-1),"Комиссия при покупке"]
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_buydate, 's_dates': f_s_buydate,'amounts': com_sum*(-1),'comment': "Комиссия при покупке"}, index=[0])],ignore_index=True)                              
                #pl.to_csv("pl___.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                #--------- Проверяем амортизации. Если есть , то заносим                 
                nnn = 0
                for index,row in coup.iterrows():
                    nnn = nnn + 1
                    if nnn>=2 and coup['prc'][index]>0:  # для второго купона
                        nm = round(coup['amounts'][index] * 36500 / coup['prc'][index] / float((coup['s_dates'][index]-s_date_prev).days),0)
                        if nm != "nan":
                            if nm < nom_prev:
                                s_dt = s_date_prev
                                dt = fi.get_next_work_day(s_dt)
                                asum = nom_prev - nm
                                if asum*100/nm > 3:    # больше 3-х %
                                    nom_now = nm
                                    #-------  Добавляем запись частичного погашения 
                                    #st.text(asum)
                                    #pl.loc[len(pl.index)] = [dt, s_dt, asum,"Частичное погашение тела облигации"]  
                                    pl = pd.concat([pl, pd.DataFrame({'dates': dt, 's_dates': s_dt,'amounts': asum,'comment': "Частичное погашение тела облигации"}, index=[0])],ignore_index=True)                              
                                    #------------------------------------------------------
                                    nom_prev = nom_now
                    s_date_prev = coup['s_dates'][index]
                #---------   Добавляем окончательное погашение -----
                #st.text("Последняя сумма -->" + str(nom_now))
                if nom_now>0:
                    #pl.loc[len(pl.index)] = [f_enddate,f_s_enddate,nom_now,"Погашение тела облигации"]
                    pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': nom_now,'comment': "Погашение тела облигации"}, index=[0])],ignore_index=True)                              
                #--- если купили дешевле, то еще налог - в конце срока
                if use_nalog:
                    if (f_buysum + com_sum) < nom_00:
                        y_amount = (f_s_enddate - f_buydate).days//365    #-- число полных лет до погашения
                        if y_amount < 3:
                            pl = pd.concat([pl, pd.DataFrame({'dates': f_enddate, 's_dates': f_s_enddate,'amounts': round((nom_sum-f_buysum-com_sum)*(-0.13),2),'comment': "Налог с разницы сумм погаш. и покупки с комиссией"}, index=[0])],ignore_index=True)     
                #st.dataframe(pl,800)                           
                #-------  Запуск расчета ------
                #pl2 = pl[["dates","amounts"]].copy() # 
                #pl[["dates","amounts"]].to_csv("2.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                IRR = xirr(pl[["dates","amounts"]])
                #st.divider()
                #-------  Только ненулевые суммы  
                rslt_pl = pl[pl['amounts'] != 0].copy() 
                #-------  Перерасчитываем дисконтируемые суммы потоков + добавляем столбец даты в нужном формате 
                rslt_pl['d_ams'] = 0
                rslt_pl['str_dates'] = ""
                rslt_pl['str_s_dates'] = ""
                dams_total = 0
                dur = 0
                #rslt_pl.to_csv("rslt_pl.csv",sep=";")   #-----  Выгрузка в файл для тестирования
                for index, row in rslt_pl.iterrows():
                    rslt_pl['str_dates'].loc[index] = rslt_pl['dates'].loc[index].strftime("%d-%m-%Y")
                    rslt_pl['str_s_dates'].loc[index] = rslt_pl['s_dates'].loc[index].strftime("%d-%m-%Y")
                    #----------------------------------------------                
                    ddelta = (rslt_pl['dates'].loc[index]-f_buydate).days
                    dams = rslt_pl['amounts'].loc[index]/((1+IRR)**(ddelta/365))
                    rslt_pl['d_ams'].loc[index] = dams
                    dams_total = dams_total + dams
                    if dams > 0:
                        dur = dur + dams*ddelta
                #----  Дюрация 
                dur = round(dur/f_buysum/365,1)
                #-------  Выводим основные данные ---
                with col1: 
                    if IRR>0:
                        st.success("$$\Large\kern5cm Доходность: \space" + str(round(IRR*100,2)) + " \space\% $$")                
                    else:                    
                        st.error("$$\Large\kern5cm Доходность: \space" + str(round(IRR*100,2)) + " \space\% $$")                
                    #st.subheader("Доходность: " + str(round(IRR*100,2)) + " %")
                    if nom_cur != "RUB":
                        st.markdown("**Номинал облигации выражен в иностранной валюте " + nom_cur + ". При изменении курса валюты доходность также изменится." + "**")
                    #--------  Разделим колонку еще на 2 колонки 
                    c1, c2 = col1.columns([1,1])
                    with c1:
                        st.markdown("**Дюрация Макколея: " + str(dur) + " лет**")
                    with c2:
                        dur_m = round(dur/(1+IRR),1)
                        st.markdown("**Модифицированная дюрация: " + str(dur_m) + "**")
                    if use_nalog and ((f_buysum+com_sum) < nom_00) and y_amount>=3:
                        st.markdown("Длительность инвестиции будет составлять более 3-х лет. В этом случае применяется льгота долгосрочного владения (ЛДВ) и налог с разницы суммы погашения и суммы приобретения - не применяется.")
                    #-------  Сортируем и выводим подробности расчета 
                    #st.divider()
                with col2: 
                    st.markdown("##")    # пропуск строки
                    st.markdown("**Все будущие денежные потоки (знак суммы соответствует направлению)**")    
                    #-------  Перерасчитываем дисконтируемые суммы потоков 
                    rslt_pl2 = rslt_pl.sort_values(by=['dates'])
                    rslt_pl2.reset_index(drop= True , inplace= True )     #-- сброс индекса  
                    rslt_pl3 = rslt_pl2[['str_dates','str_s_dates','comment','amounts','d_ams']]
                    rslt_pl3.columns = ['Дата потока','  Дата бирж.','         Вид суммы', '  Сумма','Дисконт.сумма']   #-- переименовать столбцы
                    nnn = rslt_pl3.shape[0]
                    if nnn>=22:
                        nnn = 22
                    #st.dataframe(rslt_pl3, 1200, (nnn+1)*36+20) # Сначала ширина, потом - высота 
                    #st.dataframe(rslt_pl3, 1200, int(round((nnn+1)*36.4,0))+8) # Сначала ширина, потом - высота 
                    #st.dataframe(rslt_pl3, 1200, int(round((nnn+1)*36.5,0))+4) # Сначала ширина, потом - высота 
                    #st.dataframe(rslt_pl3, 1200, int(round((nnn+1)*36.3,0))+6) # Сначала ширина, потом - высота 
                    st.dataframe(rslt_pl3, 1200, int(round((nnn+1)*36.1,0))+8) # Сначала ширина, потом - высота 
                #col1, col2 = st.columns([1,1.1])
                #with col2: 
                    c1, c2 = col2.columns([1,2])
                    with c2:
                        st.markdown("**Сумма дисконтируемых денежных потоков, Итого:  " + str(round(dams_total,2)) + "**")
            #-----------------------------------------------------------------------------------------
#st.divider()
col1, col2 = st.columns([4,1])
with col2:    
    st.text("e-mail: tarasbmal@gmail.com")
