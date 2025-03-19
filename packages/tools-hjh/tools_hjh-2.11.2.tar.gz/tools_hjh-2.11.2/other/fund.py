# coding:utf-8
import sys
from tools_hjh import DBConn
from tools_hjh import Log
from tools_hjh import ThreadPool
from tools_hjh import Tools
from tools_hjh import HTTPTools
import json
import time
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import math
from tools_hjh.Tools import str_exception

stop_flag = False
page_num = None

date = Tools.locatdate()
log = Log('D:/MyFiles/MyPy/log/fund/' + date + '.log')

host = 'https://'

chrome_path = r'D:\MyApps\CentBrowser\App\chrome.exe'
chromedriver_path = r'D:\MyApps\CentBrowser\chromedriver.exe'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'text',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-ch-ua': 'x86;v=99, Windows;v=10, Surface Laptop Studio;v=1',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Referer':'http://fundf10.eastmoney.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'cookie':'qgqp_b_id=5b3011884880cd251f1bc065e16256ae; emshistory=%5B%22513100%22%5D; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; HAList=ty-103-NQ00Y-%u5C0F%u578B%u7EB3%u6307%u5F53%u6708%u8FDE%u7EED%2Cty-100-NDX100-%u7EB3%u65AF%u8FBE%u514B100%2Cty-133-USDCNH-%u7F8E%u5143%u79BB%u5CB8%u4EBA%u6C11%u5E01%2Cty-1-512690-%u9152ETF%2Cty-1-513100-%u7EB3%u6307ETF%2Cty-105-NVDA-%u82F1%u4F1F%u8FBE%2Cty-1-600900-%u957F%u6C5F%u7535%u529B%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570; st_si=04690614705089; st_asi=delete; EMFUND0=null; EMFUND7=07-18%2022%3A48%3A53@%23%24%u62DB%u5546%u4E2D%u8BC1%u767D%u9152%u6307%u6570%28LOF%29A@%23%24161725; EMFUND8=07-19%2002%3A43%3A47@%23%24%u6613%u65B9%u8FBE%u5929%u5929%u7406%u8D22%u8D27%u5E01A@%23%24000009; EMFUND9=07-29 10:05:57@#$%u534E%u590F%u6210%u957F%u6DF7%u5408@%23%24000001; st_pvi=99805886133314; st_sp=2024-04-24%2009%3A56%3A14; st_inirUrl=http%3A%2F%2Fquote.eastmoney.com%2Fsh513100.html; st_sn=4; st_psi=20240729100557782-112200305282-3955411629'
}

try:
    sys_argv_1 = sys.argv[1]
except:
    sys_argv_1 = 'download'
try:
    sys_argv_2 = int(sys.argv[2])
except:
    sys_argv_2 = -1  # 获取条数
try:
    sys_argv_3 = sys.argv[3]
except:
    sys_argv_3 = 1
    
thread_num = 64


def main(): 
    db = DBConn('sqlite', db='D:/MyFiles/MyPy/data/fund.db', poolsize=64)
    try:
        db.run('PRAGMA journal_mode = WAL')
        createDatabase(db, rebuild=False)
        # get_fund_main(db, HTTPTools)
        # get_fund_dv(db, HTTPTools, begin_code='000000', code=None, name_like='%国泰纳斯达克100指数%')
        # get_fund_dv(db, HTTPTools, begin_code='000000', code=None, name_like='%纳斯达克%')
        # get_fund_dv(db, HTTPTools, begin_code='000000', code=None, name_like='%纳指%')
        # fix_fund_dv(db, HTTPTools, begin_code='000000', code=None, name_like='%%')
        get_fund_dv(db, HTTPTools, begin_code='000000', code=None, name_like='%%')
        fix_dwjz(db)
        get_zf(db)
        get_val(db)
        get_hc(db)
        get_nh(db)
        get_xp(db)
    finally:
        db.run('PRAGMA main.wal_checkpoint')
        db.close()


