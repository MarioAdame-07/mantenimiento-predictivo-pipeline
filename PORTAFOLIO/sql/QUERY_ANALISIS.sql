SELECT TOP 10
	device_id,
	fecha_alta,
	dias_totales_operacion
FROM dim_device
where fallo_historico = 0
order by dias_totales_operacion desc;

select
	f1.device_id,
	f1.date as fecha_anomalia,
	f2.date as fecha_fallo,
	f1.metric1,
    f1.metric2,
    f1.metric3,
    f1.metric4
from fact_device_metrics f1
inner join fact_device_metrics f2
	on f1.device_id = f2.device_id
	and f1.date = DATEADD(day, -1, f2.date)
where f2.failure = 1;

SELECT 
    date,
    device_id,
    metric2 AS valor_diario,
    -- Calculamos el promedio del día actual y los 2 días anteriores
    AVG(metric2) OVER(
        PARTITION BY device_id 
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS promedio_movil_3_dias
FROM fact_device_metrics
WHERE device_id = 'S1F0RRB1'
ORDER BY date;