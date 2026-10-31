import {useEffect,useRef} from 'react';
import * as echarts from 'echarts/core';
import {BarChart,ScatterChart,HeatmapChart,LineChart,TreemapChart} from 'echarts/charts';
import {GridComponent,TooltipComponent,LegendComponent,VisualMapComponent,AriaComponent} from 'echarts/components';
import {CanvasRenderer,SVGRenderer} from 'echarts/renderers';
import type {EChartsOption} from 'echarts';
import {Download} from 'lucide-react';
echarts.use([BarChart,ScatterChart,HeatmapChart,LineChart,TreemapChart,GridComponent,TooltipComponent,LegendComponent,VisualMapComponent,AriaComponent,CanvasRenderer,SVGRenderer]);
export function Chart({option,label,dark,height=340}:{option:EChartsOption;label:string;dark:boolean;height?:number}) {
 const ref=useRef<HTMLDivElement>(null); const chart=useRef<echarts.ECharts|null>(null);
 useEffect(()=>{if(!ref.current)return;const instance=echarts.init(ref.current,dark?'dark':undefined,{renderer:'canvas'});chart.current=instance;const observer=new ResizeObserver(()=>instance.resize());observer.observe(ref.current);return()=>{observer.disconnect();instance.dispose();};},[dark]);
 useEffect(()=>{chart.current?.setOption({backgroundColor:dark?'#142237':'#fff',textStyle:{color:dark?'#cbd5e1':'#475569',fontFamily:'system-ui'},animation:!matchMedia('(prefers-reduced-motion: reduce)').matches,aria:{enabled:true},...option},true);},[option,dark]);
 return <div className="chart-wrap"><div ref={ref} style={{height}} role="img" aria-label={label}/><div className="chart-downloads"><button className="chart-export" onClick={()=>{const link=document.createElement('a');link.download='enarm-chart.png';link.href=chart.current!.getDataURL({pixelRatio:2,backgroundColor:dark?'#142237':'#fff'});link.click();}}><Download size={14}/> PNG</button><button className="chart-export" onClick={()=>{if(!chart.current)return;const container=document.createElement('div');const exported=echarts.init(container,dark?'dark':undefined,{renderer:'svg',width:chart.current.getWidth(),height:chart.current.getHeight()});exported.setOption({...chart.current.getOption(),animation:false});const link=document.createElement('a');link.download='enarm-chart.svg';link.href=exported.getDataURL({type:'svg'});link.click();exported.dispose();}}><Download size={14}/> SVG</button></div></div>;
}