def createDatabase(db, rebuild=False):
    if rebuild:
        db.run('drop table if exists t_m')
        db.run('drop table if exists t_e')

    t_m = '''
        create table if not exists t_m(
            code char(9),
            name varchar(255),
            type varchar(255),
            primary key(code)
        )
    '''
    
    t_e = '''
        create table if not exists t_e(
            code char(9),
            date char(10),
            dwjz real,
            ljjz real,
            zf real,
            fh text,
            val real,
            hc real,
            nh1n real,
            nh3n real,
            nh5n real,
            xp1n real,
            xp3n real,
            xp5n real,
            primary key(code, date)
        )
    '''
    
    db.run(t_m)
    db.run(t_e)


def get_fund_main(db, rep):
    sql = 'insert or replace into t_m(code,name,type) values(?,?,?)'
    page = rep.get('http://fund.eastmoney.com/js/fundcode_search.js')
    page = page.encode('utf8')[3:].decode('utf8')
    page = page.replace('var r = ', '').replace(';', '')
    fund_list = json.loads(page)
    params = []
    for fund in fund_list:
        code = fund[0]
        name = fund[2]
        type_ = fund[3]
        params.append((code, name, type_))
    num = db.run(sql, params)
    log.info('get_fund_main', num)


# 从库中最大的date开始，获取至今的数据，如果中间缺了不会补
def get_fund_dv(db, rep, begin_code='000000', code=None, name_like=''):
            
    sql = "replace into t_e(code,date,dwjz,ljjz,fh) values(?,?,?,?,?)"
    vals_all = []

    def get_fund_dv_one(code, rep, times=1):
        try:
            timestamp = str(int(time.time() * 1000))
            end_date = Tools.locatdate()
            start_date = db.run('select max(date) from t_e where code = ?', (code,)).get_rows()[0][0]
            if start_date is None:
                start_date = '1949-10-01'
            
            if end_date == start_date:
                log.info('get_fund_dv_one', code, 0, len(vals_all), times)
                return
            
            page_size = 20
            all_size = (datetime.datetime.strptime(end_date, "%Y-%m-%d").date() - datetime.datetime.strptime(start_date, "%Y-%m-%d").date()).days
            all_size = 230
            page_num = math.ceil(all_size / page_size)
            
            rss_num = 0
            for page_idx in range(1, page_num + 1):
                url = 'http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18306743973867400965_1722217638986&fundCode=' + code + '&pageIndex=' + str(page_idx) + '&pageSize=' + str(page_size) + '&startDate=' + start_date + '&endDate=' + end_date + '&_=' + timestamp
                page = rep.get(url, headers=headers)
                page = page.replace('jQuery18306743973867400965_1722217638986', '').strip()
                page = page.split('"LSJZList":')[1].split(',"FundType"')[0]
                rss = json.loads(page)
                rss_num = rss_num + len(rss)
                
                if len(rss) == 0:
                    break
                
                for rs in reversed(rss):
                    date_ = rs['FSRQ']
                    dwjz = rs['DWJZ']
                    if dwjz == '':
                        dwjz = None
                    ljjz = rs['LJJZ']
                    if ljjz == '':
                        ljjz = None
                    zf = rs['JZZZL']
                    if zf == '':
                        zf = 0
                    fh = rs['FHSP']
                    if fh == '':
                        fh = None
         
                    vals_all.append((code, date_, dwjz, ljjz, fh))

            log.info('get_fund_dv_one', code, rss_num, len(vals_all), times)
                    
        except Exception as _:
            if times <= 99:
                # log.warning('get_fund_dv_one', code, times, _)
                # time.sleep(1)
                times = times + 1
                get_fund_dv_one(code, rep, times)
            else:
                log.error('get_fund_dv_one', code, times, str_exception(_))
    
    if code is not None:
        get_code_sql = '''
            select code from t_m 
            where code = ?
        '''
        funds = db.run(get_code_sql, (begin_code,)).get_rows()
    else:
        get_code_sql = '''
            select code from t_m 
            where 1=1
            and type not in('货币型-普通货币')
            and code >= ?
            and name like ?
            order by code
        '''
        funds = db.run(get_code_sql, (begin_code, name_like)).get_rows()
    
    tp = ThreadPool(thread_num)
    for fund in funds:
        if len(vals_all) >= 1000000:
            tp.wait()
            num = db.run(sql, vals_all)
            log.info('get_fund_dv', num)
            vals_all.clear()
        else:
            code = fund[0]
            tp.run_wait(get_fund_dv_one, (code, rep))
            
    tp.wait()
    num = db.run(sql, vals_all)
    log.info('get_fund_dv', num)
    vals_all.clear()


