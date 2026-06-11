<template>
  <v-chart :option="chartOption" autoresize style="height: 480px; width: 100%" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

interface CurvePoint {
  week: number
  speed: number
  strength: number
  endurance: number
  agility: number
  flexibility: number
  total: number
}

const props = defineProps<{
  curveData: CurvePoint[]
}>()

const chartOption = computed(() => {
  const weeks = props.curveData.map((d) => d.week)
  const series = [
    { name: '速度', key: 'speed', color: '#409eff' },
    { name: '力量', key: 'strength', color: '#f56c6c' },
    { name: '耐力', key: 'endurance', color: '#e6a23c' },
    { name: '敏捷', key: 'agility', color: '#67c23a' },
    { name: '柔韧', key: 'flexibility', color: '#909399' },
    { name: '综合', key: 'total', color: '#9b59b6' }
  ]

  return {
    title: {
      text: '学员成长曲线',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: series.map((s) => s.name),
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: weeks,
      name: '训练周次',
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '标准化得分',
      min: 0,
      max: 100
    },
    series: series.map((s) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: props.curveData.map((d) => (d as any)[s.key]),
      itemStyle: { color: s.color },
      lineStyle: { width: 2 },
      symbolSize: 6
    }))
  }
})
</script>
