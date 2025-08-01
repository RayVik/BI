import datetime
import pandas as pd


def scoring_segment(reserach_period=90, currdate=pd.to_datetime(datetime.datetime.now()).date().strftime('%Y-%m-%d'),
                    seed=42):
    # table_name = 'BIG_DATA_LTV_ONLINE_OFFLINE_NEW'
    table_name = 'BIG_DATA_LTV_ONLINE_OFFLINE_NEW2025'
    currdate = pd.to_datetime(currdate).date()
    currdate = currdate - datetime.timedelta(days=1)
    query_base = f'''
with cte as (
select 
	CUSTOMER_ID 
	, CASSTICKID 
	, FIRSTORDERDATE 
	, min(CREATED_AT_ORD) as min_data_purches
	, max(CREATED_AT_ORD) as max_data_purches
	, min(TRADE_DT)
	, date_diff('day', FIRSTORDERDATE, toDate('{currdate}')) as b
from 
	{table_name}
where
	FIRSTORDERDATE <= TRADE_DT
	and toDate(TRADE_DT) <= toDate('{currdate}')
	and toDate(FIRSTORDERDATE) <= toDate('{currdate}')
	and date_diff('day', toDate(FIRSTORDERDATE) , toDate('{currdate}')) < {reserach_period} 
	and CUSTOMER_ID not in (
		select 
			CUSTOMER_ID 
		from (
			select 
				CUSTOMER_ID
				, FIRSTORDERDATE
				, min(TRADE_DT) as min_trade_dt
			from 
				{table_name}
			group by 
				CUSTOMER_ID, FIRSTORDERDATE
			  )
		where 
			FIRSTORDERDATE < min_trade_dt
	 )
group by
	CUSTOMER_ID
	, CASSTICKID 
	, FIRSTORDERDATE
),
cte_two as (
select 
	*
from 
	{table_name}
where
	CUSTOMER_ID IN (select CUSTOMER_ID from cte)
),
cte_five as (
select 
	*,
	 if(IDENTIFICATION == 'ONLINE', 1, 0) as IDENTIFICATION_INDEX,
	anyLast(FIRSTORDERDATE) over (partition by CUSTOMER_ID order by TRADE_DT) as anyLastNull

from cte_two
where CUSTOMER_ID not in (SELECT CUSTOMER_ID FROM cte_two where PRODUCT_CODE is null)
order by TRADE_DT
),

cte_region_name as (
select CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, REGION_NAME_EN
	, USER_TYPE
	, COUNT(*) as region_count
from 
	cte_five
group by
CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, REGION_NAME_EN
	, USER_TYPE
),

cte_region_name_count_main as (
select *,
ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID
	, TRADE_DT
	order by region_count DESC, cityHash64(toString(REGION_NAME_EN), {seed})) as rn_region
from cte_region_name
),

cte_identification_count as (
select CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, IDENTIFICATION_INDEX
	, USER_TYPE
	, COUNT(*) as identification_count
from 
	cte_five
group by
CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, IDENTIFICATION_INDEX
	, USER_TYPE
),

cte_identification_count_main as (
select *,
ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID
	, TRADE_DT
	order by identification_count DESC, cityHash64(toString(IDENTIFICATION_INDEX), {seed})) as rn_identification
from cte_identification_count
),

cte_casstickid_count as (
select CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, CASSTICKID
	, USER_TYPE
	, COUNT(*) as casstickid_count
from 
	cte_five
group by
CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, CASSTICKID
	, USER_TYPE
),

cte_casstickid_count_main as (
select *,
ROW_NUMBER() OVER (PARTITION BY CUSTOMER_ID
	, TRADE_DT
	order by casstickid_count DESC, cityHash64(toString(CASSTICKID), {seed})) as rn_casstickid
from cte_casstickid_count
),

cte_six as (
select 
	CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, USER_TYPE
	, round(min(PRICE),3) as PRICEmin
	, round(max(PRICE),3) as PRICEmax
	, round(avg(PRICE),3) as PRICEmean
	, round(sum(PRICE),3) as PRICEsum
	, count(distinct CASSTICKID) as COUNT_TICK	
	, count(distinct PRODUCT_CODE) as PRODUCT_CODEnunique
	, count(PRODUCT_CODE) as PRODUCT_CODEcount

from 
	cte_five
where 
	CUSTOMER_ID not in (select CUSTOMER_ID from cte_five where FIRSTORDERDATE is null)
group by
	CUSTOMER_ID
	, FIRSTORDERDATE
	, TRADE_DT
	, USER_TYPE
),

cte_features as (
    select 
        *,
        coalesce(round((PRICEsum - lagInFrame(PRICEsum) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ASC)) / 
           lagInFrame(PRICEsum) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ASC) * 100, 3), 0) AS PRICEpct_change,
           
        round(sum(PRICEsum) over (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEcumsum,
        count(distinct TRADE_DT) over (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW) as sequence_number, 
        dateDiff('day', FIRSTORDERDATE, TRADE_DT) + 1 as order_diff_cum,
        
        CASE
            WHEN avg(PRICEsum) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW) = 0 THEN 0
            ELSE stddevPop(PRICEsum) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW) / 
                 avg(PRICEsum) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW)
        END as order_sum_var_coef,
        
        ifNull(sumIf(PRICEsum, 
            TRADE_DT >= subtractDays(addDays(FIRSTORDERDATE, 89), 10) AND 
            TRADE_DT <= addDays(FIRSTORDERDATE, 89) AND
            TRADE_DT <= TRADE_DT
        ) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0) as last10_periodend,
        
        
        ifNull(sumIf(PRICEsum, 
            TRADE_DT >= subtractDays(addDays(FIRSTORDERDATE, 89), 40) AND 
            TRADE_DT <= addDays(FIRSTORDERDATE, 89) AND
            TRADE_DT <= TRADE_DT
        ) OVER (PARTITION BY CUSTOMER_ID ORDER BY TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0) as last40_periodend
        
        
    from cte_six 
    where  PRICEsum > 10
    ORDER BY TRADE_DT ASC
)

select 
    cm.CUSTOMER_ID as CUSTOMER_ID,
    cm.FIRSTORDERDATE as FIRSTORDERDATE,
    dateDiff('day', cm.FIRSTORDERDATE, toDate('{currdate}')) + 1 as LIFETIME_DAY,
    cm.TRADE_DT as TRADE_DT,
    cm.USER_TYPE as USER_TYPE,
    cm.PRICEmax as PRICEmax,
    cm.PRICEmean as PRICEmean,
    cm.PRICEmin as PRICEmin,
    cm.PRICEsum as PRICEsum,
    cm.PRODUCT_CODEcount as PRODUCT_CODEcount,
    cm.PRODUCT_CODEnunique as PRODUCT_CODEnunique, 
    cm.PRICEpct_change as PRICEpct_change,
    cm.PRICEcumsum as PRICEcumsum,
    cm.COUNT_TICK as COUNT_TICK,
    cm.sequence_number as sequence_number,
    cm.order_diff_cum as order_diff_cum,
    cm.order_sum_var_coef as order_sum_var_coef,
    cm.last10_periodend as last10_periodend,
    cm.last40_periodend as last40_periodend,


    round(sum(cm.PRICEmax) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEmax_cumsum,
    round(sum(cm.PRODUCT_CODEcount) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRODUCT_CODEcount_cumsum,
    round(max(cm.PRICEsum) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEsum_max,
    round(avg(cm.PRICEsum) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEexpanding_sum_mean,
    round(avg(cm.PRICEmean) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEexpanding_mean_mean,
    round(avg(cm.PRICEmax) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEexpanding_max_mean,
    round(avg(cm.PRICEpct_change) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PRICEpct_change_expanding_mean,
    round(avg(cm.PRODUCT_CODEnunique) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as PCnunique_expanding_mean,
    round(avg(identification_count.IDENTIFICATION_INDEX) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT ROWS BETWEEN UNBOUNDED PRECEDING and CURRENT ROW), 3) as ONLINE_SHARE,
    
    round(cm.sequence_number / cm.order_diff_cum, 3) as order_density,
    round(cm.PRICEmax - cm.PRICEmin, 3) as PRICE_RANGE,
    (cm.PRICEsum / cm.PRICEcumsum) * 100 as PERCENT_OF_TOTAL_PRICE,
    coalesce(round((cm.PRICEsum - first_value(cm.PRICEsum) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT)) / 
         first_value(cm.PRICEsum) over (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT) * 100, 3), 0) as pct_change_base,
    
    CASE 
        WHEN lagInFrame(region_count.REGION_NAME_EN, 1) OVER (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT) IS NULL THEN 0
        WHEN region_count.REGION_NAME_EN = lagInFrame(region_count.REGION_NAME_EN, 1) OVER (PARTITION BY cm.CUSTOMER_ID ORDER BY cm.TRADE_DT) THEN 0
        ELSE 1
    END as region_changing,

    region_count.REGION_NAME_EN,
    identification_count.IDENTIFICATION_INDEX,
    casstickid_count.CASSTICKID
    
from 
    cte_features cm
LEFT JOIN cte_region_name_count_main region_count 
    ON region_count.CUSTOMER_ID = cm.CUSTOMER_ID 
    AND region_count.TRADE_DT = cm.TRADE_DT 
    AND region_count.rn_region = 1
LEFT JOIN cte_identification_count_main identification_count 
    ON identification_count.CUSTOMER_ID = cm.CUSTOMER_ID 
    AND identification_count.TRADE_DT = cm.TRADE_DT
    AND identification_count.rn_identification = 1
LEFT JOIN cte_casstickid_count_main casstickid_count 
    ON casstickid_count.CUSTOMER_ID = cm.CUSTOMER_ID 
    AND casstickid_count.TRADE_DT = cm.TRADE_DT
    AND casstickid_count.rn_casstickid = 1

where  
    cm.PRICEsum > 10
ORDER BY cm.TRADE_DT ASC
    '''

    return query_base