# 从库中最大的date开始，获取至今的数据，如果中间缺了不会补
def fix_fund_dv(db, rep, begin_code='000000', code=None, name_like=''):
            
    sql = "replace into t_e(code,date,dwjz,ljjz,fh) values(?,?,?,?,?)"
    vals_all = []

    def fix_fund_dv_one(code, rep, times=1):
        try:
            idx = 1
            page_size = 9999
            timestamp = str(int(time.time() * 1000))
            start_date = '1949-10-01'
            db_count = int(db.run('select count(1) from t_e where code = ?', (code,)).get_rows()[0][0])
            try:
                end_date = db.run('select max(date) from t_e where code = ?', (code,)).get_rows()[0][0]
            except:
                end_date = Tools.locatdate()
            if end_date is None:
                end_date = Tools.locatdate()
            
            url = 'http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18306743973867400965_1722217638986&fundCode=' + code + '&pageIndex=' + str(idx) + '&pageSize=' + str(page_size) + '&startDate=' + start_date + '&endDate=' + end_date + '&_=' + timestamp
            page = rep.get(url, headers=headers)
            page = page.replace('jQuery18306743973867400965_1722217638986', '').strip()
            page = page.split('"LSJZList":')[1].split(',"FundType"')[0]
            rss = json.loads(page)
            
            if len(rss) == 0 or len(rss) == db_count:
                log.info('fix_fund_dv_one', code, 0, len(vals_all), times)
                return
            
            for rs in reversed(rss):
                date_ = rs['FSRQ']
                dwjz = rs['DWJZ']
                if dwjz == '':
                    dwjz = None
                ljjz = rs['LJJZ']
                if ljjz == '':
                    ljjz = None
                zf = rs['JZZZL']
                if zf == '':
                    zf = 0
                fh = rs['FHSP']
                if fh == '':
                    fh = None
     
                vals_all.append((code, date_, dwjz, ljjz, fh))

            log.info('fix_fund_dv_one', code, len(rss), len(vals_all), times)
                    
        except Exception as _:
            if times <= 99:
                # log.warning('fix_fund_dv_one', code, times, _)
                # time.sleep(1)
                times = times + 1
                fix_fund_dv_one(code, rep, times)
            else:
                log.error('fix_fund_dv_one', code, times, _)
    
    if code is not None:
        get_code_sql = '''
            select code from t_m 
            where code = ?
        '''
        funds = db.run(get_code_sql, (begin_code,)).get_rows()
    else:
        get_code_sql = '''
            select code from t_m 
            where 1=1
            and type not in('货币型-普通货币')
            and code >= ?
            and name like ?
            order by code
        '''
        funds = db.run(get_code_sql, (begin_code, name_like)).get_rows()
    
    tp = ThreadPool(thread_num)
    for fund in funds:
        if len(vals_all) >= 1000000:
            tp.wait()
            num = db.run(sql, vals_all)
            log.info('fix_fund_dv', num)
            vals_all.clear()
        else:
            code = fund[0]
            tp.run_wait(fix_fund_dv_one, (code, rep))
            
    tp.wait()
    num = db.run(sql, vals_all)
    log.info('fix_fund_dv', num)
    vals_all.clear()


def fix_dwjz(db):

    def get_dwjz_one(db, code):
        sql = 'update t_e set dwjz = ? where code = ? and date = ?'
        params = []
        rss = db.run('select date,fh from t_e where code = ? and dwjz is null order by date', (code,)).get_rows()
        for rs in rss:
            date_ = rs[0]
            fh = rs[1]
                
            try:
                previous_dwjz = float(db.run('select dwjz from t_e where code = ? and date < ? and dwjz is not null order by date desc limit 1', (code, date_)).get_rows()[0][0])
                if previous_dwjz is None:
                    previous_dwjz = 1
            except:
                previous_dwjz = 1 
        
            if '每份基金份额分拆' in str(fh):
                fh_cf = float(fh.replace('每份基金份额分拆', '').replace('份', ''))
                dwjz = previous_dwjz / fh_cf
            elif '每份派现金' in str(fh):
                fh_xj = float(fh.replace('每份派现金', '').replace('元', ''))
                dwjz = previous_dwjz - fh_xj
            else:
                dwjz = previous_dwjz
                
            params.append((dwjz, code, date_))
            
        num = db.run(sql, params)
        log.info('get_dwjz', code, num, len(params))

    tp = ThreadPool(64)
    log.info('get_dwjz', 'begin')
    funds = db.run("select code from t_m order by code").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ?', (fund[0],)).get_rows()[0][0]
        if num > 0:
            tp.run(get_dwjz_one, (db, fund[0]))
    tp.wait()


def get_zf(db):

    def get_zf_one(db, code):
        sql = 'update t_e set zf = ? where code = ? and date = ?'
        params = []
        rss = db.run('select date,dwjz,fh from t_e where code = ? and zf is null order by date', (code,)).get_rows()
        for rs in rss:
            date_ = rs[0]
            dwjz = float(rs[1])
            fh = rs[2]
            try:
                previous_dwjz = float(db.run('select dwjz from t_e where code = ? and date < ? order by date desc limit 1', (code, date_)).get_rows()[0][0])
            except:
                zf = 0
                params.append((zf, code, date_))
                continue
            
            if '每份基金份额分拆' in str(fh):
                fh_cf = float(fh.replace('每份基金份额分拆', '').replace('份', ''))
                zf = ((dwjz * fh_cf) - previous_dwjz) / previous_dwjz * 100
            elif '每份派现金' in str(fh):
                fh_xj = float(fh.replace('每份派现金', '').replace('元', ''))
                zf = ((dwjz + fh_xj) - previous_dwjz) / previous_dwjz * 100
            elif '每份基金份额折算' in str(fh):
                fh_zs = float(fh.replace('每份基金份额折算', '').replace('份', ''))
                zf = (dwjz - (previous_dwjz / fh_zs)) / (previous_dwjz / fh_zs) * 100
            else:
                zf = (dwjz - previous_dwjz) / previous_dwjz * 100
            
            params.append((zf, code, date_))
        try:
            num = db.run(sql, params)
            log.info('get_zf', code, num, len(params))
        except Exception as _:
            log.error('get_zf', code, str(_))

    tp = ThreadPool(64)
    log.info('get_zf', 'begin')
    funds = db.run("select code from t_m").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ? and dwjz is null', (fund[0],)).get_rows()[0][0]
        if num == 0:
            tp.run(get_zf_one, (db, fund[0]))
    tp.wait()

    
def get_val(db):

    def get_val_one(db, code):
        sql = 'update t_e set val = ? where code = ? and date = ?'
        params = []   
        rss = db.run('select date,zf from t_e where code = ? and val is null order by date', (code,)).get_rows()
        next_val = 1 
        for rs in rss:
            try:
                date_ = rs[0]
                zf = rs[1]
                try:
                    next_val_db = None
                    next_val_db = db.run('select val from t_e where code = ? and date < ? order by date desc limit 1', (code, date_)).get_rows()[0][0]
                except:
                    next_val_db = None
                if next_val_db is not None:
                    next_val = next_val_db
                val = float(next_val) * (1 + float(zf) / 100)
                params.append((val, code, date_))
                next_val = val
            except Exception as _:
                print(_, code, date_, next_val, zf)
        try:
            num = db.run(sql, params)
            log.info('get_val', code, num, len(params))
        except Exception as _:
            log.error('get_val', code, str(_))

    tp = ThreadPool(64)
    log.info('get_val', 'begin')
    funds = db.run("select code from t_m").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ? and zf is null', (fund[0],)).get_rows()[0][0]
        if num == 0:
            tp.run(get_val_one, (db, fund[0]))
    tp.wait()


def get_hc(db):

    def get_hc_one(db, code):
        params = []      
        sql = 'update t_e set hc = ? where code = ? and date = ?'
        rows = db.run('select date,val from t_e where hc is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            val = row[1]
            max_val = db.run('select max(val) from t_e where date <= ? and code = ?', (date_now, code)).get_rows()[0][0]
            val = float(val)
            max_val = float(max_val)
            hc = round((max_val - val) / max_val * 100, 3)
            params.append((hc, code, date_now))
        try:
            num = db.run(sql, params)
            log.info('get_hc', code, num, len(params))
        except Exception as _:
            log.error('get_hc', code, str(_))
    
    tp = ThreadPool(64)
    log.info('get_hc', 'begin')
    funds = db.run("select code from t_m").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ? and val is null', (fund[0],)).get_rows()[0][0]
        if num == 0:
            tp.run(get_hc_one, (db, fund[0]))
    tp.wait()


def get_nh(db):

    def get_nh1n_one(db, code):
        nh1n_params = []
        nh1n_sql = 'update t_e set nh1n = ? where code = ? and date = ?'
        rows = db.run('select date,val from t_e where nh1n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=1)).strftime('%Y-%m-%d')
            val = row[1]
            val = float(val)
            try:
                val_future = db.run('select val from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                val_future = float(val_future)
                nh1n = round((val_future - val) / val * 100, 3)
            except:
                nh1n = None
            if nh1n is None:
                break
            nh1n_params.append((nh1n, code, date_now))
        try:
            num = db.run(nh1n_sql, nh1n_params)
            log.info('get_nh1n_one', code, num, len(nh1n_params))
        except Exception as _:
            log.error('get_nh1n_one', code, str(_))
        
    def get_nh3n_one(db, code):
        nh3n_params = []
        nh3n_sql = 'update t_e set nh3n = ? where code = ? and date = ?'
        rows = db.run('select date,val from t_e where nh3n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=3)).strftime('%Y-%m-%d')
            val = row[1]
            val = float(val)
            try:
                val_future = db.run('select val from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                val_future = float(val_future)
                nh3n = round((val_future - val) / val / 3 * 100, 3)
            except:
                nh3n = None
            if nh3n is None:
                break
            nh3n_params.append((nh3n, code, date_now))
        try:
            num = db.run(nh3n_sql, nh3n_params)
            log.info('get_nh3n_one', code, num, len(nh3n_params))
        except Exception as _:
            log.error('get_nh3n_one', code, str(_))
        
    def get_nh5n_one(db, code):
        nh5n_params = []
        nh5n_sql = 'update t_e set nh5n = ? where code = ? and date = ?'
        rows = db.run('select date,val from t_e where nh5n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=5)).strftime('%Y-%m-%d')
            val = row[1]
            val = float(val)
            try:
                val_future = db.run('select val from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                val_future = float(val_future)
                nh5n = round((val_future - val) / val / 5 * 100, 3)
            except:
                nh5n = None
            if nh5n is None:
                break
            nh5n_params.append((nh5n, code, date_now))
        try:
            num = db.run(nh5n_sql, nh5n_params)
            log.info('get_nh5n_one', code, num, len(nh5n_params))
        except Exception as _:
            log.error('get_nh5n_one', code, str(_))
    
    tp = ThreadPool(64)
    log.info('get_nh', 'begin')
    funds = db.run("select code from t_m").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ? and val is null', (fund[0],)).get_rows()[0][0]
        if num == 0:
            tp.run(get_nh1n_one, (db, fund[0]))
            tp.run(get_nh3n_one, (db, fund[0]))
            tp.run(get_nh5n_one, (db, fund[0]))
    tp.wait()
    

def get_xp(db):

    def get_xp1n_one(db, code):
        xp1n_params = []
        xp1n_sql = 'update t_e set xp1n = ? where code = ? and date = ?'
        rows = db.run('select date from t_e where xp1n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=1)).strftime('%Y-%m-%d')
            try:
                zfs_future_num = db.run('select count(1) from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                if zfs_future_num == 0:
                    break
                zfs_future = db.run('select zf from t_e where date >= ? and date < ? and code = ? order by date', (date_now, date_future, code)).get_rows()
                zfs_future = [c[0] / 100 for c in zfs_future]
                year_rate = sum(zfs_future)
                day_standard_deviation = np.std(zfs_future) * math.sqrt(365)
                if day_standard_deviation == 0:
                    xp1n = None
                else:
                    xp1n = round(year_rate / day_standard_deviation, 3)
            except Exception as _:
                xp1n = None
            xp1n_params.append((xp1n, code, date_now))
        try:
            num = db.run(xp1n_sql, xp1n_params)
            log.info('get_xp1n_one', code, num, len(xp1n_params))
        except Exception as _:
            log.error('get_xp1n_one', code, str(_))
        
    def get_xp3n_one(db, code):
        xp3n_params = []
        xp3n_sql = 'update t_e set xp3n = ? where code = ? and date = ?'
        rows = db.run('select date from t_e where xp3n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=3)).strftime('%Y-%m-%d')
            try:
                zfs_future_num = db.run('select count(1) from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                if zfs_future_num == 0:
                    break
                zfs_future = db.run('select zf from t_e where date >= ? and date < ? and code = ? order by date', (date_now, date_future, code)).get_rows()
                zfs_future = [c[0] / 100 for c in zfs_future]
                year_rate = sum(zfs_future)
                day_standard_deviation = np.std(zfs_future) * math.sqrt(365 * 3)
                if day_standard_deviation == 0:
                    xp3n = None
                else:
                    xp3n = round(year_rate / day_standard_deviation, 3)
            except Exception as _:
                xp3n = None
            xp3n_params.append((xp3n, code, date_now))
        try:
            num = db.run(xp3n_sql, xp3n_params)
            log.info('get_xp3n_one', code, num, len(xp3n_params))
        except Exception as _:
            log.error('get_xp3n_one', code, str(_))
        
    def get_xp5n_one(db, code):
        xp5n_params = []
        xp5n_sql = 'update t_e set xp5n = ? where code = ? and date = ?'
        rows = db.run('select date from t_e where xp5n is null and code = ?', (code,)).get_rows()
        for row in rows:
            date_now = row[0]
            date_future = (datetime.datetime.strptime(date_now, '%Y-%m-%d') + relativedelta(years=5)).strftime('%Y-%m-%d')
            try:
                zfs_future_num = db.run('select count(1) from t_e where date >= ? and code = ? order by date limit 1', (date_future, code)).get_rows()[0][0]
                if zfs_future_num == 0:
                    break
                zfs_future = db.run('select zf from t_e where date >= ? and date < ? and code = ? order by date', (date_now, date_future, code)).get_rows()
                zfs_future = [c[0] / 100 for c in zfs_future]
                year_rate = sum(zfs_future)
                day_standard_deviation = np.std(zfs_future) * math.sqrt(365 * 5)
                if day_standard_deviation == 0:
                    xp5n = None
                else:
                    xp5n = round(year_rate / day_standard_deviation, 3)
            except Exception as _:
                xp5n = None
            xp5n_params.append((xp5n, code, date_now))
        try:
            num = db.run(xp5n_sql, xp5n_params)
            log.info('get_xp5n_one', code, num, len(xp5n_params))
        except Exception as _:
            log.error('get_xp5n_one', code, str(_))
    
    tp = ThreadPool(64)
    log.info('get_xp', 'begin')
    funds = db.run("select code from t_m").get_rows()
    for fund in funds:
        num = db.run('select count(1) from t_e where code = ? and zf is null', (fund[0],)).get_rows()[0][0]
        if num == 0:
            tp.run(get_xp1n_one, (db, fund[0]))
            tp.run(get_xp3n_one, (db, fund[0]))
            tp.run(get_xp5n_one, (db, fund[0]))
    tp.wait()


if __name__ == '__main__':
    main()

